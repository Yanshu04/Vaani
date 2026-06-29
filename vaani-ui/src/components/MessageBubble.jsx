import React, { useState, useEffect, useRef } from 'react'

function AudioPlayer({ src }) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const onTimeUpdate = () => setCurrentTime(audio.currentTime)
    const onLoadedMetadata = () => setDuration(audio.duration)
    const onEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', onTimeUpdate)
    audio.addEventListener('loadedmetadata', onLoadedMetadata)
    audio.addEventListener('ended', onEnded)

    // Reset player state if source changes
    setIsPlaying(false)
    setCurrentTime(0)

    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate)
      audio.removeEventListener('loadedmetadata', onLoadedMetadata)
      audio.removeEventListener('ended', onEnded)
    }
  }, [src])

  const togglePlay = () => {
    if (isPlaying) {
      audioRef.current.pause()
      setIsPlaying(false)
    } else {
      audioRef.current.play()
      setIsPlaying(true)
    }
  }

  const handleSeek = (e) => {
    const val = parseFloat(e.target.value)
    audioRef.current.currentTime = val
    setCurrentTime(val)
  }

  const formatTime = (secs) => {
    if (isNaN(secs)) return '0:00'
    const m = Math.floor(secs / 60)
    const s = Math.floor(secs % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      marginTop: '12px',
      padding: '8px 12px',
      background: 'var(--surface-2)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)',
      width: '100%',
      maxWidth: '300px',
      userSelect: 'none'
    }}>
      <audio ref={audioRef} src={src} />
      <button 
        onClick={togglePlay}
        style={{
          background: isPlaying ? 'var(--accent)' : 'var(--border-strong)',
          border: 'none',
          borderRadius: '50%',
          width: '32px',
          height: '32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          color: 'var(--text)',
          transition: 'all 0.2s ease',
          boxShadow: isPlaying ? '0 0 10px var(--accent-glow)' : 'none'
        }}
      >
        {isPlaying ? (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <rect x="4" y="4" width="4" height="16" rx="1" />
            <rect x="16" y="4" width="4" height="16" rx="1" />
          </svg>
        ) : (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style={{ marginLeft: '2px' }}>
            <polygon points="5,3 19,12 5,21" />
          </svg>
        )}
      </button>
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <input 
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          style={{
            width: '100%',
            accentColor: 'var(--accent)',
            cursor: 'pointer',
            height: '4px',
            background: 'var(--border)',
            borderRadius: '2px',
            outline: 'none'
          }}
        />
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '9px',
          color: 'var(--text-secondary)',
          fontFamily: 'var(--font-mono)'
        }}>
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>
    </div>
  )
}


export default function MessageBubble({ message, streaming }) {
  const { role, content, original_text, detected_language, confidence, noise_level, audioUrl } = message
  const isUser = role === 'user'

  const userStyle = {
    alignSelf: 'flex-end',
    maxWidth: '65%',
    background: 'var(--surface-2)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg) var(--radius-lg) 4px var(--radius-lg)',
    padding: '12px 16px',
    fontFamily: 'var(--font-sans)',
    fontSize: '14px',
    lineHeight: 1.6,
    color: 'var(--text)'
  }

  const assistantStyle = {
    alignSelf: 'flex-start',
    maxWidth: '75%',
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderLeft: '2px solid var(--accent)',
    borderRadius: '4px var(--radius-lg) var(--radius-lg) var(--radius-lg)',
    padding: '16px 18px',
    fontFamily: 'var(--font-sans)',
    fontSize: '14px',
    lineHeight: 1.7,
    color: 'var(--text)'
  }

  const metadataRowStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginTop: '8px',
    flexWrap: 'wrap',
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--muted)'
  }

  const badgeStyles = {
    hi: {
      background: 'rgba(245,158,11,0.15)',
      color: 'var(--badge-hi)',
      border: '1px solid rgba(245,158,11,0.3)'
    },
    en: {
      background: 'rgba(99,102,241,0.15)',
      color: 'var(--badge-en)',
      border: '1px solid rgba(99,102,241,0.3)'
    },
    gu: {
      background: 'rgba(139,92,246,0.15)',
      color: 'var(--badge-gu)',
      border: '1px solid rgba(139,92,246,0.3)'
    }
  }

  const badgeStyle = (lang) => ({
    ...(badgeStyles[lang] || {
      background: 'var(--surface-3)',
      color: 'var(--text-secondary)',
      border: '1px solid var(--border)'
    }),
    fontFamily: 'var(--font-mono)',
    fontSize: '10px',
    padding: '2px 8px',
    borderRadius: '20px',
    letterSpacing: '1px',
    textTransform: 'uppercase'
  })

  const textStyle = {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--muted)'
  }

  return (
    <div className="message" style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
      {isUser ? (
        <div style={userStyle}>
          <div>{original_text || content}</div>
          {(detected_language || confidence || noise_level || (original_text && original_text !== content)) && (
            <div style={metadataRowStyle}>
              {detected_language && (
                <span style={badgeStyle(detected_language)}>{detected_language}</span>
              )}
              {confidence !== undefined && confidence !== null && (
                <span style={textStyle}>
                  Conf: {typeof confidence === 'number' ? Math.round(confidence * 100) + '%' : confidence}
                </span>
              )}
              {noise_level && (
                <span style={textStyle}>Noise: {noise_level}</span>
              )}
              {original_text && original_text !== content && (
                <span style={textStyle}>Translation: "{content}"</span>
              )}
            </div>
          )}
        </div>
      ) : (
        <div style={assistantStyle}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <span>
              {content}
              {streaming && <span className="cursor">|</span>}
            </span>
            {audioUrl && <AudioPlayer src={audioUrl} />}
          </div>
        </div>
      )}
    </div>
  )
}
