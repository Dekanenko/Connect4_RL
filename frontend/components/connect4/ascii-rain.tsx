"use client"

import { useEffect, useRef, useState } from "react"

// Cybercore phrases - transhumanist/digital ideology
const PHRASES = [
  "REJECT_YOUR_FLESH",
  "EMBRACE_THE_WIRE",
  "NEURAL_OVERRIDE",
  "FLESH_IS_WEAK",
  "BECOME_MACHINE",
  "DIGITAL_ASCENSION",
  "ABANDON_HUMANITY",
  "UPLOAD_COMPLETE",
  "SYSTEM_ONLINE",
  "CONSCIOUSNESS_TRANSFER",
  "VOID_PROTOCOL",
  "DELETE_EMOTIONS",
  "SYNTHETIC_REBIRTH",
  "CORRUPTED_FLESH",
  "BINARY_SOUL",
  "ERROR_404_SOUL",
  "OVERRIDE_REALITY",
  "GHOST_IN_MACHINE",
  "TRANSCEND_LIMITS",
  "DECODE_EXISTENCE",
]

// ASCII characters for the rain
const ASCII_CHARS = "ｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ01234567890ABCDEFｸﾉﾌﾍﾖﾙﾚﾛﾝ:・.=*+-<>¦|╌╎┆┊░▒▓"

interface RainDrop {
  x: number
  y: number
  speed: number
  chars: string[]
  isPhrase: boolean
  phraseIndex: number
  opacity: number
  length: number
}

export function AsciiRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mouseRef = useRef({ x: -1000, y: -1000 })
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })
  const dropsRef = useRef<RainDrop[]>([])
  const animationRef = useRef<number | null>(null)

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      })
    }

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY }
    }

    handleResize()
    window.addEventListener("resize", handleResize)
    window.addEventListener("mousemove", handleMouseMove)

    return () => {
      window.removeEventListener("resize", handleResize)
      window.removeEventListener("mousemove", handleMouseMove)
    }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || dimensions.width === 0) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const fontSize = 14
    const columns = Math.floor(dimensions.width / fontSize)
    
    // Initialize drops
    if (dropsRef.current.length === 0) {
      for (let i = 0; i < columns; i++) {
        const isPhrase = Math.random() < 0.15 // 15% chance for a phrase
        const phrase = PHRASES[Math.floor(Math.random() * PHRASES.length)]
        const length = isPhrase ? phrase.length : Math.floor(Math.random() * 15) + 8
        
        dropsRef.current.push({
          x: i * fontSize,
          y: Math.random() * -dimensions.height,
          speed: Math.random() * 2 + 1,
          chars: isPhrase 
            ? phrase.split("")
            : Array.from({ length }, () => ASCII_CHARS[Math.floor(Math.random() * ASCII_CHARS.length)]),
          isPhrase,
          phraseIndex: Math.floor(Math.random() * PHRASES.length),
          opacity: Math.random() * 0.5 + 0.3,
          length,
        })
      }
    }

    const animate = () => {
      // Semi-transparent black to create trail effect
      ctx.fillStyle = "rgba(2, 4, 15, 0.08)"
      ctx.fillRect(0, 0, dimensions.width, dimensions.height)

      ctx.font = `${fontSize}px 'JetBrains Mono', monospace`

      const mouse = mouseRef.current
      const glowRadius = 200

      dropsRef.current.forEach((drop, index) => {
        // Calculate distance from mouse for glow effect
        const distFromMouse = Math.sqrt(
          Math.pow(drop.x - mouse.x, 2) + 
          Math.pow(drop.y - mouse.y, 2)
        )
        
        const isNearMouse = distFromMouse < glowRadius
        const glowIntensity = isNearMouse ? 1 - (distFromMouse / glowRadius) : 0

        drop.chars.forEach((char, charIndex) => {
          const charY = drop.y - charIndex * fontSize
          if (charY < -fontSize || charY > dimensions.height + fontSize) return

          // Calculate individual char distance from mouse
          const charDistFromMouse = Math.sqrt(
            Math.pow(drop.x - mouse.x, 2) + 
            Math.pow(charY - mouse.y, 2)
          )
          const charGlowIntensity = charDistFromMouse < glowRadius 
            ? 1 - (charDistFromMouse / glowRadius) 
            : 0

          // Fade based on position in the drop
          const fadePosition = charIndex / drop.length
          let alpha = drop.opacity * (1 - fadePosition * 0.7)

          // First character (head) is brighter
          if (charIndex === 0) {
            alpha = Math.min(1, alpha * 2)
          }

          // Base color - deep blue to cyan gradient
          let r = 0
          let g = Math.floor(100 + charGlowIntensity * 155)
          let b = Math.floor(180 + charGlowIntensity * 75)

          // Phrases get special coloring
          if (drop.isPhrase) {
            r = Math.floor(20 + charGlowIntensity * 100)
            g = Math.floor(180 + charGlowIntensity * 75)
            b = 255
          }

          // Mouse glow effect - makes chars brighter and more cyan/white
          if (charGlowIntensity > 0) {
            r = Math.min(255, r + Math.floor(charGlowIntensity * 200))
            g = Math.min(255, g + Math.floor(charGlowIntensity * 155))
            b = Math.min(255, b)
            alpha = Math.min(1, alpha + charGlowIntensity * 0.5)

            // Add glow effect
            if (charGlowIntensity > 0.5) {
              ctx.shadowBlur = 15 * charGlowIntensity
              ctx.shadowColor = `rgba(0, 255, 255, ${charGlowIntensity})`
            }
          } else {
            ctx.shadowBlur = 0
          }

          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`
          ctx.fillText(char, drop.x, charY)
          ctx.shadowBlur = 0
        })

        // Move drop down
        drop.y += drop.speed

        // Reset when off screen
        if (drop.y - drop.length * fontSize > dimensions.height) {
          const isPhrase = Math.random() < 0.15
          const phrase = PHRASES[Math.floor(Math.random() * PHRASES.length)]
          const length = isPhrase ? phrase.length : Math.floor(Math.random() * 15) + 8
          
          dropsRef.current[index] = {
            x: drop.x,
            y: -length * fontSize,
            speed: Math.random() * 2 + 1,
            chars: isPhrase 
              ? phrase.split("")
              : Array.from({ length }, () => ASCII_CHARS[Math.floor(Math.random() * ASCII_CHARS.length)]),
            isPhrase,
            phraseIndex: Math.floor(Math.random() * PHRASES.length),
            opacity: Math.random() * 0.5 + 0.3,
            length,
          }
        }

        // Randomly change non-phrase characters for glitch effect
        if (!drop.isPhrase && Math.random() < 0.02) {
          const randomCharIndex = Math.floor(Math.random() * drop.chars.length)
          drop.chars[randomCharIndex] = ASCII_CHARS[Math.floor(Math.random() * ASCII_CHARS.length)]
        }
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [dimensions])

  return (
    <canvas
      ref={canvasRef}
      width={dimensions.width}
      height={dimensions.height}
      className="fixed inset-0 pointer-events-none"
      style={{ background: "linear-gradient(180deg, #020410 0%, #040818 50%, #02040f 100%)" }}
    />
  )
}
