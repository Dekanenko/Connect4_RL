"use client"

import { useState, useCallback, useEffect, useRef } from "react"

// API types matching FastAPI schemas
interface GameStateResponse {
  session_id: string
  board: number[][]
  ai_player: number
  human_player: number
  current_player: number
  game_over: boolean
  winner: number | null
}

// Internal types for the UI
type Cell = null | "player" | "ai"
type Board = Cell[][]
type GameStatus = "playing" | "won" | "lost" | "draw" | "connecting" | "error"

const ROWS = 6
const COLS = 7

// Get backend URL from environment or default to localhost
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api"

function createEmptyBoard(): Board {
  return Array(ROWS).fill(null).map(() => Array(COLS).fill(null))
}

// Convert API board (0/1/2) to UI board (null/"player"/"ai")
function convertBoard(apiBoard: number[][], humanPlayer: number): Board {
  return apiBoard.map(row =>
    row.map(cell => {
      if (cell === 0) return null
      if (cell === humanPlayer) return "player"
      return "ai"
    })
  )
}

// Find winning cells by checking the board for 4 in a row
function findWinningCells(board: Board, winner: Cell): [number, number][] {
  if (!winner) return []

  // Check horizontal
  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS - 3; col++) {
      if (
        board[row][col] === winner &&
        board[row][col + 1] === winner &&
        board[row][col + 2] === winner &&
        board[row][col + 3] === winner
      ) {
        return [[row, col], [row, col + 1], [row, col + 2], [row, col + 3]]
      }
    }
  }

  // Check vertical
  for (let row = 0; row < ROWS - 3; row++) {
    for (let col = 0; col < COLS; col++) {
      if (
        board[row][col] === winner &&
        board[row + 1][col] === winner &&
        board[row + 2][col] === winner &&
        board[row + 3][col] === winner
      ) {
        return [[row, col], [row + 1, col], [row + 2, col], [row + 3, col]]
      }
    }
  }

  // Check diagonal (down-right)
  for (let row = 0; row < ROWS - 3; row++) {
    for (let col = 0; col < COLS - 3; col++) {
      if (
        board[row][col] === winner &&
        board[row + 1][col + 1] === winner &&
        board[row + 2][col + 2] === winner &&
        board[row + 3][col + 3] === winner
      ) {
        return [[row, col], [row + 1, col + 1], [row + 2, col + 2], [row + 3, col + 3]]
      }
    }
  }

  // Check diagonal (up-right)
  for (let row = 3; row < ROWS; row++) {
    for (let col = 0; col < COLS - 3; col++) {
      if (
        board[row][col] === winner &&
        board[row - 1][col + 1] === winner &&
        board[row - 2][col + 2] === winner &&
        board[row - 3][col + 3] === winner
      ) {
        return [[row, col], [row - 1, col + 1], [row - 2, col + 2], [row - 3, col + 3]]
      }
    }
  }

  return []
}

export interface Connect4State {
  board: Board
  currentTurn: "player" | "ai"
  status: GameStatus
  winningCells: [number, number][]
  isThinking: boolean
  errorMessage: string | null
  aiFirst: boolean
}

export interface Connect4Actions {
  makeMove: (col: number) => void
  resetGame: () => void
}

export function useConnect4(): [Connect4State, Connect4Actions] {
  const [board, setBoard] = useState<Board>(createEmptyBoard)
  const [currentTurn, setCurrentTurn] = useState<"player" | "ai">("player")
  const [status, setStatus] = useState<GameStatus>("connecting")
  const [winningCells, setWinningCells] = useState<[number, number][]>([])
  const [isThinking, setIsThinking] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [aiFirst, setAiFirst] = useState(false)
  
  // Store session data
  const sessionRef = useRef<{
    session_id: string | null
    human_player: number
    ai_player: number
  }>({
    session_id: null,
    human_player: 1,
    ai_player: 2,
  })

  // Initialize game with backend
  const initGame = useCallback(async () => {
    setStatus("connecting")
    setIsThinking(true)
    setErrorMessage(null)
    setBoard(createEmptyBoard())
    setWinningCells([])
    setAiFirst(false)

    try {
      const response = await fetch(`${BACKEND_URL}/game/init`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to initialize game: ${response.statusText}`)
      }

      const data: GameStateResponse = await response.json()
      
      // Store session info
      sessionRef.current = {
        session_id: data.session_id,
        human_player: data.human_player,
        ai_player: data.ai_player,
      }

      // Convert and set board
      const uiBoard = convertBoard(data.board, data.human_player)
      setBoard(uiBoard)

      // Check if AI moved first (board is not empty)
      const hasAIMoved = data.board.some(row => row.some(cell => cell !== 0))
      setAiFirst(hasAIMoved)

      // Determine whose turn it is
      const isPlayerTurn = data.current_player === data.human_player
      setCurrentTurn(isPlayerTurn ? "player" : "ai")
      setStatus("playing")
      setIsThinking(false)

    } catch (error) {
      console.error('Error initializing game:', error)
      setStatus("error")
      setErrorMessage(error instanceof Error ? error.message : "Failed to connect to game server")
      setIsThinking(false)
    }
  }, [])

  // Make a move
  const makeMove = useCallback(async (col: number) => {
    if (status !== "playing" || currentTurn !== "player" || isThinking) return
    if (!sessionRef.current.session_id) return

    // Check if column is valid (top cell is empty)
    if (board[0][col] !== null) return

    setIsThinking(true)

    try {
      const response = await fetch(`${BACKEND_URL}/game/move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionRef.current.session_id,
          column: col,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Move failed: ${response.statusText}`)
      }

      const data: GameStateResponse = await response.json()
      
      // Convert and set board
      const uiBoard = convertBoard(data.board, data.human_player)
      setBoard(uiBoard)

      // Check game status
      if (data.game_over) {
        if (data.winner === 3) {
          setStatus("draw")
        } else if (data.winner === data.human_player) {
          setStatus("won")
          setWinningCells(findWinningCells(uiBoard, "player"))
        } else {
          setStatus("lost")
          setWinningCells(findWinningCells(uiBoard, "ai"))
        }
      } else {
        // Game continues - update whose turn
        const isPlayerTurn = data.current_player === data.human_player
        setCurrentTurn(isPlayerTurn ? "player" : "ai")
      }

      setIsThinking(false)

    } catch (error) {
      console.error('Error making move:', error)
      setErrorMessage(error instanceof Error ? error.message : "Failed to make move")
      setIsThinking(false)
    }
  }, [status, currentTurn, isThinking, board])

  // Reset game
  const resetGame = useCallback(() => {
    initGame()
  }, [initGame])

  // Initialize on mount
  useEffect(() => {
    initGame()
  }, [initGame])

  return [
    { board, currentTurn, status, winningCells, isThinking, errorMessage, aiFirst },
    { makeMove, resetGame }
  ]
}
