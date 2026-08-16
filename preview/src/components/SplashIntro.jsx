import { useState, useEffect, useRef, useCallback } from 'react'

/* ─── Glitch character set ─── */
const GLITCH_CHARS = '█▓▒░╬╫╪┼┤╡╞╟╚╔╩╦╠═╬▌▐░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╠═╬01'

function scramble(text, intensity = 0.3) {
  return text
    .split('')
    .map(ch => {
      if (ch === ' ') return ' '
      return Math.random() < intensity
        ? GLITCH_CHARS[Math.floor(Math.random() * GLITCH_CHARS.length)]
        : ch
    })
    .join('')
}

/* ─── Animated glitch text hook ─── */
function useGlitchText(text, active, intensity = 0.25, fps = 12) {
  const [display, setDisplay] = useState(text)
  const frame = useRef(null)

  useEffect(() => {
    if (!active) { setDisplay(text); return }
    let tick = 0
    const run = () => {
      tick++
      // Settle more and more toward the real text over time
      const decayedIntensity = Math.max(0, intensity - tick * 0.012)
      setDisplay(tick > 30 ? text : scramble(text, decayedIntensity))
      if (decayedIntensity > 0) {
        frame.current = setTimeout(run, 1000 / fps)
      } else {
        setDisplay(text)
      }
    }
    frame.current = setTimeout(run, 60)
    return () => clearTimeout(frame.current)
  }, [text, active, intensity, fps])

  return display
}

/* ─── RGB split layer ─── */
function RGBSplit({ children, active }) {
  if (!active) return <>{children}</>
  return (
    <span className="relative inline-block">
      <span className="absolute inset-0 text-red-500 opacity-40" style={{ transform: 'translate(-3px, 0)', clipPath: 'inset(0 0 60% 0)' }}>{children}</span>
      <span className="absolute inset-0 text-cyan-400 opacity-40" style={{ transform: 'translate(3px, 0)', clipPath: 'inset(60% 0 0 0)' }}>{children}</span>
      <span className="relative">{children}</span>
    </span>
  )
}

/* ─── Horizontal tear bars ─── */
function TearBars({ active }) {
  const [bars, setBars] = useState([])

  useEffect(() => {
    if (!active) { setBars([]); return }
    const gen = () => {
      const count = Math.floor(Math.random() * 3) + 1
      setBars(Array.from({ length: count }, () => ({
        top: Math.random() * 90,
        height: Math.random() * 4 + 1,
        offset: (Math.random() - 0.5) * 24,
        opacity: Math.random() * 0.4 + 0.15,
      })))
    }
    gen()
    const id = setInterval(gen, 220)
    return () => clearInterval(id)
  }, [active])

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {bars.map((b, i) => (
        <div
          key={i}
          className="absolute left-0 right-0 bg-white"
          style={{
            top: `${b.top}%`,
            height: `${b.height}px`,
            opacity: b.opacity,
            transform: `translateX(${b.offset}px)`,
            mixBlendMode: 'overlay',
          }}
        />
      ))}
    </div>
  )
}

/* ─── SVG Turbulence filter (applied to entire screen during "Then" phases) ─── */
function TurbulenceFilter({ active, intensity = 0 }) {
  return (
    <svg width="0" height="0" className="absolute">
      <defs>
        <filter id="tape-warp" x="-10%" y="-10%" width="120%" height="120%">
          <feTurbulence
            type="turbulence"
            baseFrequency={active ? `0.0${Math.floor(intensity * 6 + 1)} 0.0${Math.floor(intensity * 4 + 2)}` : '0.001 0.001'}
            numOctaves="3"
            seed="2"
            result="noise"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="noise"
            scale={active ? intensity * 14 + 2 : 0}
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </defs>
    </svg>
  )
}

/* ─── Sequence definition ─── */
const SEQUENCE = [
  { id: 0, text: 'Some memories are like',   sub: null,       duration: 2200, glitch: false, tear: false },
  { id: 1, text: 'faded photographs.',        sub: null,       duration: 2200, glitch: false, tear: false },
  { id: 2, text: 'Then time degrades them.', sub: null,       duration: 2000, glitch: true,  tear: true,  intensity: 0.28 },
  { id: 3, text: 'Then the tape fades.',     sub: null,       duration: 2000, glitch: true,  tear: true,  intensity: 0.40 },
  { id: 4, text: 'Then faces blur.',         sub: null,       duration: 2000, glitch: true,  tear: true,  intensity: 0.50 },
  { id: 5, text: 'Then colors die.',         sub: null,       duration: 2000, glitch: true,  tear: true,  intensity: 0.60 },
  { id: 6, text: 'What if AI could remember', sub: 'for you?', duration: 2800, glitch: false, tear: false },
  {
    id: 7,
    text: 'AI Video Restoration Pipeline',
    sub: 'VIVEK SHARMA · COMPUTER VISION ENGINEER',
    duration: 3200,
    isBrand: true,
    glitch: false,
    tear: false,
  },
]

/* ─── GlitchCard — text card with all distortion effects ─── */
function GlitchCard({ card, visible }) {
  const isGlitch = card?.glitch && visible
  const glitched = useGlitchText(card?.text ?? '', isGlitch, card?.intensity ?? 0.3)

  return (
    <div
      className="relative z-10 text-center px-8 max-w-5xl mx-auto"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0) skewX(0deg)' : 'translateY(14px) skewX(-1deg)',
        transition: 'opacity 0.5s ease, transform 0.5s ease',
        filter: isGlitch ? 'url(#tape-warp)' : 'none',
      }}
    >
      {card && (
        card.isBrand ? (
          // ── Brand card ──
          <div>
            <div className="flex items-center justify-center gap-4 mb-8">
              <div className="h-px w-20 bg-gradient-to-r from-transparent to-electric-cyan/60" />
              <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', letterSpacing: '0.4em', color: 'rgba(0,240,255,0.7)', textTransform: 'uppercase' }}>
                AI Research Project
              </span>
              <div className="h-px w-20 bg-gradient-to-l from-transparent to-electric-cyan/60" />
            </div>

            <h1
              style={{
                fontFamily: 'Barlow Condensed, sans-serif',
                fontSize: 'clamp(3rem, 8vw, 7rem)',
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: '-0.01em',
                lineHeight: 1,
                color: '#fff',
              }}
            >
              AI Video{' '}
              <span style={{
                background: 'linear-gradient(90deg, #00f0ff 0%, #a855f7 60%, #38bdf8 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>
                Restoration
              </span>
              <br />Pipeline
            </h1>

            <p style={{
              marginTop: '2rem',
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '11px',
              letterSpacing: '0.35em',
              textTransform: 'uppercase',
              color: 'rgba(148,163,184,0.8)',
            }}>
              {card.sub}
            </p>

            {/* Loading bar */}
            <div style={{ marginTop: '2.5rem', width: '12rem', height: '1px', background: 'rgba(255,255,255,0.1)', borderRadius: '9999px', overflow: 'hidden', margin: '2.5rem auto 0' }}>
              <div
                style={{
                  height: '100%',
                  borderRadius: '9999px',
                  background: 'linear-gradient(90deg, #00f0ff, #a855f7)',
                  width: visible ? '100%' : '0%',
                  transition: 'width 3s linear',
                }}
              />
            </div>
          </div>
        ) : (
          // ── Quote card ──
          <div>
            <RGBSplit active={isGlitch}>
              <p
                style={{
                  fontFamily: 'Barlow Condensed, sans-serif',
                  fontSize: 'clamp(2.2rem, 6vw, 5.5rem)',
                  fontWeight: card.id <= 1 ? 300 : 500,
                  fontStyle: card.id === 0 ? 'italic' : 'normal',
                  lineHeight: 1.1,
                  letterSpacing: '0.01em',
                  color: isGlitch ? 'rgba(255,255,255,0.85)' : 'rgba(255,255,255,0.92)',
                  textShadow: isGlitch
                    ? '0 0 20px rgba(0,240,255,0.15), 0 0 40px rgba(0,240,255,0.08)'
                    : 'none',
                }}
              >
                {isGlitch ? glitched : card.text}
              </p>
            </RGBSplit>

            {card.sub && (
              <p style={{
                marginTop: '0.75rem',
                fontFamily: 'Barlow Condensed, sans-serif',
                fontSize: 'clamp(2rem, 5.5vw, 5rem)',
                fontWeight: 700,
                letterSpacing: '0.01em',
                color: '#00f0ff',
              }}>
                {card.sub}
              </p>
            )}

            {/* Intensity gauge for glitch cards */}
            {card.glitch && (
              <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '9px', color: 'rgba(255,100,100,0.5)', letterSpacing: '0.2em', textTransform: 'uppercase' }}>
                  SIGNAL LOSS
                </span>
                <div style={{ width: '80px', height: '2px', background: 'rgba(255,255,255,0.08)', borderRadius: '9999px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    borderRadius: '9999px',
                    background: 'rgba(255,80,80,0.7)',
                    width: `${(card.intensity ?? 0.3) * 100}%`,
                    transition: 'width 0.3s ease',
                  }} />
                </div>
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '9px', color: 'rgba(255,80,80,0.5)' }}>
                  {Math.round((card.intensity ?? 0.3) * 100)}%
                </span>
              </div>
            )}
          </div>
        )
      )}
    </div>
  )
}

/* ─── Rolling scan glow ─── */
function ScanGlow() {
  const [pos, setPos] = useState(0)
  useEffect(() => {
    let raf
    const tick = () => {
      setPos(p => (p + 0.5) % 110)
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])
  return (
    <div
      className="absolute left-0 right-0 pointer-events-none"
      style={{
        top: `${pos}%`,
        height: '80px',
        background: 'linear-gradient(to bottom, transparent, rgba(0,240,255,0.025) 40%, rgba(0,240,255,0.04) 50%, rgba(0,240,255,0.025) 60%, transparent)',
        filter: 'blur(3px)',
        transform: 'translateY(-50%)',
      }}
    />
  )
}

/* ─── Main export ─── */
export default function SplashIntro({ onDone }) {
  const [phase, setPhase]       = useState(0)
  const [visible, setVisible]   = useState(false)
  const [exiting, setExiting]   = useState(false)

  const doExit = useCallback(() => {
    setExiting(true)
    setTimeout(onDone, 800)
  }, [onDone])

  useEffect(() => {
    if (phase >= SEQUENCE.length) {
      setTimeout(doExit, 300)
      return
    }
    const fadeIn  = setTimeout(() => setVisible(true), 80)
    const fadeOut = setTimeout(() => {
      setVisible(false)
      setTimeout(() => setPhase(p => p + 1), 550)
    }, SEQUENCE[phase].duration)
    return () => { clearTimeout(fadeIn); clearTimeout(fadeOut) }
  }, [phase, doExit])

  const card = SEQUENCE[phase] ?? null
  const isGlitching = card?.glitch && visible

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: '#010103',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        userSelect: 'none',
        opacity: exiting ? 0 : 1,
        transition: 'opacity 0.7s ease',
        pointerEvents: exiting ? 'none' : 'auto',
      }}
    >
      {/* SVG Turbulence filter */}
      <TurbulenceFilter active={isGlitching} intensity={card?.intensity ?? 0} />

      {/* Noise grain */}
      <div style={{
        position: 'absolute', inset: 0, opacity: 0.045, pointerEvents: 'none',
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        backgroundSize: '160px 160px',
      }} />

      {/* CRT scanlines */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        opacity: isGlitching ? 0.13 : 0.07,
        transition: 'opacity 0.3s',
        background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.9) 2px, rgba(0,0,0,0.9) 4px)',
      }} />

      {/* Rolling scan glow */}
      <ScanGlow />

      {/* Horizontal tape tears — only on glitch phases */}
      <TearBars active={isGlitching} />

      {/* Vignette */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse 75% 75% at 50% 50%, transparent 25%, rgba(0,0,0,0.8) 100%)',
      }} />

      {/* Corner reticles */}
      {[
        { top: '1.25rem', left: '1.25rem', borderTop: '1px solid', borderLeft: '1px solid' },
        { top: '1.25rem', right: '1.25rem', borderTop: '1px solid', borderRight: '1px solid' },
        { bottom: '1.25rem', left: '1.25rem', borderBottom: '1px solid', borderLeft: '1px solid' },
        { bottom: '1.25rem', right: '1.25rem', borderBottom: '1px solid', borderRight: '1px solid' },
      ].map((s, i) => (
        <div key={i} style={{ position: 'absolute', width: '1.5rem', height: '1.5rem', borderColor: 'rgba(255,255,255,0.15)', ...s }} />
      ))}

      {/* Phase label — top-left */}
      {card && (
        <div style={{
          position: 'absolute', top: '1.5rem', left: '2rem',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '9px', letterSpacing: '0.3em',
          color: isGlitching ? 'rgba(255,80,80,0.5)' : 'rgba(255,255,255,0.15)',
          textTransform: 'uppercase',
          transition: 'color 0.3s',
        }}>
          {isGlitching ? '◈ SIGNAL CORRUPT' : `◈ FRAME ${String(card.id + 1).padStart(2, '0')} / ${SEQUENCE.length}`}
        </div>
      )}

      {/* Main text card */}
      <GlitchCard card={card} visible={visible} />

      {/* Bottom telemetry */}
      <div style={{
        position: 'absolute', bottom: '1.5rem', left: 0, right: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 2rem',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: '9px', letterSpacing: '0.2em',
        color: 'rgba(255,255,255,0.15)',
        textTransform: 'uppercase',
      }}>
        <span>VIVEK SHARMA · 2026</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            width: '6px', height: '6px', borderRadius: '50%',
            background: isGlitching ? 'rgba(255,80,80,0.7)' : 'rgba(0,240,255,0.5)',
            display: 'inline-block',
            boxShadow: isGlitching ? '0 0 6px rgba(255,80,80,0.6)' : '0 0 6px rgba(0,240,255,0.5)',
            transition: 'all 0.3s',
          }} />
          {isGlitching ? 'DEGRADED SIGNAL' : 'RENDERING PIPELINE'}
        </span>
        <span>COMPUTER VISION · PYTHON</span>
      </div>

      {/* Skip */}
      <button
        onClick={doExit}
        style={{
          position: 'absolute', top: '1.5rem', right: '2rem',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '9px', letterSpacing: '0.3em',
          color: 'rgba(255,255,255,0.2)',
          textTransform: 'uppercase',
          background: 'none', border: 'none', cursor: 'pointer',
          transition: 'color 0.2s',
        }}
        onMouseEnter={e => (e.target.style.color = 'rgba(255,255,255,0.6)')}
        onMouseLeave={e => (e.target.style.color = 'rgba(255,255,255,0.2)')}
      >
        SKIP ↓
      </button>
    </div>
  )
}
