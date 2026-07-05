import { useState, useEffect, useRef } from 'react'

export function useScrollProgress(ref) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const update = () => {
      const rect = el.getBoundingClientRect()
      const scrollable = el.offsetHeight - window.innerHeight
      if (scrollable <= 0) {
        setProgress(0)
        return
      }
      const scrolled = -rect.top
      setProgress(Math.min(1, Math.max(0, scrolled / scrollable)))
    }

    update()
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [ref])

  return progress
}

export function useInView(threshold = 0.4) {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => setInView(entry.isIntersecting),
      { threshold, rootMargin: '-10% 0px -10% 0px' }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [threshold])

  return [ref, inView]
}

export function useGlobalScroll() {
  const [scrollY, setScrollY] = useState(0)
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const update = () => {
      setScrollY(window.scrollY)
      const max = document.documentElement.scrollHeight - window.innerHeight
      setScrollProgress(max > 0 ? window.scrollY / max : 0)
    }
    update()
    window.addEventListener('scroll', update, { passive: true })
    return () => window.removeEventListener('scroll', update)
  }, [])

  return { scrollY, scrollProgress }
}

function beatOpacity(progress, index, total) {
  const slice = 1 / total
  const start = index * slice
  const end = (index + 1) * slice
  const fade = slice * 0.25

  if (progress < start - fade) return 0
  if (progress < start + fade) return (progress - (start - fade)) / (fade * 2)
  if (progress < end - fade) return 1
  if (progress < end + fade) return 1 - (progress - (end - fade)) / (fade * 2)
  return 0
}

export function getBeatStyles(progress, index, total) {
  const opacity = beatOpacity(progress, index, total)
  const translateY = (1 - opacity) * 28
  const scale = 0.96 + opacity * 0.04
  return {
    opacity,
    transform: `translateY(${translateY}px) scale(${scale})`,
    pointerEvents: opacity > 0.5 ? 'auto' : 'none',
  }
}
