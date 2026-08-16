import { KEY_METRICS } from '../data/pipelineData'

export default function MetricsSection() {
  return (
    <section className="py-20 px-4 sm:px-6 relative border-y border-white/[0.06] bg-[#040407]">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-14 space-y-2">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            ENGINEERING SPECIFICATIONS
          </p>
          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white font-display uppercase">
            Measured System Impact
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 font-light">
            Real performance parameters measured across 180,000 frames of legacy media restoration.
          </p>
        </div>

        {/* Editorial Large Number Grid with Minimal Dividers */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 divide-y sm:divide-y-0 sm:divide-x divide-white/[0.08] border border-white/[0.08] rounded-3xl bg-white/[0.02] backdrop-blur-xl">
          {KEY_METRICS.map((metric, i) => (
            <div key={metric.label} className="p-8 text-left space-y-3 group hover:bg-white/[0.03] transition-colors">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">
                METRIC_0{i + 1}
              </span>
              <p className="text-4xl xl:text-5xl font-extrabold text-white font-display tracking-tight group-hover:text-electric-cyan transition-colors">
                {metric.value}
              </p>
              <div>
                <h3 className="text-sm font-semibold text-slate-200 font-display">
                  {metric.label}
                </h3>
                <p className="text-xs text-slate-400 font-light mt-1 leading-snug">
                  {metric.detail}
                </p>
              </div>
              <p className="text-[11px] font-mono text-slate-500 pt-2 border-t border-white/[0.04]">
                {metric.sub}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
