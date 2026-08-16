import { PIPELINE_STAGES } from '../data/pipelineData'

export default function StageModal({ activeStageId, onClose, onSelectStage }) {
  const stage = PIPELINE_STAGES.find((s) => s.id === activeStageId)
  if (!stage) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md animate-[fadeIn_0.2s_ease-out]"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl bg-[#080a10] border border-white/[0.14] rounded-3xl p-6 sm:p-8 shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
      >
        {/* Glow accent */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-electric-cyan/10 blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="flex items-start justify-between gap-4 pb-6 border-b border-white/[0.08]">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/[0.04] border border-white/10 flex items-center justify-center text-2xl shadow-inner">
              {stage.icon}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-electric-cyan uppercase tracking-widest font-semibold">
                  STAGE {stage.number}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.06] text-slate-400 font-mono">
                  {stage.tag}
                </span>
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-white font-display mt-0.5">
                {stage.name}
              </h3>
              <p className="text-xs font-mono text-slate-400 mt-1">
                Engine: <span className="text-slate-200">{stage.tool}</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-white/[0.06] hover:bg-white/[0.12] border border-white/10 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
            aria-label="Close dialog"
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <div className="py-6 space-y-6">
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">
              Engineering Rationale
            </h4>
            <p className="text-sm text-slate-300 font-light leading-relaxed">
              {stage.description}
            </p>
          </div>

          {/* Technical Specs List */}
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-2">
            <h4 className="text-xs font-mono uppercase tracking-wider text-electric-cyan mb-2">
              Key Technical Implementations
            </h4>
            <ul className="space-y-2">
              {stage.techDetails.map((detail, idx) => (
                <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                  <span className="text-electric-cyan shrink-0 mt-0.5">▸</span>
                  <span>{detail}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Inputs and Outputs */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1.5">
                Inputs
              </span>
              <div className="space-y-1">
                {stage.inputs.map((inp, idx) => (
                  <div key={idx} className="text-xs font-mono text-slate-300 truncate">
                    • {inp}
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
              <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 block mb-1.5">
                Output Artifacts
              </span>
              <div className="space-y-1">
                {stage.outputs.map((out, idx) => (
                  <div key={idx} className="text-xs font-mono text-slate-300 truncate">
                    → {out}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Command execution wrapper */}
          <div className="p-3.5 rounded-xl bg-[#030407] border border-white/[0.08]">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block mb-1">
              CLI Execution Runner
            </span>
            <code className="text-xs font-mono text-electric-cyan block truncate">
              {stage.cli}
            </code>
          </div>
        </div>

        {/* Footer / Navigation among stages */}
        <div className="pt-4 border-t border-white/[0.08] flex items-center justify-between">
          <div className="flex gap-1.5 overflow-x-auto py-1">
            {PIPELINE_STAGES.map((s) => (
              <button
                key={s.id}
                onClick={() => onSelectStage(s.id)}
                className={`w-8 h-8 rounded-lg text-xs font-mono transition-all ${
                  s.id === activeStageId
                    ? 'bg-electric-cyan text-[#040407] font-bold shadow-cyan-glow'
                    : 'bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]'
                }`}
              >
                {s.number}
              </button>
            ))}
          </div>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-xs font-medium text-slate-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
