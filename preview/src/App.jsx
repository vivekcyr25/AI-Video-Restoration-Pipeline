import { useState } from 'react'
import ShaderBackground from './components/ShaderBackground'
import IntroSequence from './components/IntroSequence'
import ScrollWorkflow from './components/ScrollWorkflow'
import FinalReveal from './components/FinalReveal'
import StagePanel from './components/StagePanel'
import { useGlobalScroll } from './hooks/useScroll'

export default function App() {
  const [activeStage, setActiveStage] = useState(null)
  const [introProgress, setIntroProgress] = useState(0)
  const { scrollProgress } = useGlobalScroll()

  const shaderProgress = Math.min(1, introProgress * 0.6 + scrollProgress * 0.5)

  const navOpaque = scrollProgress > 0.02

  return (
    <div className="relative">
      <ShaderBackground progress={shaderProgress} />

      {/* Nav — fades in after first scroll */}
      <nav
        className={`fixed top-0 inset-x-0 z-40 transition-all duration-500 ${
          navOpaque ? 'glass border-b border-white/[0.06]' : 'bg-transparent border-transparent'
        }`}
      >
        <div className="max-w-6xl mx-auto px-5 h-12 flex items-center justify-between">
          <span className="text-sm font-semibold tracking-tight text-white/80">
            AI Video Restoration
          </span>
          <div className="flex items-center gap-4 text-xs text-white/45">
            <a
              href="https://github.com/vivekcyr25/AI-Video-Restoration-Pipeline"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Act 1: Apple-style problem → solution intro */}
      <IntroSequence onProgress={setIntroProgress} />

      {/* Act 2: Scroll-driven connected workflow */}
      <ScrollWorkflow onStageClick={setActiveStage} />

      {/* Act 3: Final reveal */}
      <FinalReveal />

      <footer className="text-center py-10 text-xs text-white/25 border-t border-white/[0.04]">
        MIT License · Preserving irreplaceable memories through AI
      </footer>

      {activeStage && (
        <StagePanel
          activeStage={activeStage}
          onClose={() => setActiveStage(null)}
          onStageSelect={setActiveStage}
        />
      )}
    </div>
  )
}
