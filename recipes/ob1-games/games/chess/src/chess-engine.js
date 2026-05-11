// chess-engine.js — pure game logic, no DOM

const PIECES = { K:'K', Q:'Q', R:'R', B:'B', N:'N', P:'P' };

const INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

// ---------- State ----------

function createState() {
  return parseFEN(INITIAL_FEN);
}

function parseFEN(fen) {
  const parts = fen.split(' ');
  const board = Array(64).fill(null);
  let idx = 0;
  for (const ch of parts[0]) {
    if (ch === '/') continue;
    if (ch >= '1' && ch <= '8') { idx += parseInt(ch); continue; }
    board[idx++] = ch;
  }
  const turn = parts[1] === 'w' ? 'white' : 'black';
  const castlingStr = parts[2];
  const castling = {
    wK: castlingStr.includes('K'),
    wQ: castlingStr.includes('Q'),
    bK: castlingStr.includes('k'),
    bQ: castlingStr.includes('q'),
  };
  const epStr = parts[3];
  const enPassant = epStr === '-' ? null : algebraicToIndex(epStr);
  const halfMoveClock = parseInt(parts[4]) || 0;
  const fullMoveNumber = parseInt(parts[5]) || 1;
  return { board, turn, castling, enPassant, halfMoveClock, fullMoveNumber, status: 'playing' };
}

function cloneState(state) {
  return {
    board: [...state.board],
    turn: state.turn,
    castling: { ...state.castling },
    enPassant: state.enPassant,
    halfMoveClock: state.halfMoveClock,
    fullMoveNumber: state.fullMoveNumber,
    status: state.status,
  };
}

// ---------- Coordinates ----------

function algebraicToIndex(sq) {
  const file = sq.charCodeAt(0) - 97;
  const rank = parseInt(sq[1]) - 1;
  return (7 - rank) * 8 + file;
}

function indexToAlgebraic(idx) {
  const file = String.fromCharCode(97 + (idx % 8));
  const rank = 8 - Math.floor(idx / 8);
  return file + rank;
}

function fileOf(idx) { return idx % 8; }
function rankOf(idx) { return Math.floor(idx / 8); }

// ---------- Piece helpers ----------

function isWhite(piece) { return piece !== null && piece === piece.toUpperCase(); }
function isBlack(piece) { return piece !== null && piece === piece.toLowerCase(); }
function color(piece) { return piece === null ? null : (isWhite(piece) ? 'white' : 'black'); }
function type(piece) { return piece === null ? null : piece.toUpperCase(); }
function opponent(turn) { return turn === 'white' ? 'black' : 'white'; }
function ownPiece(piece, turn) { return color(piece) === turn; }

// ---------- Raw (pseudo-legal) move generation ----------

function pseudoLegalMoves(state, from) {
  const piece = state.board[from];
  if (!piece || color(piece) !== state.turn) return [];
  const t = type(piece);
  const moves = [];

  if (t === 'P') addPawnMoves(state, from, moves);
  else if (t === 'N') addKnightMoves(state, from, moves);
  else if (t === 'B') addSlidingMoves(state, from, moves, [[-1,-1],[-1,1],[1,-1],[1,1]]);
  else if (t === 'R') addSlidingMoves(state, from, moves, [[-1,0],[1,0],[0,-1],[0,1]]);
  else if (t === 'Q') addSlidingMoves(state, from, moves, [[-1,-1],[-1,1],[1,-1],[1,1],[-1,0],[1,0],[0,-1],[0,1]]);
  else if (t === 'K') addKingMoves(state, from, moves);

  return moves;
}

function addPawnMoves(state, from, moves) {
  const { board, turn, enPassant } = state;
  const dir = turn === 'white' ? -1 : 1;
  const startRank = turn === 'white' ? 6 : 1;
  const r = rankOf(from), f = fileOf(from);

  const one = from + dir * 8;
  if (one >= 0 && one < 64 && board[one] === null) {
    moves.push({ from, to: one });
    const two = from + dir * 16;
    if (r === startRank && board[two] === null) moves.push({ from, to: two });
  }
  for (const df of [-1, 1]) {
    if (f + df < 0 || f + df > 7) continue;
    const cap = from + dir * 8 + df;
    if (cap >= 0 && cap < 64 && board[cap] !== null && color(board[cap]) !== turn)
      moves.push({ from, to: cap });
    if (cap === enPassant)
      moves.push({ from, to: cap, enPassant: true });
  }
}

function addKnightMoves(state, from, moves) {
  const { board, turn } = state;
  const r = rankOf(from), f = fileOf(from);
  for (const [dr, df] of [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]]) {
    const nr = r + dr, nf = f + df;
    if (nr < 0 || nr > 7 || nf < 0 || nf > 7) continue;
    const to = nr * 8 + nf;
    if (!ownPiece(board[to], turn)) moves.push({ from, to });
  }
}

function addSlidingMoves(state, from, moves, dirs) {
  const { board, turn } = state;
  for (const [dr, df] of dirs) {
    let r = rankOf(from), f = fileOf(from);
    while (true) {
      r += dr; f += df;
      if (r < 0 || r > 7 || f < 0 || f > 7) break;
      const to = r * 8 + f;
      if (ownPiece(board[to], turn)) break;
      moves.push({ from, to });
      if (board[to] !== null) break;
    }
  }
}

function addKingMoves(state, from, moves) {
  const { board, turn, castling } = state;
  const r = rankOf(from), f = fileOf(from);
  for (const [dr, df] of [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]) {
    const nr = r + dr, nf = f + df;
    if (nr < 0 || nr > 7 || nf < 0 || nf > 7) continue;
    const to = nr * 8 + nf;
    if (!ownPiece(board[to], turn)) moves.push({ from, to });
  }
  // Castling
  if (turn === 'white' && from === 60) {
    if (castling.wK && board[61] === null && board[62] === null && board[63] === 'R')
      moves.push({ from, to: 62, castling: 'K' });
    if (castling.wQ && board[59] === null && board[58] === null && board[57] === null && board[56] === 'R')
      moves.push({ from, to: 58, castling: 'Q' });
  }
  if (turn === 'black' && from === 4) {
    if (castling.bK && board[5] === null && board[6] === null && board[7] === 'r')
      moves.push({ from, to: 6, castling: 'K' });
    if (castling.bQ && board[3] === null && board[2] === null && board[1] === null && board[0] === 'r')
      moves.push({ from, to: 2, castling: 'Q' });
  }
}

// ---------- Apply move ----------

function applyMove(state, move) {
  const next = cloneState(state);
  const { board } = next;
  const piece = board[move.from];
  const t = type(piece);

  // En passant capture
  if (move.enPassant) {
    const capIdx = move.to + (state.turn === 'white' ? 8 : -8);
    board[capIdx] = null;
  }

  // Castling — move the rook
  if (move.castling) {
    if (move.castling === 'K' && state.turn === 'white') { board[63] = null; board[61] = 'R'; }
    if (move.castling === 'Q' && state.turn === 'white') { board[56] = null; board[59] = 'R'; }
    if (move.castling === 'K' && state.turn === 'black') { board[7] = null; board[5] = 'r'; }
    if (move.castling === 'Q' && state.turn === 'black') { board[0] = null; board[3] = 'r'; }
  }

  board[move.to] = move.promotion
    ? (state.turn === 'white' ? move.promotion.toUpperCase() : move.promotion.toLowerCase())
    : piece;
  board[move.from] = null;

  // Update castling rights
  if (t === 'K') {
    if (state.turn === 'white') { next.castling.wK = false; next.castling.wQ = false; }
    else { next.castling.bK = false; next.castling.bQ = false; }
  }
  if (t === 'R') {
    if (move.from === 63) next.castling.wK = false;
    if (move.from === 56) next.castling.wQ = false;
    if (move.from === 7)  next.castling.bK = false;
    if (move.from === 0)  next.castling.bQ = false;
  }
  // Rook captured — remove castling right
  if (move.to === 63) next.castling.wK = false;
  if (move.to === 56) next.castling.wQ = false;
  if (move.to === 7)  next.castling.bK = false;
  if (move.to === 0)  next.castling.bQ = false;

  // En passant target
  next.enPassant = null;
  if (t === 'P' && Math.abs(move.to - move.from) === 16) {
    next.enPassant = (move.from + move.to) / 2;
  }

  // Clocks
  next.halfMoveClock = (t === 'P' || board[move.to] !== null) ? 0 : state.halfMoveClock + 1;
  if (state.turn === 'black') next.fullMoveNumber++;

  next.turn = opponent(state.turn);
  return next;
}

// ---------- Check detection ----------

function isSquareAttacked(board, sq, byColor) {
  // Check by knights
  const r = rankOf(sq), f = fileOf(sq);
  for (const [dr, df] of [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]]) {
    const nr = r + dr, nf = f + df;
    if (nr < 0 || nr > 7 || nf < 0 || nf > 7) continue;
    const p = board[nr * 8 + nf];
    if (p && color(p) === byColor && type(p) === 'N') return true;
  }
  // Sliding pieces (Q, R, B)
  for (const [dr, df] of [[-1,0],[1,0],[0,-1],[0,1]]) {
    let cr = r, cf = f;
    while (true) {
      cr += dr; cf += df;
      if (cr < 0 || cr > 7 || cf < 0 || cf > 7) break;
      const p = board[cr * 8 + cf];
      if (!p) continue;
      if (color(p) === byColor && (type(p) === 'R' || type(p) === 'Q')) return true;
      break;
    }
  }
  for (const [dr, df] of [[-1,-1],[-1,1],[1,-1],[1,1]]) {
    let cr = r, cf = f;
    while (true) {
      cr += dr; cf += df;
      if (cr < 0 || cr > 7 || cf < 0 || cf > 7) break;
      const p = board[cr * 8 + cf];
      if (!p) continue;
      if (color(p) === byColor && (type(p) === 'B' || type(p) === 'Q')) return true;
      break;
    }
  }
  // Pawns
  const pDir = byColor === 'white' ? 1 : -1;
  for (const df of [-1, 1]) {
    const nr = r + pDir, nf = f + df;
    if (nr < 0 || nr > 7 || nf < 0 || nf > 7) continue;
    const p = board[nr * 8 + nf];
    if (p && color(p) === byColor && type(p) === 'P') return true;
  }
  // King
  for (const [dr, df] of [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]) {
    const nr = r + dr, nf = f + df;
    if (nr < 0 || nr > 7 || nf < 0 || nf > 7) continue;
    const p = board[nr * 8 + nf];
    if (p && color(p) === byColor && type(p) === 'K') return true;
  }
  return false;
}

function findKing(board, kingColor) {
  const k = kingColor === 'white' ? 'K' : 'k';
  return board.indexOf(k);
}

function inCheck(state, kingColor) {
  const kSq = findKing(state.board, kingColor);
  if (kSq === -1) return false;
  return isSquareAttacked(state.board, kSq, opponent(kingColor));
}

// ---------- Legal move generation ----------

function legalMovesFrom(state, from) {
  const piece = state.board[from];
  if (!piece || color(piece) !== state.turn) return [];

  const pseudo = pseudoLegalMoves(state, from);
  const legal = [];

  for (const move of pseudo) {
    // Validate castling: squares king passes through must not be attacked
    if (move.castling) {
      const passThroughs = move.castling === 'K' ? [from + 1, from + 2] : [from - 1, from - 2];
      const opp = opponent(state.turn);
      if (isSquareAttacked(state.board, from, opp)) continue;
      if (passThroughs.some(sq => isSquareAttacked(state.board, sq, opp))) continue;
    }

    const next = applyMove(state, move);
    if (!inCheck(next, state.turn)) legal.push(move);
  }

  return legal;
}

function allLegalMoves(state) {
  const moves = [];
  for (let i = 0; i < 64; i++) {
    if (color(state.board[i]) === state.turn) {
      moves.push(...legalMovesFrom(state, i));
    }
  }
  return moves;
}

// ---------- Game status ----------

function computeStatus(state) {
  const moves = allLegalMoves(state);
  const checked = inCheck(state, state.turn);

  if (moves.length === 0) return checked ? 'checkmate' : 'stalemate';
  if (state.halfMoveClock >= 100) return 'draw';
  if (checked) return 'check';
  return 'playing';
}

// ---------- Promotion helpers ----------

function needsPromotion(state, move) {
  const piece = state.board[move.from];
  if (type(piece) !== 'P') return false;
  const toRank = rankOf(move.to);
  return (color(piece) === 'white' && toRank === 0) || (color(piece) === 'black' && toRank === 7);
}

// ---------- Algebraic notation ----------

function moveToAlgebraic(state, move) {
  const piece = state.board[move.from];
  const t = type(piece);
  const captured = state.board[move.to] !== null || move.enPassant;

  let notation = '';
  if (move.castling === 'K') return 'O-O';
  if (move.castling === 'Q') return 'O-O-O';

  if (t !== 'P') notation += t;
  if (captured) {
    if (t === 'P') notation += indexToAlgebraic(move.from)[0];
    notation += 'x';
  }
  notation += indexToAlgebraic(move.to);
  if (move.promotion) notation += '=' + move.promotion.toUpperCase();

  const next = applyMove(state, move);
  const nextStatus = computeStatus(next);
  if (nextStatus === 'checkmate') notation += '#';
  else if (nextStatus === 'check') notation += '+';

  return notation;
}

// ---------- Public API ----------

export {
  createState,
  parseFEN,
  cloneState,
  legalMovesFrom,
  allLegalMoves,
  applyMove,
  computeStatus,
  needsPromotion,
  moveToAlgebraic,
  inCheck,
  isSquareAttacked,
  indexToAlgebraic,
  algebraicToIndex,
  color,
  type,
  opponent,
};
