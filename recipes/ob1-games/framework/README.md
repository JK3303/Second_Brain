# Framework

Shared conventions for all OB1 Games.

## Code Standards

- **Language:** Vanilla JavaScript (ES2020+). No build tools, no frameworks — files drop straight into a browser.
- **Modules:** Each game is split into `chess-engine.js` (pure logic, no DOM), `board-renderer.js` (DOM only), and `ai-opponent.js` (AI only). Logic never touches the DOM; renderer never contains rules.
- **State:** Game state is a plain JS object. Never stored in the DOM.
- **Naming:** `camelCase` for variables/functions, `SCREAMING_SNAKE_CASE` for constants.

## File Conventions

Every game under `games/<name>/src/` should have:

| File | Purpose |
|------|---------|
| `index.html` | Entry point and UI shell |
| `style.css` | All styling |
| `<game>-engine.js` | Pure game logic — rules, state, validation |
| `<game>-renderer.js` | DOM rendering only |
| `ai-opponent.js` | AI logic |

## Exporting to a Platform

Copy the entire `src/` folder to your project. All files use relative paths and have no external dependencies unless noted in the game's README.
