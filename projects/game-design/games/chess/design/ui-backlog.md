# Chess UI Backlog

Potential UI enhancements to add in future sessions.

## Visual Style
- Different color theme options
- Custom board colors
- 3D-look pieces
- Wood / marble textures via CSS

## Piece Style
- Swap unicode for SVG pieces (sharper, more polished)

## Layout
- Different panel arrangement
- Fullscreen board option
- Floating panel

## Win Probability Tracker
- Bar showing win probability for each player, updating after every move
- Use existing `evaluate()` centipawn score converted to % via sigmoid function (same formula as Lichess)
- `win% = 50 + 50 * (2/(1 + exp(-0.00368208 * cp)) - 1)`

## Extra Features
- Move sound effects
- Move animation
- Clock / timer
- Opening name display
- Board coordinates (rank/file labels)
- Flip board button
