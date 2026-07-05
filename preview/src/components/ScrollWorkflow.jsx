import { memo, useRef } from 'react'
import { STAGES } from '../data/pipeline'
import { useSectionScroll } from '../hooks/useScroll'

const StageCard = memo(function StageCard({ stage, active, onClick }) {
  return (
    <div
      className={`relative pl-8 transition-opacity duration-200 ${
        active ? 'opacity-100' : 'opacity-35'
      }`}
      style={{ contentVisibility: 'auto', containIntrinsicSize: '0 120px' }}
    >
      <div
        className={`absolute left-0 top-6 w-3 h-3 rounded-full border-2 transition-colors duration-200 ${
          active
            ? 'bg-cyber-blue border-cyber-glow shadow-[0_0_12px_rgba(100,210,255,0.5)]'
            : 'bg-transparent border-white/20'
        }`}
      />

      <button
        onClick={() => onClick(stage.id)}
        className={`w-full text-left rounded-2xl p-5 sm:p-6 border transition-colors duration-200 ${
          active
            ? 'border-cyber-blue/30 bg-white/[0.07]'
            : 'border-white/[0.06] bg-white/[0.03] hover:bg-white/[0.05]'
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
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyber-blue/20 text-cyber-glow">
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
})

const PipelineVisual = memo(function PipelineVisual({ activeIndex, restoreAmount }) {
  const pct = Math.round(restoreAmount * 100)

  return (
    <div className="relative aspect-[4/3] rounded-3xl overflow-hidden border border-white/10 bg-[#0c0c10]">
      <div
        className="absolute inset-0 vintage-media transition-opacity duration-150"
        style={{
          background: 'linear-gradient(145deg, #2a1810 0%, #4a3728 40%, #1a1008 100%)',
          opacity: 1 - restoreAmount * 0.85,
        }}
      />
      <div
        className="absolute inset-0 restored-media transition-opacity duration-150"
        style={{
          background: 'linear-gradient(145deg, #0c1929 0%, #1a4a6e 30%, #2d6a4f 60%, #8b6914 100%)',
          opacity: restoreAmount,
        }}
      />
      <div className="absolute inset-0 flex items-end justify-center pb-[18%]">
        <div
          className="flex gap-4 items-end"
          style={{ opacity: 0.35 + restoreAmount * 0.55 }}
        >
          <div className="w-10 h-20 rounded-t-full bg-white/25" />
          <div className="w-14 h-28 rounded-t-full bg-white/35" />
          <div className="w-10 h-20 rounded-t-full bg-white/25" />
        </div>
      </div>

      {restoreAmount > 0.05 && restoreAmount < 0.95 && (
        <div
          className="absolute inset-x-0 h-16 bg-gradient-to-b from-transparent via-cyber-blue/15 to-transparent pointer-events-none"
          style={{ top: `${restoreAmount * 80}%` }}
        />
      )}

      <div className="absolute top-4 left-4 right-4 flex justify-between">
        <span className="text-[10px] font-mono px-2 py-1 rounded-md bg-black/40 text-white/50">
          {restoreAmount < 0.15
            ? 'INPUT · DEGRADED ASSET'
            : restoreAmount < 0.85
              ? `PROCESSING · STAGE ${activeIndex + 1}`
              : 'OUTPUT · RESTORED ASSET'}
        </span>
        <span className="text-[10px] font-mono text-cyber-glow">{pct}%</span>
      </div>
    </div>
  )
})

export default function ScrollWorkflow({ onStageClick }) {
  const containerRef = useRef(null)
  const { activeIndex, restoreAmount } = useSectionScroll(containerRef, STAGES.length)

  const lineHeight = ((activeIndex + 0.5) / STAGES.length) * 100
  const sectionHeight = 60 + STAGES.length * 18

  return (
    <section
      ref={containerRef}
      className="relative z-10 bg-[#050508]"
      style={{ height: `${sectionHeight}vh` }}
    >
      <div className="sticky top-0 h-screen flex items-center py-16 overflow-hidden">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 w-full">
          <div className="text-center mb-8">
            <p className="text-xs font-medium tracking-[0.25em] uppercase text-cyber-blue mb-3">
              How It Works
            </p>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight">
              The pipeline, connected.
            </h2>
            <p className="mt-3 text-white/45 max-w-lg mx-auto text-sm sm:text-base">
              Scroll to walk through each stage — watch asset recovery build in real time.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-6 lg:gap-10 items-center">
            <div className="shrink-0">
              <PipelineVisual activeIndex={activeIndex} restoreAmount={restoreAmount} />
              <div className="mt-4 flex gap-1">
                {STAGES.map((s, i) => (
                  <div
                    key={s.id}
                    className={`h-1 flex-1 rounded-full transition-colors duration-200 ${
                      i <= activeIndex ? 'bg-cyber-blue' : 'bg-white/10'
                    }`}
                  />
                ))}
              </div>
              <p className="mt-2 text-center text-xs text-white/35 font-mono">
                {STAGES[activeIndex].label} · {STAGES[activeIndex].tool}
              </p>
            </div>

            <div className="relative min-h-[280px]">
              <div className="absolute left-[5px] top-8 bottom-8 w-px bg-white/10">
                <div
                  className="absolute top-0 left-0 w-full bg-gradient-to-b from-cyber-blue to-cyber-glow transition-[height] duration-200"
                  style={{ height: `${lineHeight}%` }}
                />
              </div>
              <StageCard
                key={STAGES[activeIndex].id}
                stage={STAGES[activeIndex]}
                active
                onClick={onStageClick}
              />
              <p className="mt-4 pl-8 text-[11px] font-mono text-white/30">
                Stage {activeIndex + 1} of {STAGES.length} · tap for details
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
