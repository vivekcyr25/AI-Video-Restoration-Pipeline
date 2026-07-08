import { useRef, useEffect } from 'react'

const VERTEX = `
  attribute vec2 a_position;
  void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`

const FRAGMENT = `
  precision mediump float;
  uniform float u_time;
  uniform vec2 u_resolution;
  uniform float u_progress;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
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

  float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    for (int i = 0; i < 4; i++) {
      v += a * noise(p);
      p *= 2.1;
      a *= 0.5;
    }
    return v;
  }

  void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;
    float t = u_time * 0.25;

    float vintageMix = 1.0 - smoothstep(0.08, 0.45, u_progress);

    vec3 deepSpace = vec3(0.01, 0.02, 0.06);
    vec3 aiBlue = vec3(0.02, 0.06, 0.14);
    vec3 vintageWarm = vec3(0.06, 0.03, 0.02);
    vec3 base = mix(aiBlue, vintageWarm, vintageMix * 0.7);
    base = mix(base, deepSpace, 0.3);

    float n = fbm(uv * 3.0 + t * 0.1) * 0.04;
    base += n;

    float gridX = smoothstep(0.992, 1.0, fract(uv.x * 30.0 + t * 0.02));
    float gridY = smoothstep(0.992, 1.0, fract(uv.y * 30.0 - t * 0.015));
    float grid = (gridX + gridY) * 0.04 * (1.0 - vintageMix * 0.5);
    base += vec3(0.0, 0.35, 0.65) * grid;

    for (float i = 0.0; i < 5.0; i++) {
      float y = fract(i * 0.21 + t * (0.04 + i * 0.008));
      float stream = exp(-pow((uv.y - y) * 12.0, 2.0));
      float pulse = sin(uv.x * 20.0 + t * 3.0 + i * 2.0) * 0.5 + 0.5;
      vec3 streamColor = mix(vec3(0.0, 0.5, 0.9), vec3(0.4, 0.8, 1.0), u_progress);
      base += streamColor * stream * pulse * 0.025 * (1.0 - vintageMix * 0.3);
    }

    float nodeDist = length(p - vec2(sin(t * 0.5) * 0.3, cos(t * 0.7) * 0.2));
    float nodeGlow = exp(-nodeDist * 4.0) * 0.06;
    base += vec3(0.0, 0.6, 1.0) * nodeGlow * u_progress;

    float cx = uv.x - 0.5;
    float cy = uv.y - 0.5;
    float radial = fbm(vec2(atan(cx, cy) * 2.0, length(vec2(cx, cy)) * 4.0 - t * 0.2));
    base += vec3(0.05, 0.15, 0.3) * radial * 0.15 * u_progress;

    float scanline = sin(uv.y * u_resolution.y * 0.8) * 0.008 * vintageMix;
    base -= scanline;

    float beam = exp(-pow((uv.x - fract(t * 0.08) * 1.4) * 2.5, 2.0));
    vec3 beamCol = mix(vec3(0.7, 0.4, 0.15), vec3(0.0, 0.7, 1.0), u_progress);
    base += beamCol * beam * 0.06;

    float vig = 1.0 - dot(p, p) * 0.35;
    base *= vig;

    gl_FragColor = vec4(base, 1.0);
  }
`

export default function ShaderBackground({ progress = 0 }) {
  const canvasRef = useRef(null)
  const progressRef = useRef(progress)

  progressRef.current = progress

  useEffect(() => {
    const canvas = canvasRef.current
    const gl = canvas.getContext('webgl')
    if (!gl) return

    // If user prefers reduced motion, avoid continuous animation frames.
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches

    const compile = (type, source) => {
      const shader = gl.createShader(type)
      gl.shaderSource(shader, source)
      gl.compileShader(shader)
      return shader
    }

    const program = gl.createProgram()
    gl.attachShader(program, compile(gl.VERTEX_SHADER, VERTEX))
    gl.attachShader(program, compile(gl.FRAGMENT_SHADER, FRAGMENT))
    gl.linkProgram(program)
    gl.useProgram(program)

    const buffer = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW)

    const posLoc = gl.getAttribLocation(program, 'a_position')
    gl.enableVertexAttribArray(posLoc)
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0)

    const timeLoc = gl.getUniformLocation(program, 'u_time')
    const resLoc = gl.getUniformLocation(program, 'u_resolution')
    const progLoc = gl.getUniformLocation(program, 'u_progress')

    let frame = null
    const start = performance.now()

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      gl.viewport(0, 0, canvas.width, canvas.height)
    }

    const render = () => {
      gl.uniform1f(timeLoc, (performance.now() - start) / 1000)
      gl.uniform2f(resLoc, canvas.width, canvas.height)
      gl.uniform1f(progLoc, progressRef.current)
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
      frame = requestAnimationFrame(render)
    }

    resize()
    window.addEventListener('resize', resize)

    if (prefersReducedMotion) {
      gl.uniform1f(timeLoc, 0)
      gl.uniform2f(resLoc, canvas.width, canvas.height)
      gl.uniform1f(progLoc, progressRef.current)
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
    } else {
      frame = requestAnimationFrame(render)
    }

    return () => {
      if (frame) cancelAnimationFrame(frame)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <canvas ref={canvasRef} className="fixed inset-0 w-full h-full -z-10" aria-hidden="true" />
  )
}
