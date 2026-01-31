"use client"

interface PlayerIndicatorProps {
  player: "player" | "ai"
  label: string
  isActive: boolean
}

export function PlayerIndicator({ player, label, isActive }: PlayerIndicatorProps) {
  const isPlayerSide = player === "player"
  
  return (
    <div
      className={`
        relative flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-sm transition-all duration-300
        ${isActive 
          ? isPlayerSide 
            ? "border-cyan-500/50 bg-cyan-500/10" 
            : "border-indigo-500/50 bg-indigo-500/10"
          : "border-cyan-900/30 bg-[#040818]/50"
        }
        ${isActive ? "scale-[1.02]" : "scale-100"}
      `}
    >
      {/* Corner accents */}
      <div className={`absolute top-0 left-0 w-2 h-2 border-l border-t ${isActive ? (isPlayerSide ? "border-cyan-400/70" : "border-indigo-400/70") : "border-cyan-800/30"}`} />
      <div className={`absolute top-0 right-0 w-2 h-2 border-r border-t ${isActive ? (isPlayerSide ? "border-cyan-400/70" : "border-indigo-400/70") : "border-cyan-800/30"}`} />
      <div className={`absolute bottom-0 left-0 w-2 h-2 border-l border-b ${isActive ? (isPlayerSide ? "border-cyan-400/70" : "border-indigo-400/70") : "border-cyan-800/30"}`} />
      <div className={`absolute bottom-0 right-0 w-2 h-2 border-r border-b ${isActive ? (isPlayerSide ? "border-cyan-400/70" : "border-indigo-400/70") : "border-cyan-800/30"}`} />
      
      {/* Orb preview */}
      <div className="relative">
        <div 
          className={`
            w-8 h-8 rounded-full 
            ${isPlayerSide 
              ? "bg-gradient-to-br from-cyan-300 via-cyan-500 to-blue-700" 
              : "bg-gradient-to-br from-blue-400 via-indigo-500 to-purple-700"
            }
          `}
        >
          <div className="absolute top-0.5 left-0.5 w-2 h-2 rounded-full bg-white/50 blur-sm" />
        </div>
        {isActive && (
          <>
            <div
              className={`
                absolute -inset-1 rounded-full border animate-ping
                ${isPlayerSide ? "border-cyan-400" : "border-indigo-400"}
              `}
            />
            <div
              className={`
                absolute -inset-2 rounded-full blur-md opacity-40
                ${isPlayerSide ? "bg-cyan-400" : "bg-indigo-500"}
              `}
            />
          </>
        )}
      </div>

      <div className="flex-1">
        <div className="text-[10px] font-mono text-cyan-700/60 uppercase tracking-[0.2em]">
          {isPlayerSide ? "UNIT://01" : "UNIT://02"}
        </div>
        <div className={`text-sm font-mono font-medium tracking-wider ${isActive ? "text-white" : "text-cyan-600/80"}`}>
          {label}
        </div>
      </div>

      {/* Active indicator */}
      {isActive && (
        <div className="flex flex-col items-end gap-0.5">
          <div
            className={`
              text-xs font-mono animate-pulse tracking-wider
              ${isPlayerSide ? "text-cyan-400" : "text-indigo-400"}
            `}
          >
            ACTIVE
          </div>
          <div className={`w-8 h-0.5 rounded-full ${isPlayerSide ? "bg-cyan-400" : "bg-indigo-400"}`} />
        </div>
      )}
      
      {/* Inactive indicator */}
      {!isActive && (
        <div className="text-[10px] font-mono text-cyan-800/40 tracking-wider">
          STANDBY
        </div>
      )}
    </div>
  )
}
