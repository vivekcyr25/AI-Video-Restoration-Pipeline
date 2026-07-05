import { useState, useEffect } from 'react'

function MediaFrame({ variant, label, artifacts }) {
  const isVintage = variant === 'vintage'

  return (
    <div className="relative flex-1 min-w-0">
      <div
        className={`relative aspect-video rounded-2xl overflow-hidden border ${
          isVintage
            ? 'border-amber-900/40 shadow-[inset_0_0_30px_rgba(139,105,20,0.3)]'
            : 'border-white/10 shadow-[0_0_40px_rgba(0,113,227,0.15)]'
        }`}
      >
        <div
          className={`absolute inset-0 ${
            isVintage ? 'vintage-media' : 'restored-media'
          }`}
          style={{
            background: isVintage
              ? `linear-gradient(135deg, #3d2b1f 0%, #5c4033 30%, #2a1810 60%, #4a3728 100%)`
              : `linear-gradient(135deg, #1a3a5c 0%, #2d5a87 25%, #4a7c59 50%, #8b6914 75%, #c4956a 100%)`,
          }}
        />

        {/* Simulated scene silhouettes */}
        <div className="absolute inset-0 flex items-end justify-center pb-[15%]">
          <div
            className={`flex gap-3 items-end ${
              isVintage ? 'opacity-40 blur-[2px]' : 'opacity-80'
            }`}
          >
            <div className="w-8 h-16 rounded-t-full bg-white/20" />
            <div className="w-10 h-20 rounded-t-full bg-white/30" />
            <div className="w-8 h-16 rounded-t-full bg-white/20" />
          </div>
        </div>

        {isVintage && (
          <>
            <div
              className="absolute inset-0 opacity-[0.12] animate-grain pointer-events-none"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
                backgroundSize: '128px 128px',
              }}
            />
            <div className="absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(0,0,0,0.08)_2px,rgba(0,0,0,0.08)_4px)] pointer-events-none" />
            {artifacts && (
              <div className="absolute top-1/3 left-1/4 w-16 h-1 bg-black/30 rotate-12 blur-sm" />
            )}
            <div className="absolute bottom-3 left-3 text-[10px] font-mono text-amber-400/70 tracking-wider">
              DEGRADED · AAC COMPRESSED
            </div>
          </>
        )}

        {!isVintage && (
          <>
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
            <div className="absolute bottom-3 left-3 text-[10px] font-mono text-cyber-glow/80 tracking-wider">
              RESTORED · ORIGINAL QUALITY
            </div>
          </>
        )}
      </div>
      <p className="mt-2 text-center text-xs text-white/40 font-medium tracking-wide">
        {label}
      </p>
    </div>
  )
}

function AlgorithmCore({ activeStage, onStageClick, stages }) {
  return (
    <div className="relative flex-shrink-0 w-28 sm:w-36 flex flex-col items-center justify-center gap-1 py-4">
      <div className="absolute inset-y-4 left-1/2 -translate-x-1/2 w-px bg-gradient-to-b from-amber-600/0 via-cyber-blue/40 to-cyber-cyan/0" />

      {stages.slice(0, 6).map((stage, i) => (
        <button
          key={stage.id}
          onClick={() => onStageClick(stage.id)}
          className={`relative z-10 w-10 h-10 rounded-xl flex items-center justify-center text-sm transition-all duration-300 ${
            activeStage === stage.id
              ? 'glass bg-cyber-blue/20 border-cyber-blue/40 scale-110 shadow-[0_0_20px_rgba(0,113,227,0.3)]'
              : 'glass-hover bg-white/[0.04] border-white/[0.06] hover:scale-105'
          }`}
          title={stage.label}
        >
          {stage.icon}
        </button>
      ))}

      <div className="relative w-full h-8 flex items-center justify-center overflow-hidden my-1">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full h-px bg-gradient-to-r from-amber-500/60 via-cyber-blue to-cyber-cyan/60" />
        </div>
        <div className="absolute w-2 h-2 rounded-full bg-cyber-glow shadow-[0_0_12px_#64d2ff] animate-flow" />
      </div>

      {stages.slice(6).map((stage) => (
        <button
          key={stage.id}
          onClick={() => onStageClick(stage.id)}
          className={`relative z-10 w-10 h-10 rounded-xl flex items-center justify-center text-sm transition-all duration-300 ${
            activeStage === stage.id
              ? 'glass bg-cyber-blue/20 border-cyber-blue/40 scale-110'
              : 'glass-hover bg-white/[0.04] border-white/[0.06] hover:scale-105'
          }`}
          title={stage.label}
        >
          {stage.icon}
        </button>
      ))}

      <p className="mt-2 text-[10px] text-white/30 text-center leading-tight">
        tap stages
      </p>
    </div>
  )
}

export default function PipelineAnimation({ stages, activeStage, onStageClick }) {
  const [phase, setPhase] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setPhase((p) => (p + 1) % 100)
    }, 60)
    return () => clearInterval(interval)
  }, [])

  const progress = phase / 100
  const transitionActive = progress > 0.3 && progress < 0.7

  return (
    <div className="wwdc-card relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold tracking-tight">Live Algorithm Flow</h2>
        <span className="text-xs font-mono text-white/40 px-2 py-1 rounded-full glass">
          {transitionActive ? 'PROCESSING' : progress < 0.3 ? 'INPUT' : 'OUTPUT'}
        </span>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        <div
          className="relative flex-1 transition-opacity duration-500"
          style={{ opacity: progress > 0.65 ? 0.3 : 1 }}
        >
          <MediaFrame variant="vintage" label="Legacy Source Video" artifacts />
        </div>

        <AlgorithmCore
          activeStage={activeStage}
          onStageClick={onStageClick}
          stages={stages}
        />

        <div
          className="relative flex-1 transition-opacity duration-500"
          style={{ opacity: progress < 0.35 ? 0.3 : 1 }}
        >
          <MediaFrame variant="restored" label="Restored Output" />
        </div>
      </div>

      {/* Animated light beam overlay */}
      <div
        className="absolute inset-0 pointer-events-none overflow-hidden rounded-3xl"
        aria-hidden="true"
      >
        <div
          className="absolute top-1/2 -translate-y-1/2 h-32 w-24 blur-2xl transition-all duration-100"
          style={{
            left: `${progress * 85 + 5}%`,
            background:
              progress < 0.5
                ? 'radial-gradient(circle, rgba(196,149,106,0.4) 0%, transparent 70%)'
                : 'radial-gradient(circle, rgba(0,113,227,0.5) 0%, transparent 70%)',
          }}
        />
      </div>

      <p className="mt-4 text-center text-sm text-white/50">
        Degraded media enters the pipeline → AI matches album references → optical flow propagates restoration enhancement → restored video emerges
      </p>
    </div>
  )
}
