# Chess — Game Design Document

## Overview

A complete, self-contained chess game running in a web browser. Single HTML file + CSS + JS, no dependencies. Supports human vs. AI and human vs. human modes.

## Target Platform

Web browser. Copy `src/` files into any web project or open `index.html` directly.

## Core Features

- Full chess rules: legal move generation, castling, en passant, pawn promotion
- Check, checkmate, and stalemate detection
- Two game modes: Human vs. AI, Human vs. Human
- AI opponent: minimax with alpha-beta pruning (configurable depth)
- Move history panel (algebraic notation)
- Highlight: selected piece, legal move targets, last move
- Captured pieces display
- New game / resign controls

## Out of Scope (v1)

- Online multiplayer
- Time controls / clocks
- Opening book
- Endgame tablebases
- Save / load game (PGN import/export)

## Architecture

### Files

| File | Responsibility |
|------|---------------|
| `index.html` | DOM structure, wires modules together |
| `style.css` | Board, pieces, UI panel styling |
| `chess-engine.js` | All game rules — no DOM touches |
| `board-renderer.js` | All DOM updates — no rule logic |
| `ai-opponent.js` | Minimax search — calls engine only |

### State Shape

```js
{
  board: Array(64),       // piece codes, null for empty. Index 0 = a8, 63 = h8
  turn: 'white' | 'black',
  castling: { wK, wQ, bK, bQ },  // boolean flags
  enPassant: null | squareIndex,
  halfMoveClock: number,  // for 50-move rule
  fullMoveNumber: number,
  status: 'playing' | 'check' | 'checkmate' | 'stalemate' | 'draw'
}
```

### Piece Codes

Uppercase = white, lowercase = black.

| Code | Piece |
|------|-------|
| K/k | King |
| Q/q | Queen |
| R/r | Rook |
| B/b | Bishop |
| N/n | Knight |
| P/p | Pawn |

### Board Indexing

```
Index 0  = a8 (top-left from white's perspective)
Index 7  = h8
Index 56 = a1
Index 63 = h1

file = index % 8       (0=a … 7=h)
rank = 7 - Math.floor(index / 8)   (0=1 … 7=8)
```

## AI Design

- Algorithm: Minimax with alpha-beta pruning
- Default depth: 3 (playable speed, ~club level)
- Evaluation: material count + piece-square tables
- Piece values: P=100, N=320, B=330, R=500, Q=900, K=20000

### Piece-Square Tables

Position bonuses applied to all pieces to encourage:
- Pawns advancing toward center and promotion
- Knights toward center squares
- Bishops on long diagonals
- Rooks on open files
- King safety (castled position in midgame, active in endgame)

## UI Layout

```
┌─────────────────────────────────┐
│  Chess            [New] [Resign] │
├──────────────────┬──────────────┤
│                  │ Move History │
│   Chess Board    │              │
│   (8×8 grid)     │ Captured     │
│                  │ Pieces       │
├──────────────────┴──────────────┤
│  Status: White to move           │
└─────────────────────────────────┘
```

## Visual Design

- Classic board: light `#f0d9b5`, dark `#b58863` (Lichess palette)
- Selected square highlight: `#7fc97f`
- Legal move dots on empty squares, rings on occupied
- Last move highlight: subtle yellow tint
- Unicode chess pieces (no image assets needed)
- Responsive: scales to viewport width

## Move Flow (Human)

1. Click piece → highlight it + show legal move dots
2. Click legal target → execute move, update state, re-render
3. If AI mode → trigger AI search after render, execute AI move

## Pawn Promotion

On reaching the back rank, show a modal with Q/R/B/N options. Wait for selection before completing the move.
