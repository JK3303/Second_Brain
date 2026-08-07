# Chess Color Palette

## Attack Map Colors

| Role | Hex |
|------|-----|
| White attacks a square | `#61210F` — dark red/maroon |
| Black attacks a square | `#216869` — dark teal |

### Intensity (opacity overlay on board square)

| Attack count | Opacity |
|-------------|---------|
| 1 (low) | 35% |
| 2 (medium) | 60% |
| 3+ (high/full) | 85% |

### Split squares (attacked by both sides)

- Top half: `#61210F` at white attack intensity
- Bottom half: `#216869` at black attack intensity
- Implemented via CSS `linear-gradient(to bottom, ...)`

## Reserved (unassigned)

| Hex | Description |
|-----|-------------|
| `#c9a97a` | Warm beige |
| `#08142A` | Very dark navy |
| `#567568` | Muted sage green |
