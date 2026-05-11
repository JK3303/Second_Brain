// board-renderer.js — all DOM updates, no game logic

import { legalMovesFrom, color, type } from './chess-engine.js';

const UNICODE = {
  K: '♔', Q: '♕', R: '♖', B: '♗', N: '♘', P: '♙',
  k: '♚', q: '♛', r: '♜', b: '♝', n: '♞', p: '♟',
};

const COLORS = {
  light: '#f0d9b5',
  dark:  '#b58863',
  selected: '#7fc97f',
  legalDot: 'rgba(0,0,0,0.15)',
  legalRing: 'rgba(0,0,0,0.25)',
  lastMove: 'rgba(255,255,0,0.35)',
  check: 'rgba(220,50,50,0.55)',
};

let _state = null;
let _selectedSquare = null;
let _legalTargets = [];
let _lastMove = null;
let _onSquareClick = null;

function init(boardEl, onSquareClick) {
  _onSquareClick = onSquareClick;
  boardEl.innerHTML = '';
  boardEl.style.display = 'grid';
  boardEl.style.gridTemplateColumns = 'repeat(8, 1fr)';

  for (let i = 0; i < 64; i++) {
    const sq = document.createElement('div');
    sq.classList.add('square');
    sq.dataset.idx = i;
    sq.addEventListener('click', () => _onSquareClick(parseInt(sq.dataset.idx)));
    boardEl.appendChild(sq);
  }
}

function render(state, selectedSquare, lastMove) {
  _state = state;
  _selectedSquare = selectedSquare;
  _lastMove = lastMove;
  _legalTargets = selectedSquare !== null
    ? legalMovesFrom(state, selectedSquare).map(m => m.to)
    : [];

  const squares = document.querySelectorAll('.square');
  squares.forEach((sq, i) => {
    const r = Math.floor(i / 8);
    const f = i % 8;
    const isLight = (r + f) % 2 === 0;

    let bg = isLight ? COLORS.light : COLORS.dark;
    if (_lastMove && (i === _lastMove.from || i === _lastMove.to)) bg = blendColor(bg, COLORS.lastMove);
    if (i === _selectedSquare) bg = COLORS.selected;

    sq.style.backgroundColor = bg;
    sq.style.position = 'relative';
    sq.style.display = 'flex';
    sq.style.alignItems = 'center';
    sq.style.justifyContent = 'center';
    sq.style.cursor = 'pointer';
    sq.style.userSelect = 'none';

    // Clear children
    sq.innerHTML = '';

    const piece = state.board[i];

    // Check highlight on king
    if (state.status === 'check' || state.status === 'checkmate') {
      if (piece && type(piece) === 'K' && color(piece) === state.turn) {
        sq.style.backgroundColor = COLORS.check;
      }
    }

    // Legal move indicator
    if (_legalTargets.includes(i)) {
      const dot = document.createElement('div');
      if (piece !== null) {
        dot.style.cssText = `position:absolute;inset:0;border-radius:50%;box-shadow:inset 0 0 0 4px ${COLORS.legalRing};pointer-events:none;`;
      } else {
        dot.style.cssText = `width:30%;height:30%;border-radius:50%;background:${COLORS.legalDot};pointer-events:none;`;
      }
      sq.appendChild(dot);
    }

    // Piece
    if (piece) {
      const span = document.createElement('span');
      span.textContent = UNICODE[piece];
      span.style.cssText = 'font-size:clamp(20px,5vw,52px);line-height:1;position:relative;z-index:1;';
      sq.appendChild(span);
    }
  });

  renderRankFileLabels();
}

function renderRankFileLabels() {
  // Labels are baked into the HTML grid as overlay elements; skip if not present
  const labels = document.querySelectorAll('.rank-label, .file-label');
  labels.forEach(el => {
    const idx = parseInt(el.dataset.idx);
    if (el.classList.contains('rank-label')) el.textContent = 8 - Math.floor(idx / 8);
    if (el.classList.contains('file-label')) el.textContent = String.fromCharCode(97 + idx % 8);
  });
}

function renderMoveHistory(moves, containerEl) {
  containerEl.innerHTML = '';
  for (let i = 0; i < moves.length; i += 2) {
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;gap:6px;padding:2px 4px;font-size:13px;';
    const num = document.createElement('span');
    num.style.cssText = 'color:#888;min-width:22px;';
    num.textContent = `${Math.floor(i / 2) + 1}.`;
    const w = document.createElement('span');
    w.style.cssText = 'min-width:52px;';
    w.textContent = moves[i] || '';
    const b = document.createElement('span');
    b.textContent = moves[i + 1] || '';
    row.appendChild(num); row.appendChild(w); row.appendChild(b);
    containerEl.appendChild(row);
  }
  containerEl.scrollTop = containerEl.scrollHeight;
}

function renderCaptured(capturedWhite, capturedBlack, whiteEl, blackEl) {
  const render = (pieces, el) => {
    el.textContent = pieces.map(p => UNICODE[p]).join(' ') || '—';
  };
  render(capturedWhite, whiteEl);
  render(capturedBlack, blackEl);
}

function renderStatus(state, el) {
  const msgs = {
    playing: `${state.turn === 'white' ? 'White' : 'Black'} to move`,
    check:    `${state.turn === 'white' ? 'White' : 'Black'} is in check`,
    checkmate:`Checkmate — ${state.turn === 'white' ? 'Black' : 'White'} wins`,
    stalemate:'Stalemate — Draw',
    draw:     'Draw (50-move rule)',
  };
  el.textContent = msgs[state.status] || '';
}

function showPromotionModal(color, onChoice) {
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:100;';
  const box = document.createElement('div');
  box.style.cssText = 'background:#fff;border-radius:8px;padding:16px;display:flex;gap:12px;';
  const pieces = color === 'white' ? ['Q','R','B','N'] : ['q','r','b','n'];
  pieces.forEach(p => {
    const btn = document.createElement('button');
    btn.textContent = UNICODE[p];
    btn.style.cssText = 'font-size:40px;background:none;border:2px solid #ccc;border-radius:6px;padding:6px 10px;cursor:pointer;';
    btn.addEventListener('click', () => { overlay.remove(); onChoice(p.toUpperCase()); });
    box.appendChild(btn);
  });
  overlay.appendChild(box);
  document.body.appendChild(overlay);
}

// Simple color blending for highlights
function blendColor(base, overlay) {
  return overlay; // simplified — overlay is rgba, browser compositing handles it
}

export { init, render, renderMoveHistory, renderCaptured, renderStatus, showPromotionModal };
