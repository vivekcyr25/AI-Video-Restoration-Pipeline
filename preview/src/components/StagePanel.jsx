import { STAGES } from '../data/pipeline'

export default function StagePanel({ activeStage, onClose, onStageSelect }) {
  const stage = STAGES.find((s) => s.id === activeStage)
  if (!stage) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 sm:p-6"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      <div
        className="relative w-full max-w-lg glass rounded-3xl p-6 sm:p-8 animate-[slideUp_0.3s_ease-out] border border-white/10 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="stage-title"
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 rounded-full glass-hover flex items-center justify-center text-white/60 hover:text-white text-sm"
          aria-label="Close"
        >
          ✕
        </button>

        <div className="flex items-start gap-4 mb-5">
          <div
            className={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl bg-gradient-to-br ${stage.color} border border-white/10`}
          >
            {stage.icon}
          </div>
          <div>
            <p className="text-xs font-mono text-cyber-blue uppercase tracking-widest mb-1">
              Stage {stage.id} · {stage.tool}
            </p>
            <h3 id="stage-title" className="text-xl font-semibold tracking-tight">
              {stage.label}
            </h3>
          </div>
        </div>

        <p className="text-white/80 leading-relaxed mb-4">{stage.description}</p>

        <div className="glass rounded-2xl p-4 mb-4">
          <p className="text-xs font-mono text-white/40 uppercase tracking-wider mb-2">
            How it works
          </p>
          <p className="text-sm text-white/70 leading-relaxed">{stage.detail}</p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-white/40">
          <span className="px-2 py-1 rounded-lg bg-white/[0.06]">→ {stage.output}</span>
        </div>

        <div className="flex gap-2 mt-5">
          {STAGES.map((s) => (
            <button
              key={s.id}
              onClick={() => onStageSelect(s.id)}
              className={`flex-1 h-1 rounded-full transition-all duration-300 ${
                s.id === activeStage ? 'bg-cyber-blue' : 'bg-white/10 hover:bg-white/20'
              }`}
              aria-label={`Go to stage ${s.id}`}
            />
          ))}
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
