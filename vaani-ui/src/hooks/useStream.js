import { useState } from 'react'
import { streamChat } from '../api/client'

export function useStream() {
  const [streaming, setStreaming] = useState(false)

  async function sendMessage(payload, onToken, onDone, onError) {
    setStreaming(true)
    await streamChat(payload, onToken, (full) => {
      setStreaming(false)
      onDone(full)
    }, (e) => {
      setStreaming(false)
      onError(e)
    })
  }

  return { streaming, sendMessage }
}
