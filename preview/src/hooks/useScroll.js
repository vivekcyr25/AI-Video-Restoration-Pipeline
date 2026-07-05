import { useState, useEffect, useRef } from 'react'

export function useScrollProgress(ref) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    let raf = 0
    const update = () => {
      raf = 0
      const rect = el.getBoundingClientRect()
      const scrollable = el.offsetHeight - window.innerHeight
      if (scrollable <= 0) {
        setProgress(0)
        return
      }
      const scrolled = -rect.top
      setProgress(Math.min(1, Math.max(0, scrolled / scrollable)))
    }

    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update)
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', update)
      if (raf) cancelAnimationFrame(raf)
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
  const [scrollProgress, setScrollProgress] = useState(0)
  const rafRef = useRef(0)

  useEffect(() => {
    const update = () => {
      rafRef.current = 0
      const max = document.documentElement.scrollHeight - window.innerHeight
      setScrollProgress(max > 0 ? window.scrollY / max : 0)
    }

    const onScroll = () => {
      if (!rafRef.current) rafRef.current = requestAnimationFrame(update)
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [])

  return { scrollProgress }
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
    transform: `translate3d(0, ${translateY}px, 0) scale(${scale})`,
    pointerEvents: opacity > 0.5 ? 'auto' : 'none',
    willChange: opacity > 0 && opacity < 1 ? 'opacity, transform' : 'auto',
  }
}

export function useSectionScroll(ref, stageCount) {
  const [activeIndex, setActiveIndex] = useState(0)
  const [restoreAmount, setRestoreAmount] = useState(0)
  const lastIndexRef = useRef(0)

  useEffect(() => {
    const container = ref.current
    if (!container) return

    let rafRef = 0
    const lastAmountRef = { current: -1 }

    const update = () => {
      rafRef = 0
      const rect = container.getBoundingClientRect()
      const scrollable = container.offsetHeight - window.innerHeight
      if (scrollable <= 0) return

      const progress = Math.min(1, Math.max(0, -rect.top / scrollable))
      const idx = Math.min(stageCount - 1, Math.floor(progress * stageCount))

      if (idx !== lastIndexRef.current) {
        lastIndexRef.current = idx
        setActiveIndex(idx)
      }

      if (Math.abs(progress - lastAmountRef.current) >= 0.012) {
        lastAmountRef.current = progress
        setRestoreAmount(progress)
      }
    }

    const onScroll = () => {
      if (!rafRef) rafRef = requestAnimationFrame(update)
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', update)
      if (rafRef) cancelAnimationFrame(rafRef)
    }
  }, [ref, stageCount])

  return { activeIndex, restoreAmount }
}
