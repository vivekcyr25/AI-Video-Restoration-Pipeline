import { useRef, useEffect } from 'react'

const VERTEX = `
  attribute vec2 a_position;
  void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`

const FRAGMENT = `
  precision highp float;
  uniform float u_time;
  uniform vec2 u_resolution;
  uniform vec2 u_mouse;
  uniform float u_blur;

  // High-precision fast hash & noise
  float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
      mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
      f.y
    );
  }

  mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
  }

  float fbm(vec2 p) {
    float v = 0.0;
    float amp = 0.5;
    mat2 r = rot(0.5);
    for (int i = 0; i < 4; i++) {
      v += amp * noise(p);
      p = r * p * 2.04 + vec2(0.12, 0.34);
      amp *= 0.48;
    }
    return v;
  }

  void main() {
    vec2 p = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.12;

    // Pitch black deep void base
    vec3 color = vec3(0.012, 0.012, 0.018);

    // ── Phase 1: "The Fading Memory" (Dissolving Fog & Disintegrating Dust) ──
    vec2 fadeUv = p * 1.5 + vec2(sin(t * 0.4) * 0.2, cos(t * 0.3) * 0.15);
    float fadeMist = fbm(fadeUv + vec2(t * 0.12, -t * 0.07));
    
    float particleNoise = noise(p * 16.0 + vec2(t * 0.35, t * 0.18));
    float disintegrate = smoothstep(0.70, 0.95, particleNoise) * smoothstep(0.35, 0.7, fadeMist);
    vec3 amberFade = vec3(0.14, 0.07, 0.02) * disintegrate * 0.45;

    // ── Phase 2: "The AI Recovery Stream" (Coalescing Luminescent Ribbons) ──
    vec2 q = vec2(fbm(p * 1.9 + vec2(0.0, t * 0.25)), fbm(p * 2.0 + vec2(t * 0.18, 0.0)));
    vec2 r = vec2(fbm(p * 2.4 + 3.2 * q + vec2(1.7, 9.2) + 0.12 * t),
                  fbm(p * 2.2 + 3.2 * q + vec2(8.3, 2.8) + 0.10 * t));
    
    float recoveryWave = fbm(p * 1.6 + 2.8 * r);
    
    // Dynamic sharpness modulation on scroll
    float sharp1 = mix(14.0, 5.0, u_blur);
    float sharp2 = mix(18.0, 6.0, u_blur);
    float energyBand1 = exp(-pow((recoveryWave - 0.48) * sharp1, 2.0));
    float energyBand2 = exp(-pow((recoveryWave - 0.62) * sharp2, 2.0));
    float energyGlow  = exp(-pow((recoveryWave - 0.55) * 4.0, 2.0));

    // Electric Cyan & Spectral Violet
    vec3 cyanLaser   = vec3(0.0, 0.94, 1.0) * energyBand1 * 0.16;
    vec3 violetAura  = vec3(0.66, 0.33, 0.98) * energyBand2 * 0.14;
    vec3 deepEther   = vec3(0.02, 0.12, 0.24) * energyGlow * 0.12;

    // ── Phase 3: "Recovered Star-Sparks" (High-Frequency Clustered Landmarks) ──
    vec2 gridP = fract(p * 10.0 + vec2(sin(t * 0.5), cos(t * 0.3)) * 0.5) - 0.5;
    float sparks = exp(-length(gridP) * 32.0) * smoothstep(0.5, 0.8, recoveryWave);
    vec3 sparkColor = vec3(0.4, 0.9, 1.0) * sparks * (0.25 * (1.0 - u_blur * 0.4));

    // ── Phase 4: Gentle Mouse Interaction Aura ──
    vec2 mouseNorm = (u_mouse - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float mouseDist = length(p - mouseNorm);
    float mouseGlow = exp(-mouseDist * 3.2) * 0.07;
    vec3 interactiveGlow = vec3(0.0, 0.75, 1.0) * mouseGlow;

    // Composite
    color += amberFade;
    color += cyanLaser;
    color += violetAura;
    color += deepEther;
    color += sparkColor;
    color += interactiveGlow;

    // Edge vignette
    float vignette = smoothstep(1.4, 0.25, length(p));
    color *= vignette;

    gl_FragColor = vec4(color, 1.0);
  }
`

export default function ShaderBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const gl = canvas.getContext('webgl', {
      powerPreference: 'high-performance',
      alpha: false,
      antialias: false,
    })
    if (!gl) return

    function createShader(type, source) {
      const shader = gl.createShader(type)
      gl.shaderSource(shader, source)
      gl.compileShader(shader)
      return shader
    }

    const program = gl.createProgram()
    gl.attachShader(program, createShader(gl.VERTEX_SHADER, VERTEX))
    gl.attachShader(program, createShader(gl.FRAGMENT_SHADER, FRAGMENT))
    gl.linkProgram(program)
    gl.useProgram(program)

    const buffer = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
      gl.STATIC_DRAW
    )

    const posAttr = gl.getAttribLocation(program, 'a_position')
    gl.enableVertexAttribArray(posAttr)
    gl.vertexAttribPointer(posAttr, 2, gl.FLOAT, false, 0, 0)

    const uTime = gl.getUniformLocation(program, 'u_time')
    const uRes = gl.getUniformLocation(program, 'u_resolution')
    const uMouse = gl.getUniformLocation(program, 'u_mouse')
    const uBlur = gl.getUniformLocation(program, 'u_blur')

    let targetMouse = [window.innerWidth * 0.5, window.innerHeight * 0.5]
    let currentMouse = [window.innerWidth * 0.5, window.innerHeight * 0.5]
    let targetBlur = 0
    let currentBlur = 0

    const handleMouseMove = (e) => {
      targetMouse = [e.clientX, window.innerHeight - e.clientY]
    }

    const handleScroll = () => {
      const sy = window.scrollY || 0
      targetBlur = Math.min(1.0, Math.max(0.0, (sy - 80) / 450))
    }

    window.addEventListener('mousemove', handleMouseMove, { passive: true })
    window.addEventListener('scroll', handleScroll, { passive: true })

    function resize() {
      if (!canvas) return
      const dpr = Math.min(window.devicePixelRatio || 1, 1.25)
      canvas.width = Math.floor(window.innerWidth * dpr)
      canvas.height = Math.floor(window.innerHeight * dpr)
      gl.viewport(0, 0, canvas.width, canvas.height)
      gl.uniform2f(uRes, canvas.width, canvas.height)
    }

    window.addEventListener('resize', resize)
    resize()

    let animId
    const startTime = performance.now()

    function render(now) {
      const elapsed = (now - startTime) * 0.001
      const dpr = Math.min(window.devicePixelRatio || 1, 1.25)

      currentMouse[0] += (targetMouse[0] * dpr - currentMouse[0]) * 0.05
      currentMouse[1] += (targetMouse[1] * dpr - currentMouse[1]) * 0.05
      currentBlur += (targetBlur - currentBlur) * 0.06

      gl.uniform1f(uTime, elapsed)
      gl.uniform2f(uMouse, currentMouse[0], currentMouse[1])
      gl.uniform1f(uBlur, currentBlur)

      gl.drawArrays(gl.TRIANGLES, 0, 6)
      animId = requestAnimationFrame(render)
    }

    animId = requestAnimationFrame(render)

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('scroll', handleScroll)
      gl.deleteProgram(program)
      gl.deleteBuffer(buffer)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: '#010103',
        opacity: 0.95,
      }}
    />
  )
}
