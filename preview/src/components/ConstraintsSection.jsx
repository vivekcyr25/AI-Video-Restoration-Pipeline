import { ENGINEERING_CONSTRAINTS } from '../data/pipelineData'

export default function ConstraintsSection() {
  return (
    <section id="constraints" className="py-24 px-4 sm:px-6 relative bg-[#05060b] border-t border-white/[0.06]">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            SYSTEM DESIGN & PROFILING
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            Engineering Under Constraints
          </h2>
          <p className="text-sm sm:text-base text-slate-400 font-light leading-relaxed">
            Real optimizations engineered to run research-grade computer vision models reliably on consumer hardware without memory leaks or synchronization bottlenecks.
          </p>
        </div>

        {/* Problem -> Optimization -> Result Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          {ENGINEERING_CONSTRAINTS.map((item) => (
            <div
              key={item.id}
              className="rounded-3xl p-6 sm:p-8 bg-[#07090f] border border-white/[0.08] hover:border-white/[0.16] transition-all duration-300 shadow-xl space-y-5"
            >
              {/* Card Title */}
              <div className="pb-3 border-b border-white/[0.08] flex items-center justify-between">
                <h3 className="text-lg font-bold text-white font-display">
                  {item.title}
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.06] text-slate-400">
                  OPTIMIZED
                </span>
              </div>

              {/* Problem */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-mono uppercase tracking-wider text-rose-400 font-semibold flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                  PROBLEM
                </span>
                <p className="text-xs sm:text-sm text-slate-400 font-light leading-relaxed">
                  {item.problem}
                </p>
              </div>

              {/* Optimization */}
              <div className="space-y-1.5 p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                <span className="text-[10px] font-mono uppercase tracking-wider text-electric-cyan font-semibold flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-electric-cyan" />
                  OPTIMIZATION
                </span>
                <p className="text-xs text-slate-300 font-light leading-relaxed">
                  {item.optimization}
                </p>
              </div>

              {/* Result */}
              <div className="space-y-1.5 p-3.5 rounded-xl bg-emerald-500/[0.04] border border-emerald-500/20">
                <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-semibold flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  MEASURED RESULT
                </span>
                <p className="text-xs text-emerald-300/90 font-medium leading-relaxed font-mono">
                  {item.result}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
