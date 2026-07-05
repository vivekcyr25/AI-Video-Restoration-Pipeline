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

function beatState(progress, index, total) {
  const start = index / total
  const end = (index + 1) / total
  const width = end - start

  if (progress < start - width * 0.05 || progress > end + width * 0.05) {
    return { opacity: 0, visible: false, zIndex: 0 }
  }

  const local = (progress - start) / width
  let opacity = 1

  if (local < 0.18) opacity = local / 0.18
  else if (local > 0.82) opacity = (1 - local) / 0.18

  opacity = Math.max(0, Math.min(1, opacity))

  return {
    opacity,
    visible: opacity > 0.02,
    zIndex: Math.round(opacity * 100),
  }
}

export function getBeatStyles(progress, index, total) {
  const { opacity, visible, zIndex } = beatState(progress, index, total)
  const translateY = (1 - opacity) * 20

  return {
    opacity,
    zIndex,
    visibility: visible ? 'visible' : 'hidden',
    transform: `translate3d(0, ${translateY}px, 0)`,
    pointerEvents: opacity > 0.6 ? 'auto' : 'none',
  }
}

export function getIntroExitOpacity(progress) {
  if (progress < 0.88) return 1
  return Math.max(0, 1 - (progress - 0.88) / 0.12)
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
