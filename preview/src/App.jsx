import { useState, useEffect } from 'react'
import SplashIntro from './components/SplashIntro'
import ShaderBackground from './components/ShaderBackground'
import BackgroundAudio from './components/BackgroundAudio'
import Navbar from './components/Navbar'
import HeroSection from './components/HeroSection'
import BeforeAfterSection from './components/BeforeAfterSection'
import MetricsSection from './components/MetricsSection'
import PipelineWorkflow from './components/PipelineWorkflow'
import AlbumMatchingSection from './components/AlbumMatchingSection'
import RestorationShowcase from './components/RestorationShowcase'
import TerminalSection from './components/TerminalSection'
import ArchitectureDiagram from './components/ArchitectureDiagram'
import TechStackSection from './components/TechStackSection'
import ConstraintsSection from './components/ConstraintsSection'
import TestingSection from './components/TestingSection'
import ProjectStory from './components/ProjectStory'
import ProjectTimeline from './components/ProjectTimeline'
import GithubCTA from './components/GithubCTA'
import Footer from './components/Footer'
import StageModal from './components/StageModal'

export default function App() {
  const [activeStageId, setActiveStageId] = useState(null)
  const [introComplete, setIntroComplete] = useState(false)
  const [siteVisible, setSiteVisible] = useState(false)

  const handleIntroDone = () => {
    setIntroComplete(true)
    setTimeout(() => setSiteVisible(true), 100)
  }

  // Auto-attach scroll stretch-reveal system to all text elements & cards
  useEffect(() => {
    if (!siteVisible) return

    // Find all key text headings, paragraphs, labels, and card containers
    const elements = document.querySelectorAll(
      'section h1, section h2, section h3, section p, section .grid > div, footer'
    )

    elements.forEach((el, index) => {
      if (el.tagName.startsWith('H') || el.tagName === 'P') {
        el.classList.add('stretch-reveal')
      } else {
        el.classList.add('stretch-card')
      }
      // Add subtle stagger delay
      const delay = (index % 6) * 0.06
      el.style.transitionDelay = `${delay}s`
    })

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed')
          }
        })
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px',
      }
    )

    elements.forEach((el) => observer.observe(el))

    return () => observer.disconnect()
  }, [siteVisible])

  return (
    <>
      {/* ── Cinematic Splash Intro ── */}
      {!introComplete && <SplashIntro onDone={handleIntroDone} />}

      {/* ── Main Site (fades in after intro) ── */}
      <div
        className="relative min-h-screen bg-[#040407] text-slate-100"
        style={{
          opacity: siteVisible ? 1 : 0,
          transition: 'opacity 0.8s ease',
          pointerEvents: siteVisible ? 'auto' : 'none',
        }}
      >
        {/* Background WebGL Shader Canvas */}
        <ShaderBackground progress={0.7} />

        {/* Ambient Audio Controller */}
        <BackgroundAudio />

        {/* Global Navbar */}
        <Navbar onOpenStage={(id) => setActiveStageId(id)} />

        {/* 1. Cinematic Hero Section */}
        <HeroSection />

        {/* 2. Before / After Interactive Slider */}
        <BeforeAfterSection />

        {/* 3. Project Impact / Real Number Metrics */}
        <MetricsSection />

        {/* 4. Interactive 8-Stage Pipeline Workflow */}
        <PipelineWorkflow onStageClick={(id) => setActiveStageId(id)} />

        {/* 5. Album ↔ Video Semantic Matching */}
        <AlbumMatchingSection />

        {/* 6. AI Restoration Detail Recovery Breakdown */}
        <RestorationShowcase />

        {/* 7. Engineering Developer Terminal */}
        <TerminalSection />

        {/* 8. System Architecture Diagram */}
        <ArchitectureDiagram />

        {/* 9. Verified Tech Stack */}
        <TechStackSection />

        {/* 10. Engineering Under Constraints */}
        <ConstraintsSection />

        {/* 11. Built To Be Verified: Automated Testing */}
        <TestingSection />

        {/* 12. Project Narrative: Why I Built This */}
        <ProjectStory />

        {/* 13. Pipeline Evolution Timeline */}
        <ProjectTimeline />

        {/* 14. Final Call to Action */}
        <GithubCTA />

        {/* 15. Minimalist Engineering Footer */}
        <Footer />

        {/* Deep-Dive Stage Inspector Modal */}
        {activeStageId && (
          <StageModal
            activeStageId={activeStageId}
            onClose={() => setActiveStageId(null)}
            onSelectStage={(id) => setActiveStageId(id)}
          />
        )}
      </div>
    </>
  )
}
