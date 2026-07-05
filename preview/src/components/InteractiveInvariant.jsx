import { useState, useEffect } from 'react'

const INVARIANTS = [
  {
    key: 'lighting',
    label: 'Lighting',
    desc: 'Matches assets across exposure shifts, shadows, and color temperature.',
  },
  {
    key: 'pose',
    label: 'Pose',
    desc: 'ArcFace embeddings stay stable across head angles and framing differences.',
  },
  {
    key: 'identity',
    label: 'Identity',
    desc: 'Same subject across degraded frames and reference assets — reliably paired.',
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
    <div className="flex flex-col items-center w-full">
      <h1 className="text-3xl sm:text-4xl md:text-6xl font-semibold tracking-tight leading-[1.12] mb-5 text-center">
        <span className="text-white">A </span>
        <span className="bg-gradient-to-r from-cyber-glow via-white to-cyber-blue bg-clip-text text-transparent">
          lighting-invariant
        </span>
        <span className="text-white block sm:inline"> restoration algorithm.</span>
      </h1>

      <div
        className="flex flex-wrap justify-center gap-2 mb-4"
        onMouseEnter={() => setHovering(true)}
        onMouseLeave={() => setHovering(false)}
      >
        {INVARIANTS.map((inv) => (
          <button
            key={inv.key}
            type="button"
            onClick={() => setActive(inv.key)}
            onMouseEnter={() => setActive(inv.key)}
            className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border ${
              active === inv.key
                ? 'bg-cyber-blue/25 border-cyber-glow/50 text-cyber-glow'
                : 'bg-white/[0.04] border-white/10 text-white/50 hover:text-white/70'
            }`}
          >
            {inv.label}
          </button>
        ))}
      </div>

      <p
        key={active}
        className="text-sm sm:text-base max-w-md mx-auto leading-relaxed font-light text-white/60 text-center min-h-[3rem]"
      >
        {current?.desc}
      </p>
    </div>
  )
}
