import { useState, useEffect } from 'react'

const INVARIANTS = [
  {
    key: 'lighting',
    label: 'Lighting',
    desc: 'Matches assets across exposure shifts, shadows, and color temperature — no pixel-level similarity required.',
  },
  {
    key: 'pose',
    label: 'Pose',
    desc: 'ArcFace embeddings stay stable across head angles and framing differences between source and reference.',
  },
  {
    key: 'identity',
    label: 'Identity',
    desc: 'Same subject across degraded frames and high-quality reference assets — reliably paired every time.',
  },
]

export default function InteractiveInvariant() {
  const [active, setActive] = useState('lighting')
  const [hovering, setHovering] = useState(false)

  useEffect(() => {
    if (hovering) return
    let i = 0
    const keys = INVARIANTS.map((v) => v.key)
    const timer = setInterval(() => {
      i = (i + 1) % keys.length
      setActive(keys[i])
    }, 2800)
    return () => clearInterval(timer)
  }, [hovering])

  const current = INVARIANTS.find((v) => v.key === active)

  return (
    <div className="flex flex-col items-center">
      <h1 className="text-4xl sm:text-5xl md:text-7xl font-semibold tracking-tight leading-[1.08] mb-6">
        <span className="text-white">A </span>
        <button
          type="button"
          className="relative inline-block group cursor-default"
          onMouseEnter={() => setHovering(true)}
          onMouseLeave={() => setHovering(false)}
        >
          <span className="relative z-10 bg-gradient-to-r from-cyber-glow via-white to-cyber-blue bg-clip-text text-transparent animate-[shimmer_3s_ease-in-out_infinite] bg-[length:200%_auto]">
            lighting-invariant
          </span>
          <span className="absolute -inset-x-2 -inset-y-1 rounded-xl bg-cyber-blue/10 blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
        <span className="text-white block sm:inline"> restoration algorithm.</span>
      </h1>

      <div
        className="flex flex-wrap justify-center gap-2 mb-5"
        onMouseEnter={() => setHovering(true)}
        onMouseLeave={() => setHovering(false)}
      >
        {INVARIANTS.map((inv) => (
          <button
            key={inv.key}
            type="button"
            onClick={() => setActive(inv.key)}
            onMouseEnter={() => setActive(inv.key)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 border ${
              active === inv.key
                ? 'bg-cyber-blue/25 border-cyber-glow/50 text-cyber-glow shadow-[0_0_24px_rgba(0,113,227,0.2)] scale-105'
                : 'bg-white/[0.04] border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'
            }`}
          >
            {inv.label}
          </button>
        ))}
      </div>

      <p
        key={active}
        className="text-base sm:text-lg max-w-lg mx-auto leading-relaxed font-light text-white/65 animate-[fadeIn_0.4s_ease-out]"
      >
        {current?.desc}
      </p>
    </div>
  )
}
