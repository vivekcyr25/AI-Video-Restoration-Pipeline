export default function TestingSection() {
  const testSuites = [
    { name: 'test_reinhard_color_transfer', desc: 'Validates Lab color distribution mean/std matching and channel bounds', status: 'PASSED' },
    { name: 'test_affine_landmark_alignment', desc: 'Ensures sub-pixel 5-point facial landmark warping accuracy (< 0.8px)', status: 'PASSED' },
    { name: 'test_clip_embedding_normalization', desc: 'Verifies L2 unit-norm [N, 512] vectors and cosine similarity bounds', status: 'PASSED' },
    { name: 'test_temporal_ema_deflicker', desc: 'Tests rolling luminance exponential moving average across video shots', status: 'PASSED' },
    { name: 'test_raft_coordinate_cache', desc: 'Checks GPU grid tensor allocation elimination and warp flow fidelity', status: 'PASSED' },
    { name: 'test_audio_stream_sync', desc: 'Validates PTS timestamp preservation and AAC direct stream copy', status: 'PASSED' },
  ]

  return (
    <section id="testing" className="py-24 px-4 sm:px-6 relative bg-[#040407] border-t border-white/[0.06]">
      <div className="max-w-5xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-14 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-emerald-400 font-semibold">
            AUTOMATED REGRESSION VERIFICATION
          </p>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-display uppercase">
            Built To Be Verified
          </h2>
          <p className="text-sm text-slate-400 font-light">
            Every computer vision and temporal enhancement algorithm is guarded by a comprehensive automated test suite.
          </p>
        </div>

        {/* Big Impact Numbers Banner */}
        <div className="p-8 sm:p-10 rounded-3xl bg-gradient-to-r from-emerald-950/30 via-slate-900/40 to-emerald-950/30 border border-emerald-500/30 shadow-2xl backdrop-blur-xl mb-8 flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
          <div className="space-y-1">
            <span className="text-xs font-mono text-emerald-400 uppercase tracking-widest font-semibold">
              PYTEST SUITE PASS RATE
            </span>
            <p className="text-5xl sm:text-6xl font-extrabold text-white font-display tracking-tight">
              95 <span className="text-emerald-400 text-3xl sm:text-4xl">/ 95</span>
            </p>
            <p className="text-xs font-mono text-slate-400">
              0 Failed · 0 Warnings · 100% Assertion Coverage
            </p>
          </div>

          <div className="px-6 py-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-300 font-mono text-xs font-semibold">
            ✓ ALL SUITES PASSING
          </div>
        </div>

        {/* Test Suites List */}
        <div className="rounded-2xl border border-white/[0.08] bg-[#07090e] divide-y divide-white/[0.04] overflow-hidden">
          {testSuites.map((suite) => (
            <div key={suite.name} className="p-4 sm:px-6 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-white/[0.02] transition-colors">
              <div className="space-y-0.5">
                <p className="text-xs sm:text-sm font-mono font-semibold text-slate-200">
                  {suite.name}
                </p>
                <p className="text-xs text-slate-400 font-light">
                  {suite.desc}
                </p>
              </div>
              <span className="self-start sm:self-auto text-[11px] font-mono px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                {suite.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
