import { useState } from 'react'
import ShaderBackground from './components/ShaderBackground'
import PipelineAnimation from './components/PipelineAnimation'
import StagePanel from './components/StagePanel'
import { PROJECT, STAGES, TECH_STACK, FEATURES } from './data/pipeline'

export default function App() {
  const [activeStage, setActiveStage] = useState(null)
  const [shaderProgress, setShaderProgress] = useState(0.35)

  const handleStageClick = (id) => {
    setActiveStage(id)
    setShaderProgress(Math.min(0.35 + id * 0.08, 0.95))
  }

  const handleStageSelect = (id) => {
    setActiveStage(id)
    setShaderProgress(Math.min(0.35 + id * 0.08, 0.95))
  }

  return (
    <div className="min-h-screen relative">
      <ShaderBackground progress={shaderProgress} />

      {/* Top nav — WWDC-style */}
      <nav className="fixed top-0 inset-x-0 z-40 glass border-b border-white/[0.06]">
        <div className="max-w-6xl mx-auto px-5 h-12 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🎬</span>
            <span className="text-sm font-semibold tracking-tight hidden sm:inline">
              AI Video Restoration
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs text-white/50">
            <a
              href="https://github.com/vivekcyr25/AI-Video-Restoration-Pipeline"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              GitHub
            </a>
            <span className="px-2 py-0.5 rounded-full bg-cyber-blue/20 text-cyber-glow text-[10px] font-medium">
              Algorithm Preview
            </span>
          </div>
        </div>
      </nav>

      <main className="relative pt-20 pb-16 px-4 sm:px-6 max-w-6xl mx-auto">
        {/* Hero */}
        <header className="text-center mb-12 sm:mb-16">
          <p className="text-xs font-mono text-cyber-blue uppercase tracking-[0.2em] mb-4 animate-pulse-soft">
            Scene-Aware · AI-Driven · Optical Flow
          </p>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight mb-4 bg-gradient-to-r from-amber-200 via-white to-cyber-glow bg-clip-text text-transparent">
            {PROJECT.name}
          </h1>
          <p className="text-lg sm:text-xl text-white/60 max-w-2xl mx-auto leading-relaxed font-light">
            {PROJECT.tagline}
          </p>
          <blockquote className="mt-6 text-sm text-white/40 italic max-w-xl mx-auto border-l-2 border-amber-600/40 pl-4 text-left sm:text-center sm:border-l-0 sm:pl-0">
            "{PROJECT.question}"
          </blockquote>
        </header>

        {/* Stats bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
          {[
            { value: PROJECT.stats.scenes, label: 'Scenes Detected' },
            { value: PROJECT.stats.duration, label: 'Video Duration' },
            { value: `${PROJECT.stats.faceWeight * 100}%`, label: 'Face Weight' },
            { value: PROJECT.stats.embeddingDim, label: 'Embedding Dim' },
          ].map((stat) => (
            <div key={stat.label} className="glass rounded-2xl p-4 text-center glass-hover">
              <p className="text-2xl font-semibold text-white">{stat.value}</p>
              <p className="text-[11px] text-white/40 mt-1 uppercase tracking-wider">
                {stat.label}
              </p>
            </div>
          ))}
        </div>

        {/* Main animation */}
        <section className="mb-12">
          <PipelineAnimation
            stages={STAGES}
            activeStage={activeStage}
            onStageClick={handleStageClick}
          />
        </section>

        {/* Pipeline stages grid — clickable */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-2 tracking-tight">8-Stage Pipeline</h2>
          <p className="text-sm text-white/50 mb-6">
            Click any stage to learn how the algorithm processes your media
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {STAGES.map((stage) => (
              <button
                key={stage.id}
                onClick={() => handleStageClick(stage.id)}
                className={`glass rounded-2xl p-4 text-left glass-hover group transition-all duration-300 ${
                  activeStage === stage.id
                    ? 'ring-1 ring-cyber-blue/50 bg-white/[0.08]'
                    : ''
                }`}
              >
                <span className="text-2xl mb-2 block group-hover:scale-110 transition-transform">
                  {stage.icon}
                </span>
                <p className="text-xs font-mono text-white/40 mb-1">Stage {stage.id}</p>
                <p className="text-sm font-medium text-white/90">{stage.label}</p>
                <p className="text-[11px] text-white/40 mt-1 truncate">{stage.tool}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Features + Tech */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="wwdc-card">
            <h3 className="text-lg font-semibold mb-4 tracking-tight">Key Features</h3>
            <ul className="space-y-3">
              {FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-3 text-sm text-white/70">
                  <span className="text-cyber-blue mt-0.5">●</span>
                  {f}
                </li>
              ))}
            </ul>
          </div>

          <div className="wwdc-card">
            <h3 className="text-lg font-semibold mb-4 tracking-tight">Technology Stack</h3>
            <div className="space-y-2">
              {TECH_STACK.map((t) => (
                <div
                  key={t.name}
                  className="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0"
                >
                  <span className="text-sm font-medium text-white/80">{t.name}</span>
                  <span className="text-[11px] text-white/40">{t.role}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Insight callout */}
        <section className="wwdc-card text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-amber-900/10 via-transparent to-cyber-blue/10 pointer-events-none" />
          <p className="text-sm font-mono text-amber-400/80 uppercase tracking-widest mb-3">
            Core Insight
          </p>
          <p className="text-lg sm:text-xl text-white/80 max-w-2xl mx-auto leading-relaxed">
            Wedding photographers capture the same moments at full quality. Match video frames to
            album photos with{' '}
            <span className="text-cyber-glow">CLIP semantics</span> +{' '}
            <span className="text-cyber-glow">face identity</span>, then propagate enhancement
            across every frame via optical flow.
          </p>
          <a
            href="https://github.com/vivekcyr25/AI-Video-Restoration-Pipeline"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 mt-6 px-5 py-2.5 rounded-full bg-cyber-blue hover:bg-cyber-blue/90 text-white text-sm font-medium transition-colors"
          >
            View Source on GitHub →
          </a>
        </section>
      </main>

      <footer className="text-center py-8 text-xs text-white/30 border-t border-white/[0.04]">
        MIT License · Made to preserve irreplaceable memories
      </footer>

      {activeStage && (
        <StagePanel
          activeStage={activeStage}
          onClose={() => setActiveStage(null)}
          onStageSelect={handleStageSelect}
        />
      )}
    </div>
  )
}
