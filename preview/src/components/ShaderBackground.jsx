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
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }

  void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    float t = u_time * 0.3;

    float vintageMix = 1.0 - smoothstep(0.35, 0.65, u_progress + uv.x * 0.2);

    vec3 vintageColor = vec3(0.12, 0.08, 0.04);
    vec3 modernColor = vec3(0.02, 0.04, 0.08);
    vec3 base = mix(modernColor, vintageColor, vintageMix);

    float n = noise(uv * 8.0 + t) * 0.03;
    base += n * vintageMix;

    float scanline = sin(uv.y * u_resolution.y * 1.5) * 0.015 * vintageMix;
    base -= scanline;

    float beam = exp(-pow((uv.x - fract(t * 0.15) * 1.2 + 0.1) * 3.0, 2.0));
    vec3 beamColor = mix(vec3(0.8, 0.5, 0.2), vec3(0.0, 0.6, 1.0), u_progress);
    base += beamColor * beam * 0.08;

    float grid = step(0.98, fract(uv.x * 40.0)) + step(0.98, fract(uv.y * 40.0));
    base += vec3(0.0, 0.4, 0.6) * grid * 0.015 * (1.0 - vintageMix);

    float vignette = 1.0 - length(uv - 0.5) * 0.8;
    base *= vignette;

    gl_FragColor = vec4(base, 1.0);
  }
`

export default function ShaderBackground({ progress = 0.5 }) {
  const canvasRef = useRef(null)
  const progressRef = useRef(progress)

  progressRef.current = progress

  useEffect(() => {
    const canvas = canvasRef.current
    const gl = canvas.getContext('webgl')
    if (!gl) return

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
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
      gl.STATIC_DRAW
    )

    const posLoc = gl.getAttribLocation(program, 'a_position')
    gl.enableVertexAttribArray(posLoc)
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0)

    const timeLoc = gl.getUniformLocation(program, 'u_time')
    const resLoc = gl.getUniformLocation(program, 'u_resolution')
    const progLoc = gl.getUniformLocation(program, 'u_progress')

    let frame
    const start = performance.now()

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      gl.viewport(0, 0, canvas.width, canvas.height)
    }

    const render = () => {
      const t = (performance.now() - start) / 1000
      gl.uniform1f(timeLoc, t)
      gl.uniform2f(resLoc, canvas.width, canvas.height)
      gl.uniform1f(progLoc, progressRef.current)
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
      frame = requestAnimationFrame(render)
    }

    resize()
    window.addEventListener('resize', resize)
    frame = requestAnimationFrame(render)

    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full -z-10"
      aria-hidden="true"
    />
  )
}
