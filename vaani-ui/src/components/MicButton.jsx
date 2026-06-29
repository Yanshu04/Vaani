import React, { useRef, useState, useEffect } from 'react'
import { transcribeAudio } from '../api/client'

export default function MicButton({
  config,
  recording,
  setRecording,
  disabled,
  onTranscription
}) {
  const [isHovered, setIsHovered] = useState(false)
  const mediaRecorder = useRef(null)
  const chunks = useRef([])
  const streamRef = useRef(null)
  const timeoutRef = useRef(null)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const animationFrameRef = useRef(null)

  const idleStyle = {
    width: '44px',
    height: '44px',
    borderRadius: '50%',
    background: isHovered ? 'var(--accent-glow)' : 'var(--surface-2)',
    border: '1px solid var(--accent)',
    color: 'var(--accent)',
    fontSize: '18px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    animation: 'breathe 2.5s ease-in-out infinite',
    transition: 'background 0.2s',
    outline: 'none'
  }

  const recordingStyle = {
    width: '44px',
    height: '44px',
    borderRadius: '50%',
    background: 'var(--accent)',
    border: '1px solid var(--accent)',
    color: '#fff',
    fontSize: '18px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    animation: 'none',
    outline: 'none'
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      mediaRecorder.current = new MediaRecorder(stream)
      chunks.current = []
      
      mediaRecorder.current.ondataavailable = e => {
        if (e.data && e.data.size > 0) {
          chunks.current.push(e.data)
        }
      }

      mediaRecorder.current.onstop = async () => {
        setRecording(false)
        
        // Clean up audio tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(t => t.stop())
          streamRef.current = null
        }

        // Clean up AudioContext & Analyser
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
        if (audioContextRef.current) {
          audioContextRef.current.close()
          audioContextRef.current = null
        }

        if (chunks.current.length > 0) {
          const blob = new Blob(chunks.current, { type: 'audio/wav' })
          try {
            const result = await transcribeAudio(blob, config.whisperModel)
            onTranscription(result)
          } catch (err) {
            console.error('Transcription failed:', err)
          }
        }
      }

      mediaRecorder.current.start()
      setRecording(true)

      // 10s absolute timeout
      timeoutRef.current = setTimeout(() => {
        stopRecording()
      }, 10000)

      // If Auto mode, run silence detection using Web Audio API
      if (!config.pttMode) {
        setupSilenceDetection(stream)
      }

    } catch (err) {
      console.error('Failed to start recording:', err)
    }
  }

  function setupSilenceDetection(stream) {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 512
      source.connect(analyser)

      audioContextRef.current = audioContext
      analyserRef.current = analyser

      const bufferLength = analyser.fftSize
      const dataArray = new Uint8Array(bufferLength)

      let lastSpeechTime = Date.now()
      const silenceThreshold = 10 // Threshold for silence
      const silenceDuration = 1500 // 1.5 seconds of silence to stop

      function checkSilence() {
        if (!mediaRecorder.current || mediaRecorder.current.state === 'inactive') return

        analyser.getByteTimeDomainData(dataArray)

        // Calculate RMS energy
        let sum = 0
        for (let i = 0; i < bufferLength; i++) {
          const val = (dataArray[i] - 128) / 128
          sum += val * val
        }
        const rms = Math.sqrt(sum / bufferLength) * 100

        if (rms > silenceThreshold) {
          lastSpeechTime = Date.now()
        } else {
          if (Date.now() - lastSpeechTime > silenceDuration) {
            stopRecording()
            return
          }
        }

        animationFrameRef.current = requestAnimationFrame(checkSilence)
      }

      // Delay checking silence by 500ms to allow user to start speaking
      setTimeout(() => {
        checkSilence()
      }, 500)

    } catch (e) {
      console.error('Error setting up Web Audio silence detection:', e)
    }
  }

  function stopRecording() {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop()
    }
    setRecording(false)
  }

  // Auto Mode Click Handler
  const handleClick = () => {
    if (config.pttMode) return
    if (recording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  // PTT Mode Handlers
  const handleMouseDown = () => {
    if (!config.pttMode) return
    startRecording()
  }

  const handleMouseUp = () => {
    if (!config.pttMode) return
    stopRecording()
  }

  const handleMouseEnter = () => {
    setIsHovered(true)
  }

  const handleMouseLeave = () => {
    setIsHovered(false)
  }

  return (
    <div style={{ position: 'relative', display: 'inline-flex' }}>
      {recording && (
        <>
          <span style={{
            position: 'absolute', inset: 0,
            borderRadius: '50%',
            background: 'var(--accent)',
            animation: 'ripple 1.5s ease-out infinite',
            zIndex: 0
          }}/>
          <span style={{
            position: 'absolute', inset: 0,
            borderRadius: '50%',
            background: 'var(--accent)',
            animation: 'ripple 1.5s ease-out infinite',
            animationDelay: '0.5s',
            zIndex: 0
          }}/>
        </>
      )}
      <button
        type="button"
        style={recording ? recordingStyle : idleStyle}
        onClick={handleClick}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onTouchStart={handleMouseDown}
        onTouchEnd={handleMouseUp}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        disabled={disabled}
        title={config.pttMode ? "Hold to speak" : "Click to speak"}
      >
        🎙
      </button>
    </div>
  )
}
