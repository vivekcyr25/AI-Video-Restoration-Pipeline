import { useRef, useState, useEffect } from 'react'
import { STAGES } from '../data/pipeline'

function StageCard({ stage, active, onClick, index }) {
  return (
    <div
      className={`relative pl-8 transition-all duration-700 ${
        active ? 'opacity-100 translate-x-0' : 'opacity-30 translate-x-4'
      }`}
    >
      {/* Connector dot */}
      <div
        className={`absolute left-0 top-6 w-3 h-3 rounded-full border-2 transition-all duration-500 ${
          active
            ? 'bg-cyber-blue border-cyber-glow shadow-[0_0_16px_rgba(100,210,255,0.6)] scale-125'
            : 'bg-transparent border-white/20'
        }`}
      />

      <button
        onClick={() => onClick(stage.id)}
        className={`w-full text-left glass rounded-2xl p-5 sm:p-6 transition-all duration-500 ${
          active ? 'border-cyber-blue/30 bg-white/[0.08] shadow-[0_0_40px_rgba(0,113,227,0.08)]' : 'glass-hover'
        }`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl bg-gradient-to-br ${stage.color} border border-white/10 shrink-0`}
          >
            {stage.icon}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono text-white/35 uppercase tracking-widest">
                Stage {String(stage.id).padStart(2, '0')}
              </span>
              {active && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyber-blue/20 text-cyber-glow animate-pulse-soft">
                  Active
                </span>
              )}
            </div>
            <h3 className="text-lg font-semibold tracking-tight text-white/95 mb-1">
              {stage.label}
            </h3>
            <p className="text-xs text-cyber-blue/80 font-mono mb-2">{stage.tool}</p>
            <p className="text-sm text-white/55 leading-relaxed">{stage.description}</p>
            <p className="mt-3 text-[11px] font-mono text-white/30">→ {stage.output}</p>
          </div>
        </div>
      </button>
    </div>
  )
}

function PipelineVisual({ activeIndex, progress }) {
  const restoreAmount = Math.min(1, (activeIndex + progress) / STAGES.length)

  return (
    <div className="relative aspect-[4/3] rounded-3xl overflow-hidden glass border border-white/10">
      {/* Degraded layer */}
      <div
        className="absolute inset-0 vintage-media"
        style={{
          background: 'linear-gradient(145deg, #2a1810 0%, #4a3728 40%, #1a1008 100%)',
          opacity: 1 - restoreAmount * 0.85,
        }}
      />

      {/* Restored layer */}
      <div
        className="absolute inset-0 restored-media"
        style={{
          background: 'linear-gradient(145deg, #0c1929 0%, #1a4a6e 30%, #2d6a4f 60%, #8b6914 100%)',
          opacity: restoreAmount,
        }}
      />

      {/* Scene silhouettes */}
      <div className="absolute inset-0 flex items-end justify-center pb-[18%]">
        <div
          className="flex gap-4 items-end transition-all duration-700"
          style={{
            opacity: 0.35 + restoreAmount * 0.55,
            filter: `blur(${(1 - restoreAmount) * 3}px)`,
          }}
        >
          <div className="w-10 h-20 rounded-t-full bg-white/25" />
          <div className="w-14 h-28 rounded-t-full bg-white/35" />
          <div className="w-10 h-20 rounded-t-full bg-white/25" />
        </div>
      </div>

      {/* Scan overlay when processing */}
      {restoreAmount > 0.05 && restoreAmount < 0.95 && (
        <div
          className="absolute inset-x-0 h-24 bg-gradient-to-b from-transparent via-cyber-blue/20 to-transparent pointer-events-none"
          style={{ top: `${restoreAmount * 80}%`, transition: 'top 0.3s ease-out' }}
        />
      )}

      {/* Status badge */}
      <div className="absolute top-4 left-4 right-4 flex justify-between items-start">
        <span className="text-[10px] font-mono px-2 py-1 rounded-md glass text-white/50">
          {restoreAmount < 0.15
            ? 'INPUT · DEGRADED'
            : restoreAmount < 0.85
              ? 'PROCESSING · STAGE ' + (activeIndex + 1)
              : 'OUTPUT · RESTORED'}
        </span>
        <span className="text-[10px] font-mono text-cyber-glow">
          {Math.round(restoreAmount * 100)}%
        </span>
      </div>

      {/* Grain on degraded portion */}
      {restoreAmount < 0.5 && (
        <div className="absolute inset-0 opacity-[0.08] animate-grain pointer-events-none mix-blend-overlay" />
      )}
    </div>
  )
}

export default function ScrollWorkflow({ onStageClick }) {
  const containerRef = useRef(null)
  const [activeIndex, setActiveIndex] = useState(0)
  const [sectionProgress, setSectionProgress] = useState(0)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const update = () => {
      const rect = container.getBoundingClientRect()
      const scrollable = container.offsetHeight - window.innerHeight
      if (scrollable <= 0) return

      const scrolled = Math.max(0, -rect.top)
      const progress = Math.min(1, scrolled / scrollable)
      setSectionProgress(progress)

      const idx = Math.min(STAGES.length - 1, Math.floor(progress * STAGES.length))
      setActiveIndex(idx)
    }

    update()
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [])

  const lineHeight = ((activeIndex + 0.5) / STAGES.length) * 100

  return (
    <section ref={containerRef} className="relative" style={{ height: `${STAGES.length * 70 + 40}vh` }}>
      <div className="sticky top-0 min-h-screen flex items-center py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 w-full">
          <div className="text-center mb-12">
            <p className="text-xs font-medium tracking-[0.25em] uppercase text-cyber-blue mb-3">
              How It Works
            </p>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight">
              The pipeline, connected.
            </h2>
            <p className="mt-3 text-white/45 max-w-lg mx-auto text-sm sm:text-base">
              Scroll to walk through each stage — watch recovery build in real time.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-start">
            {/* Sticky visual */}
            <div className="lg:sticky lg:top-28">
              <PipelineVisual activeIndex={activeIndex} progress={sectionProgress * STAGES.length - activeIndex} />

              {/* Progress rail */}
              <div className="mt-6 flex gap-1">
                {STAGES.map((s, i) => (
                  <div
                    key={s.id}
                    className={`h-1 flex-1 rounded-full transition-all duration-500 ${
                      i <= activeIndex ? 'bg-cyber-blue' : 'bg-white/10'
                    }`}
                  />
                ))}
              </div>
              <p className="mt-3 text-center text-xs text-white/35 font-mono">
                {STAGES[activeIndex].label} · {STAGES[activeIndex].tool}
              </p>
            </div>

            {/* Scrolling stages with connector line */}
            <div className="relative">
              <div className="absolute left-[5px] top-8 bottom-8 w-px bg-white/10">
                <div
                  className="absolute top-0 left-0 w-full bg-gradient-to-b from-cyber-blue to-cyber-glow transition-all duration-500"
                  style={{ height: `${lineHeight}%` }}
                />
              </div>

              <div className="space-y-6">
                {STAGES.map((stage, i) => (
                  <StageCard
                    key={stage.id}
                    stage={stage}
                    index={i}
                    active={i === activeIndex}
                    onClick={onStageClick}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
