# Chess

A fully playable chess game for the web browser. No dependencies, no build step — copy the `src/` folder and open `index.html`.

## Features

- Full chess rules: castling, en passant, pawn promotion, check/checkmate/stalemate detection
- Three modes: Play as White vs AI, Play as Black vs AI, Human vs Human
- AI opponent — minimax with alpha-beta pruning (depth 3, adjustable in `ai-opponent.js`)
- Move history in algebraic notation
- Captured pieces display
- Responsive layout

## Files

| File | Purpose |
|------|---------|
| `src/index.html` | Entry point — open this in a browser |
| `src/style.css` | All styling |
| `src/chess-engine.js` | Pure game logic: move generation, validation, check/checkmate |
| `src/board-renderer.js` | DOM rendering, piece display, UI updates |
| `src/ai-opponent.js` | Minimax AI with alpha-beta pruning and piece-square tables |

## How to Use

1. Copy the entire `src/` folder into your project
2. Open `index.html` in a browser (or serve it via a local server for ES module support)
3. Select a game mode from the dropdown and click **New Game**

> **Note:** Because the files use ES modules (`import`/`export`), you need to serve them from a local server — not open directly as `file://`. Use VS Code Live Server, `npx serve`, or any static server.

## Adjusting AI Difficulty

In `ai-opponent.js`, the default search depth is `3`. Change the `aiDepth` variable in `index.html` or pass a different depth to `getBestMoveAsync(state, depth)`:

| Depth | Speed | Strength |
|-------|-------|---------|
| 2 | Instant | Beginner |
| 3 | ~0.5s | Club |
| 4 | ~3–5s | Intermediate |

## Design Document

See [`design/game-design-document.md`](design/game-design-document.md) for full architecture decisions, state shape, board indexing, and AI design notes.
