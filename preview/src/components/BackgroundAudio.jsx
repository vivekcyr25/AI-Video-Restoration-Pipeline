import { useEffect, useRef, useState } from 'react'

const VOLUME = 0.3
const MUSIC_SRC = `${import.meta.env.BASE_URL}background-music.mp3`

export default function BackgroundAudio() {
  const audioRef = useRef(null)
  const startedRef = useRef(false)
  const [playing, setPlaying] = useState(false)
  const [muted, setMuted] = useState(false)

  const startPlayback = async () => {
    const audio = audioRef.current
    if (!audio || startedRef.current) return

    try {
      audio.volume = VOLUME
      await audio.play()
      startedRef.current = true
      setPlaying(true)
    } catch {
      // Autoplay blocked — will retry on user interaction
    }
  }

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    audio.volume = VOLUME
    audio.loop = true
    startPlayback()

    const resume = () => startPlayback()

    window.addEventListener('scroll', resume, { passive: true, once: true })
    window.addEventListener('click', resume, { once: true })
    window.addEventListener('keydown', resume, { once: true })
    window.addEventListener('touchstart', resume, { once: true })

    return () => {
      window.removeEventListener('scroll', resume)
      window.removeEventListener('click', resume)
      window.removeEventListener('keydown', resume)
      window.removeEventListener('touchstart', resume)
    }
  }, [])

  const toggleMute = () => {
    const audio = audioRef.current
    if (!audio) return

    if (!startedRef.current) {
      startPlayback()
      return
    }

    const next = !muted
    audio.muted = next
    setMuted(next)
  }

  return (
    <>
      <audio ref={audioRef} src={MUSIC_SRC} preload="auto" loop playsInline />
      <button
        type="button"
        onClick={toggleMute}
        className="fixed bottom-5 right-5 z-50 w-9 h-9 rounded-full glass border border-white/10 flex items-center justify-center text-white/50 hover:text-white/80 hover:border-white/20 transition-colors"
        aria-label={muted || !playing ? 'Unmute background music' : 'Mute background music'}
        title={muted || !playing ? 'Play music' : 'Mute music'}
      >
        {muted || !playing ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 5L6 9H2v6h4l5 4V5z" />
            <line x1="23" y1="9" x2="17" y2="15" />
            <line x1="17" y1="9" x2="23" y2="15" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 5L6 9H2v6h4l5 4V5z" />
            <path d="M15.54 8.46a5 5 0 010 7.07" />
            <path d="M19.07 4.93a10 10 0 010 14.14" />
          </svg>
        )}
      </button>
    </>
  )
}
