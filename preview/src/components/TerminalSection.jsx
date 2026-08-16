import { useState } from 'react'
import { TERMINAL_LOGS } from '../data/pipelineData'

export default function TerminalSection() {
  const [activeTab, setActiveTab] = useState('pipeline')
  const [copied, setCopied] = useState(false)

  const logs = TERMINAL_LOGS[activeTab] || TERMINAL_LOGS.pipeline

  const copyCommand = () => {
    const cmd = logs[0]?.text?.replace('$ ', '') || 'python scripts/run_pipeline.py --stage all'
    navigator.clipboard.writeText(cmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section id="terminal" className="py-24 px-4 sm:px-6 relative bg-[#040407] border-t border-white/[0.06]">
      <div className="max-w-5xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-14 space-y-3">
          <p className="text-xs font-mono tracking-[0.25em] uppercase text-electric-cyan font-semibold">
            DEVELOPER TELEMETRY & EXECUTION
          </p>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white font-display uppercase">
            Engineering Terminal
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 font-light">
            Stylized visualization of the actual pipeline manager execution, Pytest suite, and top-K vector matching.
          </p>
        </div>

        {/* Terminal Window Frame */}
        <div className="rounded-2xl border border-white/[0.12] bg-[#07090e] shadow-2xl overflow-hidden backdrop-blur-2xl">
          {/* Top Window Bar */}
          <div className="px-4 py-3 bg-[#0a0d14] border-b border-white/[0.08] flex items-center justify-between">
            {/* Window Dots */}
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-500/80" />
              <span className="w-3 h-3 rounded-full bg-amber-500/80" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
              <span className="ml-2 text-[11px] font-mono text-slate-400 hidden sm:inline">
                bash — wedding_ai_pipeline (RTX 3050 CUDA)
              </span>
            </div>

            {/* Command Tabs */}
            <div className="flex items-center gap-1 bg-black/40 p-1 rounded-lg border border-white/[0.06]">
              <button
                onClick={() => setActiveTab('pipeline')}
                className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                  activeTab === 'pipeline'
                    ? 'bg-electric-cyan/20 text-electric-cyan font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                run_pipeline.py
              </button>
              <button
                onClick={() => setActiveTab('pytest')}
                className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                  activeTab === 'pytest'
                    ? 'bg-emerald-500/20 text-emerald-400 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                pytest (95 tests)
              </button>
              <button
                onClick={() => setActiveTab('matcher')}
                className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                  activeTab === 'matcher'
                    ? 'bg-violet-subtle/20 text-violet-glow font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                advanced_matcher.py
              </button>
            </div>

            {/* Copy Command Button */}
            <button
              onClick={copyCommand}
              className="px-2.5 py-1 rounded-md bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-[11px] font-mono text-slate-300 hover:text-white transition-colors"
            >
              {copied ? '✓ Copied' : 'Copy CLI'}
            </button>
          </div>

          {/* Terminal Output Area */}
          <div className="p-6 font-mono text-xs sm:text-[13px] leading-relaxed space-y-2 select-text overflow-x-auto min-h-[300px] bg-[#05070c]">
            {logs.map((line, idx) => (
              <div key={idx} className={`${line.color} flex items-start gap-2`}>
                <span className="select-none text-slate-600 shrink-0">
                  {String(idx + 1).padStart(2, '0')}
                </span>
                <span className="break-all">{line.text}</span>
              </div>
            ))}

            {/* Blinking Cursor */}
            <div className="flex items-center gap-2 pt-2 text-electric-cyan">
              <span className="select-none text-slate-600 shrink-0">
                {String(logs.length + 1).padStart(2, '0')}
              </span>
              <span>❯</span>
              <span className="w-2 h-4 bg-electric-cyan animate-pulse inline-block" />
            </div>
          </div>

          {/* Bottom Terminal Status Footer */}
          <div className="px-4 py-2 bg-[#0a0d14] border-t border-white/[0.06] flex items-center justify-between text-[11px] font-mono text-slate-400">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                EXECUTION NOMINAL
              </span>
              <span className="text-slate-600">|</span>
              <span>Memory Footprint: <span className="text-slate-300">3.42 GB / 4.00 GB</span></span>
            </div>
            <span className="text-slate-500">Python 3.10 · CUDA 12.1</span>
          </div>
        </div>
      </div>
    </section>
  )
}
