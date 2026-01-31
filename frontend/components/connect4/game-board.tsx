"use client"

import { useState } from "react"

interface GameBoardProps {
  board: (null | "player" | "ai")[][]
  onColumnClick: (col: number) => void
  disabled?: boolean
  winningCells?: [number, number][]
}

export function GameBoard({ board, onColumnClick, disabled, winningCells = [] }: GameBoardProps) {
  const [hoveredCol, setHoveredCol] = useState<number | null>(null)

  const isWinningCell = (row: number, col: number) => {
    return winningCells.some(([r, c]) => r === row && c === col)
  }

  return (
    <div className="relative">
      {/* HUD Frame */}
      <div className="absolute -inset-6 rounded-lg border border-cyan-500/20 pointer-events-none">
        <div className="absolute top-0 left-6 -translate-y-1/2 bg-[#020410] px-3">
          <span className="text-[10px] font-mono text-cyan-500/70 tracking-[0.2em]">TACTICAL_GRID://v2.4</span>
        </div>
        <div className="absolute bottom-0 right-6 translate-y-1/2 bg-[#020410] px-3">
          <span className="text-[10px] font-mono text-cyan-500/70 tracking-[0.2em]">MATRIX://7x6</span>
        </div>
        {/* Corner decorations - enhanced */}
        <div className="absolute top-0 left-0 w-4 h-4 border-l-2 border-t-2 border-cyan-400/60" />
        <div className="absolute top-0 right-0 w-4 h-4 border-r-2 border-t-2 border-cyan-400/60" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-l-2 border-b-2 border-cyan-400/60" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-r-2 border-b-2 border-cyan-400/60" />
        
        {/* Additional corner details */}
        <div className="absolute top-1 left-1 w-1 h-1 bg-cyan-400/80" />
        <div className="absolute top-1 right-1 w-1 h-1 bg-cyan-400/80" />
        <div className="absolute bottom-1 left-1 w-1 h-1 bg-cyan-400/80" />
        <div className="absolute bottom-1 right-1 w-1 h-1 bg-cyan-400/80" />
      </div>

      {/* Main Grid */}
      <div className="relative rounded-lg p-5 backdrop-blur-md bg-[#040818]/60 border border-cyan-500/20">
        {/* Scanline overlay */}
        <div 
          className="absolute inset-0 pointer-events-none opacity-[0.04] rounded-lg overflow-hidden"
          style={{
            backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,200,255,0.15) 2px, rgba(0,200,255,0.15) 4px)'
          }}
        />

        {/* Grid background pattern */}
        <div 
          className="absolute inset-0 pointer-events-none opacity-[0.03] rounded-lg"
          style={{
            backgroundImage: 'linear-gradient(rgba(0,200,255,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(0,200,255,0.4) 1px, transparent 1px)',
            backgroundSize: '20px 20px'
          }}
        />

        {/* Inner glow */}
        <div className="absolute inset-0 rounded-lg" style={{
          boxShadow: 'inset 0 0 60px rgba(0, 150, 200, 0.1)'
        }} />

        {/* Column hover zones */}
        <div className="grid grid-cols-7 gap-2 md:gap-3 relative z-10">
          {Array.from({ length: 7 }).map((_, col) => (
            <button
              key={col}
              onClick={() => !disabled && onColumnClick(col)}
              onMouseEnter={() => setHoveredCol(col)}
              onMouseLeave={() => setHoveredCol(null)}
              disabled={disabled}
              className="group relative flex flex-col gap-2 md:gap-3 cursor-pointer disabled:cursor-not-allowed transition-transform hover:scale-[1.02]"
            >
              {/* Column indicator */}
              <div 
                className={`absolute -top-8 left-1/2 -translate-x-1/2 transition-all duration-200 ${
                  hoveredCol === col && !disabled ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'
                }`}
              >
                <div className="text-cyan-400 text-sm font-mono animate-bounce">
                  ▼
                </div>
                <div className="text-cyan-400/50 text-[8px] font-mono text-center">
                  {String(col).padStart(2, '0')}
                </div>
              </div>

              {board.map((row, rowIndex) => {
                const cell = row[col]
                const isWinning = isWinningCell(rowIndex, col)
                
                return (
                  <div
                    key={rowIndex}
                    className="relative w-10 h-10 md:w-12 md:h-12 lg:w-14 lg:h-14"
                  >
                    {/* Cell background - Dark void style */}
                    <div className="absolute inset-0 rounded-full bg-[#020410] border border-cyan-800/30 shadow-inner overflow-hidden">
                      <div className="absolute inset-1 rounded-full bg-gradient-to-b from-cyan-900/10 to-transparent" />
                      {/* Inner ring */}
                      <div className="absolute inset-2 rounded-full border border-cyan-900/20" />
                    </div>

                    {/* Game piece */}
                    {cell && (
                      <div
                        className="absolute inset-1 animate-glitch-appear"
                      >
                        <div 
                          className={`
                            w-full h-full rounded-full relative
                            ${cell === "player" 
                              ? "bg-gradient-to-br from-cyan-300 via-cyan-500 to-blue-700" 
                              : "bg-gradient-to-br from-blue-400 via-indigo-500 to-purple-700"
                            }
                            ${isWinning ? "animate-pulse" : ""}
                          `}
                        >
                          {/* Inner glow */}
                          <div 
                            className={`
                              absolute inset-0 rounded-full
                              ${cell === "player" 
                                ? "shadow-[inset_0_-4px_12px_rgba(0,200,255,0.5),inset_0_4px_8px_rgba(255,255,255,0.3)]" 
                                : "shadow-[inset_0_-4px_12px_rgba(100,80,200,0.5),inset_0_4px_8px_rgba(255,255,255,0.2)]"
                              }
                            `}
                          />
                          
                          {/* Outer glow */}
                          <div 
                            className={`
                              absolute -inset-1 rounded-full opacity-60 blur-md -z-10
                              ${cell === "player" 
                                ? "bg-cyan-400" 
                                : "bg-indigo-500"
                              }
                              ${isWinning ? "opacity-90 blur-lg" : ""}
                            `}
                          />

                          {/* Digital pulse ring for winning cells */}
                          {isWinning && (
                            <>
                              <div
                                className={`
                                  absolute -inset-2 rounded-full border-2 animate-ping
                                  ${cell === "player" ? "border-cyan-400" : "border-indigo-400"}
                                `}
                              />
                              <div
                                className={`
                                  absolute -inset-3 rounded-full border animate-pulse
                                  ${cell === "player" ? "border-cyan-500/50" : "border-indigo-500/50"}
                                `}
                              />
                            </>
                          )}

                          {/* Core light */}
                          <div className="absolute top-1.5 left-1.5 w-3 h-3 rounded-full bg-white/50 blur-sm" />
                          
                          {/* Circuit pattern overlay */}
                          <div className="absolute inset-0 rounded-full opacity-20" style={{
                            backgroundImage: 'radial-gradient(circle at 30% 30%, white 1px, transparent 1px)',
                            backgroundSize: '8px 8px'
                          }} />
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </button>
          ))}
        </div>
      </div>

      {/* Drop buttons */}
      <div className="grid grid-cols-7 gap-2 md:gap-3 mt-4">
        {Array.from({ length: 7 }).map((_, col) => (
          <DropButton
            key={col}
            col={col}
            onClick={() => !disabled && onColumnClick(col)}
            disabled={disabled || board[0][col] !== null}
          />
        ))}
      </div>

    </div>
  )
}

function DropButton({ onClick, disabled, col }: { onClick: () => void; disabled: boolean; col: number }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        group relative h-10 rounded border font-mono text-xs
        transition-all duration-300 overflow-hidden
        ${disabled 
          ? "border-cyan-900/30 text-cyan-900/50 cursor-not-allowed bg-[#020410]/50" 
          : "border-cyan-500/40 text-cyan-400 hover:border-cyan-400/70 hover:bg-cyan-500/10 cursor-pointer hover:scale-105 active:scale-95"
        }
      `}
    >
      {/* Column number */}
      <span className="absolute top-0.5 left-1 text-[8px] text-cyan-600/50">
        {String(col).padStart(2, '0')}
      </span>
      
      <span className="relative z-10 group-hover:animate-pulse">{'▼'}</span>
      
      {/* Glitch effect on hover */}
      {!disabled && (
        <>
          <span className="absolute inset-0 flex items-center justify-center text-cyan-200 opacity-0 group-hover:animate-glitch-cyan">
            {'▼'}
          </span>
          <span className="absolute inset-0 flex items-center justify-center text-blue-300 opacity-0 group-hover:animate-glitch-rose">
            {'▼'}
          </span>
          
          {/* Scan line */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-400/20 to-transparent opacity-0 group-hover:animate-scan" />
        </>
      )}
      
      {/* Corner accents */}
      <div className="absolute top-0 left-0 w-1.5 h-1.5 border-l border-t border-cyan-500/50" />
      <div className="absolute top-0 right-0 w-1.5 h-1.5 border-r border-t border-cyan-500/50" />
      <div className="absolute bottom-0 left-0 w-1.5 h-1.5 border-l border-b border-cyan-500/50" />
      <div className="absolute bottom-0 right-0 w-1.5 h-1.5 border-r border-b border-cyan-500/50" />
    </button>
  )
}
