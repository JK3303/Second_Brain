// ai-opponent.js — minimax with alpha-beta pruning

import { allLegalMoves, applyMove, computeStatus, color, type } from './chess-engine.js?v=2';

// ---------- Piece values ----------

const PIECE_VALUE = { K: 20000, Q: 900, R: 500, B: 330, N: 320, P: 100 };

// ---------- Piece-square tables (from white's perspective, index 0=a8) ----------
// Encourages good piece placement without an opening book.

const PST = {
  P: [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
  ],
  N: [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
  ],
  B: [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20,
  ],
  R: [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
  ],
  Q: [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20,
  ],
  K: [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
  ],
};

// ---------- Evaluation ----------

function evaluate(state) {
  let score = 0;
  for (let i = 0; i < 64; i++) {
    const piece = state.board[i];
    if (!piece) continue;
    const t = type(piece);
    const c = color(piece);
    const pstIdx = c === 'white' ? i : 63 - i;
    const val = PIECE_VALUE[t] + (PST[t] ? PST[t][pstIdx] : 0);
    score += c === 'white' ? val : -val;
  }
  return score;
}

// ---------- Move ordering (captures first) ----------

function orderMoves(state, moves) {
  return moves.slice().sort((a, b) => {
    const capA = state.board[a.to] !== null ? 1 : 0;
    const capB = state.board[b.to] !== null ? 1 : 0;
    return capB - capA;
  });
}

// ---------- Minimax ----------

function minimax(state, depth, alpha, beta, maximizing) {
  const status = computeStatus(state);
  if (depth === 0 || status === 'checkmate' || status === 'stalemate' || status === 'draw') {
    if (status === 'checkmate') return maximizing ? -100000 : 100000;
    if (status === 'stalemate' || status === 'draw') return 0;
    return evaluate(state);
  }

  const moves = orderMoves(state, allLegalMoves(state));

  if (maximizing) {
    let best = -Infinity;
    for (const move of moves) {
      const next = applyMove(state, { ...move, promotion: move.promotion || 'Q' });
      best = Math.max(best, minimax(next, depth - 1, alpha, beta, false));
      alpha = Math.max(alpha, best);
      if (beta <= alpha) break;
    }
    return best;
  } else {
    let best = Infinity;
    for (const move of moves) {
      const next = applyMove(state, { ...move, promotion: move.promotion || 'Q' });
      best = Math.min(best, minimax(next, depth - 1, alpha, beta, true));
      beta = Math.min(beta, best);
      if (beta <= alpha) break;
    }
    return best;
  }
}

// ---------- Best move ----------

function getBestMove(state, depth = 3) {
  const moves = orderMoves(state, allLegalMoves(state));
  if (moves.length === 0) return null;

  const maximizing = state.turn === 'white';
  let bestMove = null;
  let bestScore = maximizing ? -Infinity : Infinity;

  for (const move of moves) {
    const next = applyMove(state, { ...move, promotion: move.promotion || 'Q' });
    const score = minimax(next, depth - 1, -Infinity, Infinity, !maximizing);
    if (maximizing ? score > bestScore : score < bestScore) {
      bestScore = score;
      bestMove = move;
    }
  }

  return bestMove;
}

// Async wrapper so the UI can stay responsive during search
function getBestMoveAsync(state, depth = 3) {
  return new Promise(resolve => {
    setTimeout(() => resolve(getBestMove(state, depth)), 0);
  });
}

export { getBestMove, getBestMoveAsync, evaluate };
