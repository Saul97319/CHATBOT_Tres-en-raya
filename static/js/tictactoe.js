
/* Minimax Tic-Tac-Toe with simple alpha-beta pruning */
(() => {
  const boardEl = document.getElementById('board')
  const statusEl = document.getElementById('status')
  const selMark = document.getElementById('humanMark')
  const btnNew = document.getElementById('btnNew')
  const btnBack = document.getElementById('btnBack')

  const EMPTY = ''
  let board = Array(9).fill(EMPTY)
  let human = 'X'
  let ai = 'O'
  let gameOver = false

  function draw(){
    boardEl.innerHTML = ''
    board.forEach((val, i) => {
      const d = document.createElement('div')
      d.className = 'cell' + (gameOver ? ' disabled' : '')
      d.setAttribute('role','gridcell')
      d.setAttribute('aria-label', val || 'vacío')
      d.dataset.idx = i
      d.textContent = val
      d.addEventListener('click', () => userMove(i))
      boardEl.appendChild(d)
    })
  }

  function lines(){
    return [
      [0,1,2],[3,4,5],[6,7,8],
      [0,3,6],[1,4,7],[2,5,8],
      [0,4,8],[2,4,6]
    ]
  }

  function winner(b){
    for(const [a,c,d] of lines()){
      if(b[a] && b[a] === b[c] && b[a] === b[d]) return {mark:b[a], line:[a,c,d]}
    }
    if(b.every(v => v)) return {mark:'draw', line:[]}
    return null
  }

  function setStatus(msg){ statusEl.textContent = msg }

  function restart(){
    board = Array(9).fill(EMPTY)
    gameOver = false
    human = selMark.value || 'X'
    ai = human === 'X' ? 'O' : 'X'
    draw()
    setStatus('Tu turno')
    if(human === 'O'){
      // AI starts
      aiMove()
    }
  }

  function userMove(i){
    if(gameOver || board[i]) return
    board[i] = human
    const w = winner(board)
    if(w){
      endGame(w)
      return
    }
    aiMove()
  }

  function aiMove(){
    const { index } = bestMove(board, ai, -Infinity, Infinity)
    if(index !== undefined){
      board[index] = ai
    }
    const w = winner(board)
    if(w){
      endGame(w)
    }else{
      draw()
      setStatus('Tu turno')
    }
  }

  function bestMove(b, player, alpha, beta){
    const w = winner(b)
    if(w){
      if(w.mark === ai) return { score: 10 }
      if(w.mark === human) return { score: -10 }
      return { score: 0 }
    }
    // Prefer center, corners for speed (move ordering)
    const order = [4,0,2,6,8,1,3,5,7]
    let best = { score: player===ai ? -Infinity : Infinity, index: undefined }
    for(const i of order){
      if(b[i]) continue
      b[i] = player
      const next = bestMove(b, player===ai ? human : ai, alpha, beta)
      b[i] = EMPTY
      const score = next.score + (player===ai ? -1 : 1) // prefer faster wins / slower losses
      if(player === ai){
        if(score > best.score){ best = { score, index: i } }
        alpha = Math.max(alpha, score)
      }else{
        if(score < best.score){ best = { score, index: i } }
        beta = Math.min(beta, score)
      }
      if(beta <= alpha) break
    }
    return best
  }

  function endGame(w){
    gameOver = true
    draw()
    // highlight line
    if(w.mark !== 'draw' && w.line.length){
      w.line.forEach(i => boardEl.children[i].classList.add('win'))
      setStatus(w.mark === human ? '¡Ganaste! 🎉' : 'Gana la IA 🤖')
    }else{
      setStatus('Empate 🤝')
    }
    Array.from(boardEl.children).forEach(c => c.classList.add('disabled'))
  }

  // Events
  selMark.addEventListener('change', restart)
  btnNew.addEventListener('click', restart)
  btnBack.addEventListener('click', () => window.close() || (window.location.href = 'index.html'))

  document.addEventListener('keydown', (e) => {
    if(e.key.toLowerCase() === 'n') restart()
    if(e.key.toLowerCase() === 'b') window.close()
  })

  // Init
  restart()
})();
