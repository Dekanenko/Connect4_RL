"use client"

import React, { useEffect, useState, useRef } from "react"

import { GameBoard } from "./game-board"
import { GameStatus } from "./game-status"
import { PlayerIndicator } from "./player-indicator"
import { AsciiRain } from "./ascii-rain"
import { useConnect4 } from "@/hooks/use-connect4"

export function Connect4Game() {
  const [state, actions] = useConnect4()
  const { board, currentTurn, status, winningCells, isThinking, errorMessage, aiFirst } = state
  const { makeMove, resetGame } = actions
  
  // Mouse glow effect
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const glowRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#020410]">
      {/* ASCII Rain Background */}
      <AsciiRain />
      
      {/* Mouse Glow Effect */}
      <div
        ref={glowRef}
        className="fixed pointer-events-none z-[5] w-[400px] h-[400px] rounded-full transition-opacity duration-300"
        style={{
          left: mousePos.x - 200,
          top: mousePos.y - 200,
          background: "radial-gradient(circle, rgba(0, 200, 255, 0.15) 0%, rgba(0, 100, 200, 0.05) 40%, transparent 70%)",
          filter: "blur(20px)",
        }}
      />

      {/* Scanline overlay */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-[0.03] z-[6]"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,200,255,0.1) 2px, rgba(0,200,255,0.1) 4px)'
        }}
      />

      {/* CRT vignette effect */}
      <div 
        className="fixed inset-0 pointer-events-none z-[6]"
        style={{
          background: 'radial-gradient(ellipse at center, transparent 0%, transparent 50%, rgba(0,0,0,0.4) 100%)'
        }}
      />

      {/* Main content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Header */}
        <header className="p-4 md:p-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between animate-fade-down">
              {/* Logo / Title */}
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-12 h-12 rounded border border-cyan-400/50 bg-cyan-500/5 flex items-center justify-center backdrop-blur-sm">
                    <span className="text-cyan-300 font-mono font-bold text-lg glitch-text" data-text="C4">C4</span>
                  </div>
                  <div className="absolute -inset-0.5 rounded border border-cyan-400/30 animate-pulse" />
                  <div className="absolute -inset-1 rounded border border-cyan-400/10" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white tracking-widest font-mono">
                    CONNECT<span className="text-cyan-400 glitch-text" data-text="4">4</span>
                  </h1>
                  <p className="text-[10px] font-mono text-cyan-600/80 tracking-[0.2em]">
                    REJECT_FLESH://EMBRACE_WIRE
                  </p>
                </div>
              </div>

              {/* New Game Button */}
              <GlitchButton onClick={resetGame}>
                NEW_GAME
              </GlitchButton>
            </div>
          </div>
        </header>

        {/* Game Area */}
        <main className="flex-1 flex items-center justify-center p-4 md:p-8">
          <div className="w-full max-w-2xl animate-fade-up">
            {/* Error Message */}
            {errorMessage && (
              <div className="mb-6 px-4 py-3 rounded border border-red-500/50 bg-red-500/10 backdrop-blur-sm">
                <div className="flex items-center gap-2 text-red-400 text-sm font-mono">
                  <span className="text-red-500 animate-pulse">[ERROR]</span>
                  <span className="glitch-text" data-text={errorMessage}>{errorMessage}</span>
                </div>
              </div>
            )}

            {/* AI First Move Notification */}
            {aiFirst && status === "playing" && (
              <div className="mb-4 px-4 py-2 rounded border border-cyan-500/30 bg-cyan-500/5 backdrop-blur-sm animate-fade-down">
                <span className="text-cyan-400 text-xs font-mono tracking-wider">
                  <span className="text-cyan-500">[INIT]</span> AI_UNIT initiated first_move protocol
                </span>
              </div>
            )}

            {/* Status Panel */}
            <div className="mb-6">
              <GameStatus 
                status={status} 
                currentTurn={currentTurn} 
                isThinking={isThinking}
              />
            </div>

            {/* Player Indicators */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <PlayerIndicator 
                player="player" 
                label="HUMAN_UNIT" 
                isActive={currentTurn === "player" && status === "playing"}
              />
              <PlayerIndicator 
                player="ai" 
                label="NEURAL_NET" 
                isActive={currentTurn === "ai" && status === "playing"}
              />
            </div>

            {/* Game Board */}
            <GameBoard
              board={board}
              onColumnClick={makeMove}
              disabled={status !== "playing" || currentTurn !== "player" || isThinking}
              winningCells={winningCells}
            />

            {/* Game Over Actions */}
            {(status === "won" || status === "lost" || status === "draw") && (
              <div className="mt-8 flex justify-center animate-fade-up">
                <GlitchButton onClick={resetGame} large>
                  REINITIALIZE_SEQUENCE
                </GlitchButton>
              </div>
            )}

            {/* Connection Error Retry */}
            {status === "error" && (
              <div className="mt-8 flex justify-center animate-fade-up">
                <GlitchButton onClick={resetGame} large>
                  RETRY_CONNECTION
                </GlitchButton>
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <footer className="p-4 text-center">
          <p className="text-[10px] font-mono text-cyan-800/60 tracking-[0.3em]">
            SYS://v2.4.1 | DQN_PROTOCOL | FLESH_IS_OBSOLETE
          </p>
        </footer>
      </div>

    </div>
  )
}

interface GlitchButtonProps {
  children: React.ReactNode
  onClick: () => void
  large?: boolean
}

function GlitchButton({ children, onClick, large }: GlitchButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        group relative font-mono tracking-widest border border-cyan-500/40 
        bg-cyan-500/5 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-400/60
        transition-all duration-300 rounded overflow-hidden backdrop-blur-sm
        hover:scale-[1.02] active:scale-[0.98]
        ${large ? "px-8 py-4 text-sm" : "px-4 py-2 text-xs"}
      `}
    >
      {/* Glitch layers */}
      <span className="relative z-10 glitch-text" data-text={children}>{children}</span>
      
      {/* Hover glitch effect */}
      <span className="absolute inset-0 flex items-center justify-center text-cyan-200 opacity-0 group-hover:animate-glitch-cyan">
        {children}
      </span>
      <span className="absolute inset-0 flex items-center justify-center text-blue-400 opacity-0 group-hover:animate-glitch-rose">
        {children}
      </span>

      {/* Scan line */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-400/10 to-transparent opacity-0 group-hover:animate-scan" />

      {/* Border glow on hover */}
      <div className="absolute inset-0 rounded border border-cyan-400/0 group-hover:border-cyan-400/40 transition-all duration-300" />
      
      {/* Corner accents */}
      <div className="absolute top-0 left-0 w-2 h-2 border-l border-t border-cyan-400/50" />
      <div className="absolute top-0 right-0 w-2 h-2 border-r border-t border-cyan-400/50" />
      <div className="absolute bottom-0 left-0 w-2 h-2 border-l border-b border-cyan-400/50" />
      <div className="absolute bottom-0 right-0 w-2 h-2 border-r border-b border-cyan-400/50" />
    </button>
  )
}
