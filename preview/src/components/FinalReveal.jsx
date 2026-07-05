import { useRef } from 'react'
import { useInView } from '../hooks/useScroll'
import { PROJECT, FEATURES, TECH_STACK } from '../data/pipeline'

function ComparePanel({ variant, label, badge }) {
  const isBefore = variant === 'before'

  return (
    <div
      className={`relative flex-1 rounded-2xl overflow-hidden aspect-video border ${
        isBefore ? 'border-amber-900/30' : 'border-cyber-blue/30'
      }`}
    >
      <div
        className={`absolute inset-0 ${isBefore ? 'vintage-media' : 'restored-media'}`}
        style={{
          background: isBefore
            ? 'linear-gradient(160deg, #1a1008, #4a3728, #2a1810)'
            : 'linear-gradient(160deg, #0a1628, #1a4a6e, #3d5a40, #7a6040)',
        }}
      />
      <div className="absolute inset-0 flex items-end justify-center pb-[20%]">
        <div className={`flex gap-3 items-end ${isBefore ? 'opacity-30 blur-[2px]' : 'opacity-75'}`}>
          <div className="w-8 h-16 rounded-t-full bg-white/20" />
          <div className="w-12 h-24 rounded-t-full bg-white/30" />
          <div className="w-8 h-16 rounded-t-full bg-white/20" />
        </div>
      </div>
      {isBefore && (
        <div className="absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(0,0,0,0.06)_2px,rgba(0,0,0,0.06)_4px)]" />
      )}
      <div className="absolute bottom-3 inset-x-3 flex justify-between items-end">
        <span className={`text-[10px] font-mono tracking-wider ${isBefore ? 'text-amber-500/60' : 'text-cyber-glow/80'}`}>
          {badge}
        </span>
      </div>
      <p className="absolute top-3 left-3 text-xs font-semibold text-white/70">{label}</p>
    </div>
  )
}

export default function FinalReveal() {
  const [ref, inView] = useInView(0.2)

  return (
    <section ref={ref} className="py-24 sm:py-32 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <div
          className="text-center mb-14 transition-all duration-1000"
          style={{
            opacity: inView ? 1 : 0,
            transform: inView ? 'translateY(0)' : 'translateY(32px)',
          }}
        >
          <p className="text-xs font-medium tracking-[0.25em] uppercase text-cyber-glow mb-3">
            Final Output
          </p>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight mb-4">
            Memory, recovered.
          </h2>
          <p className="text-white/50 max-w-xl mx-auto">
            {PROJECT.stats.duration} of source footage · {PROJECT.stats.scenes} scenes ·
            lighting-invariant matching · temporally coherent optical flow reconstruction
          </p>
        </div>

        {/* Before / After */}
        <div
          className="relative flex flex-col sm:flex-row gap-4 sm:gap-0 mb-12 transition-all duration-1000 delay-200"
          style={{
            opacity: inView ? 1 : 0,
            transform: inView ? 'translateY(0) scale(1)' : 'translateY(24px) scale(0.98)',
          }}
        >
          <ComparePanel variant="before" label="Before" badge="DEGRADED · AAC" />
          <div className="hidden sm:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full glass items-center justify-center text-cyber-glow border border-cyber-blue/30 shadow-[0_0_30px_rgba(0,113,227,0.2)]">
            →
          </div>
          <ComparePanel variant="after" label="After" badge="RESTORED · FINAL" />
        </div>

        {/* Stats */}
        <div
          className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12 transition-all duration-1000 delay-300"
          style={{ opacity: inView ? 1 : 0 }}
        >
          {[
            { v: PROJECT.stats.scenes, l: 'Scenes' },
            { v: PROJECT.stats.duration, l: 'Duration' },
            { v: '70/30', l: 'Face/CLIP' },
            { v: '512', l: 'Embed Dim' },
          ].map((s) => (
            <div key={s.l} className="glass rounded-2xl p-5 text-center">
              <p className="text-2xl font-semibold">{s.v}</p>
              <p className="text-[10px] text-white/40 uppercase tracking-wider mt-1">{s.l}</p>
            </div>
          ))}
        </div>

        {/* Features + Stack */}
        <div
          className="grid md:grid-cols-2 gap-6 mb-12 transition-all duration-1000 delay-500"
          style={{ opacity: inView ? 1 : 0, transform: inView ? 'translateY(0)' : 'translateY(20px)' }}
        >
          <div className="glass rounded-3xl p-6 sm:p-8">
            <h3 className="text-lg font-semibold mb-5">Capabilities</h3>
            <ul className="space-y-3">
              {FEATURES.map((f) => (
                <li key={f} className="flex gap-3 text-sm text-white/65">
                  <span className="text-cyber-blue shrink-0">✓</span>
                  {f}
                </li>
              ))}
            </ul>
          </div>
          <div className="glass rounded-3xl p-6 sm:p-8">
            <h3 className="text-lg font-semibold mb-5">Stack</h3>
            <div className="space-y-3">
              {TECH_STACK.map((t) => (
                <div key={t.name} className="flex justify-between items-center py-1.5 border-b border-white/[0.04] last:border-0">
                  <span className="text-sm text-white/80">{t.name}</span>
                  <span className="text-[11px] text-white/35">{t.role}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <a
            href="https://github.com/vivekcyr25/AI-Video-Restoration-Pipeline"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-cyber-blue hover:bg-[#0077ED] text-white text-sm font-medium transition-colors shadow-[0_0_40px_rgba(0,113,227,0.25)]"
          >
            Explore the Source →
          </a>
        </div>
      </div>
    </section>
  )
}
