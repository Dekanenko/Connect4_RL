"use client"

interface GameStatusProps {
  status: "playing" | "won" | "lost" | "draw" | "connecting" | "error"
  currentTurn: "player" | "ai"
  isThinking?: boolean
}

export function GameStatus({ status, currentTurn, isThinking }: GameStatusProps) {
  const getStatusText = () => {
    switch (status) {
      case "won":
        return { main: "VICTORY_ACHIEVED", sub: "Neural connection established. Flesh transcended." }
      case "lost":
        return { main: "SYSTEM_FAILURE", sub: "Neural link compromised. Recalibration required." }
      case "draw":
        return { main: "DEADLOCK", sub: "Grid capacity reached. Neither flesh nor machine prevails." }
      case "connecting":
        return { main: "INITIALIZING", sub: "Establishing neural link to DQN core..." }
      case "error":
        return { main: "CONNECTION_LOST", sub: "Failed to reach neural network. Reality fragmented." }
      case "playing":
        if (isThinking) {
          return { main: "PROCESSING", sub: "AI calculating optimal neural pathway..." }
        }
        return currentTurn === "player"
          ? { main: "AWAITING_INPUT", sub: "Select column to deploy consciousness unit" }
          : { main: "AI_PROCESSING", sub: "DQN analyzing probability matrices" }
    }
  }

  const { main, sub } = getStatusText()

  const getStatusColor = () => {
    if (status === "won") return "cyan"
    if (status === "lost") return "red"
    if (status === "draw") return "amber"
    if (status === "connecting") return "blue"
    if (status === "error") return "red"
    return currentTurn === "player" ? "cyan" : "indigo"
  }

  const color = getStatusColor()

  return (
    <div className="animate-fade-in">
      {/* Glass panel */}
      <div className="relative px-6 py-4 rounded-lg border border-cyan-500/30 bg-[#040818]/70 backdrop-blur-md">
        {/* Corner accents - enhanced */}
        <div className="absolute top-0 left-0 w-3 h-3 border-l-2 border-t-2 border-cyan-400/70" />
        <div className="absolute top-0 right-0 w-3 h-3 border-r-2 border-t-2 border-cyan-400/70" />
        <div className="absolute bottom-0 left-0 w-3 h-3 border-l-2 border-b-2 border-cyan-400/70" />
        <div className="absolute bottom-0 right-0 w-3 h-3 border-r-2 border-b-2 border-cyan-400/70" />
        
        {/* Corner dots */}
        <div className="absolute top-1 left-1 w-1 h-1 bg-cyan-400" />
        <div className="absolute top-1 right-1 w-1 h-1 bg-cyan-400" />
        <div className="absolute bottom-1 left-1 w-1 h-1 bg-cyan-400" />
        <div className="absolute bottom-1 right-1 w-1 h-1 bg-cyan-400" />

        {/* Scanline */}
        <div 
          className="absolute inset-0 pointer-events-none opacity-[0.03] rounded-lg overflow-hidden"
          style={{
            backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,200,255,0.2) 2px, rgba(0,200,255,0.2) 4px)'
          }}
        />

        {/* Status indicator */}
        <div className="flex items-center gap-4">
          {/* Animated pulse */}
          <div className="relative">
            <div
              className={`w-3 h-3 rounded-full animate-pulse ${
                color === "cyan" ? "bg-cyan-400" :
                color === "red" ? "bg-red-500" :
                color === "amber" ? "bg-amber-400" :
                color === "indigo" ? "bg-indigo-400" :
                "bg-blue-400"
              }`}
            />
            <div 
              className={`absolute inset-0 rounded-full blur-sm ${
                color === "cyan" ? "bg-cyan-400" :
                color === "red" ? "bg-red-500" :
                color === "amber" ? "bg-amber-400" :
                color === "indigo" ? "bg-indigo-400" :
                "bg-blue-400"
              }`}
            />
            <div 
              className={`absolute -inset-1 rounded-full animate-ping opacity-50 ${
                color === "cyan" ? "bg-cyan-400" :
                color === "red" ? "bg-red-500" :
                color === "amber" ? "bg-amber-400" :
                color === "indigo" ? "bg-indigo-400" :
                "bg-blue-400"
              }`}
            />
          </div>

          <div className="flex-1">
            <h2 
              className={`text-lg font-mono font-bold tracking-[0.2em] glitch-text ${
                color === "cyan" ? "text-cyan-400" :
                color === "red" ? "text-red-400" :
                color === "amber" ? "text-amber-400" :
                color === "indigo" ? "text-indigo-400" :
                "text-blue-400"
              } ${isThinking || status === "connecting" ? "animate-pulse" : ""}`}
              data-text={main}
            >
              {main}
            </h2>
            <p className="text-xs font-mono text-cyan-600/80 tracking-wider">{sub}</p>
          </div>
          
          {/* Status code */}
          <div className="text-right">
            <div className="text-[10px] font-mono text-cyan-700/60 tracking-widest">STATUS</div>
            <div className={`text-xs font-mono tracking-wider ${
              status === "won" ? "text-cyan-400" :
              status === "lost" ? "text-red-400" :
              status === "draw" ? "text-amber-400" :
              "text-cyan-500"
            }`}>
              {status === "won" ? "0x00" : 
               status === "lost" ? "0xFF" : 
               status === "draw" ? "0x7F" :
               status === "error" ? "0xER" :
               "0x01"}
            </div>
          </div>
        </div>

        {/* Processing bar */}
        {(isThinking || status === "connecting") && (
          <div className="mt-3 h-1 bg-[#020410] rounded-full overflow-hidden border border-cyan-900/30">
            <div 
              className="h-full bg-gradient-to-r from-cyan-500 via-blue-400 to-indigo-500 w-1/3 animate-slide-progress" 
            />
          </div>
        )}
      </div>
    </div>
  )
}
