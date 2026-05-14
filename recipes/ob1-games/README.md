# OB1 Games

A multi-game development platform built inside OB1. This folder is the source of truth for all game design documents, source code, and assets. Code is manually exported to the target game platform (web browser, Unity, etc.).

## Structure

```
recipes/ob1-games/
  framework/          — Shared conventions, coding standards, and reusable utilities
  games/
    chess/            — Chess (web browser, JavaScript)
      design/         — Game design document and notes
      src/            — Complete, copy-ready source code
      skills/         — Claude Code skills for ongoing development
```

## How to Use

1. Browse the `games/` folder for the game you want to work on
2. Read the `design/` docs to understand the game's architecture and decisions
3. Copy files from `src/` into your game platform project
4. Use skills in `skills/` to extend or iterate on the game with AI assistance

## Games

| Game | Platform | Status |
|------|----------|--------|
| [Chess](games/chess/) | Web Browser (JS) | In Progress |

## Adding a New Game

1. Create `games/<game-name>/` with `design/`, `src/`, and `skills/` subfolders
2. Write a game design document in `design/game-design-document.md`
3. Add an entry to the table above
