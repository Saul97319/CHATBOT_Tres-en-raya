
// --- INTEGRACIÓN: activador de "El Gato" (Tres en Raya) ---
function shouldOpenTicTacToe(text){
  const t = (text||'').normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase()
const keywords = [
  /\b(vamos\s+a\s+)?(jugar|juguemos)\b.*\b(tres\s*rayas|tres\s*rayitas|tres\s+en\s+raya|gato|tic\s*-?\s*tac\s*-?\s*toe|tictactoe)\b/,
  /\b(jugar|quiero\s+jugar|abrir)\b.*\b(gato|tres\s*rayas|tres\s*rayitas|tres\s+en\s+raya|tic\s*-?\s*tac\s*-?\s*toe|tictactoe)\b/,
  /^\s*(gato|tres\s*rayas|tres\s*rayitas|tres\s+en\s+raya|tic\s*-?\s*tac\s*-?\s*toe|tictactoe)\s*$/
]

  return keywords.some(rx => rx.test(t))
}
function openTicTacToe(){
  try{
    window.open('game.html','_blank','noopener,noreferrer')
  }catch(e){
    // fallback same tab
    window.location.href = 'game.html'
  }
}

/* global localStorage, fetch */
const state = {
  serverOn: false,
  clientOn: false,
  history: [],
}

const chatEl = () => document.getElementById('chat')
const msgTpl = () => document.getElementById('tpl-msg')

function nowTime(){
  const d = new Date()
  return d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})
}

function addMessage(role, text){
  const tpl = msgTpl().content.cloneNode(true)
  const root = tpl.querySelector('.message')
  const bubble = tpl.querySelector('.bubble')
  const timeEl = tpl.querySelector('time')
  root.classList.add(role)
  bubble.textContent = text
  timeEl.textContent = nowTime()
  chatEl().appendChild(tpl)
  chatEl().scrollTop = chatEl().scrollHeight
}

function setStatus(id, on, onText, offText){
  const el = document.getElementById(id)
  el.classList.toggle('on', on)
  el.classList.toggle('off', !on)
  el.textContent = on ? onText : offText
}

async function api(path, options={}){
  const res = await fetch(path, {
    method: options.method || 'POST',
    headers: {'Content-Type':'application/json'},
    body: options.body ? JSON.stringify(options.body) : null
  })
  if(!res.ok){
    const t = await res.text()
    throw new Error(t || res.statusText)
  }
  return res.json()
}

function saveHistoryLocal(){
  try{ localStorage.setItem('qa_history', JSON.stringify(state.history)) }catch{}
  renderHistory()
}

function renderHistory(){
  const cont = document.getElementById('historyList')
  cont.innerHTML = ''
  state.history.slice().reverse().forEach(item => {
    const div = document.createElement('div')
    div.className = 'history-item'
    div.innerHTML = `<strong>Q:</strong> ${item.q}<br/><strong>A:</strong> ${item.a}<time>${new Date(item.t).toLocaleString()}</time>`
    cont.appendChild(div)
  })
}

async function refreshStatus(){
  try{
    const s = await fetch('/status').then(r => r.json())
    state.serverOn = s.server_on
    state.clientOn = s.client_on
    setStatus('serverStatus', s.server_on, 'Servidor: encendido', 'Servidor: apagado')
    setStatus('clientStatus', s.client_on, 'Cliente: conectado', 'Cliente: desconectado')
  }catch(e){
    console.warn(e)
  }
}

async function startServer(){
  const data = await api('/server/start')
  state.serverOn = data.server_on
  setStatus('serverStatus', true, 'Servidor: encendido', 'Servidor: apagado')
  addMessage('bot', 'Servidor encendido.')
}

async function stopServer(){
  const data = await api('/server/stop')
  state.serverOn = data.server_on
  setStatus('serverStatus', false, 'Servidor: encendido', 'Servidor: apagado')
  addMessage('bot', 'Servidor apagado.')
}

async function connectClient(){
  const data = await api('/client/connect')
  state.clientOn = true
  setStatus('clientStatus', true, 'Cliente: conectado', 'Cliente: desconectado')
  if(data.greeting){
    addMessage('bot', data.greeting)
  }
}

async function disconnectClient(){
  const data = await api('/client/disconnect')
  state.clientOn = false
  setStatus('clientStatus', false, 'Cliente: conectado', 'Cliente: desconectado')
  if(data.message){ addMessage('bot', data.message) }
}

async function sendMessage(ev){
  ev && ev.preventDefault()
  const input = document.getElementById('messageInput')
  const text = input.value.trim()
  
  // Integración juego "El Gato"
  if(shouldOpenTicTacToe(text)){
    addMessage('user', text)
    addMessage('bot', 'Abriendo el juego de tres rayas…')
    openTicTacToe()
    input.value = ''
    return
  }
if(!text){ return }
  if(!state.clientOn){ addMessage('bot', 'Conéctate primero.'); return }
  addMessage('user', text)
  input.value = ''
  try{
    const data = await api('/client/send', { body: { message: text } })
    const reply = data.reply || '(sin respuesta)'
    addMessage('bot', reply)
    state.history.push({q:text, a:reply, t:Date.now()})
    saveHistoryLocal()
  }catch(e){
    addMessage('bot', 'Error: ' + e.message)
  }
}

async function exitApp(){
  try{
    await api('/exit')
    addMessage('bot', 'Sesión cerrada. Puedes cerrar la pestaña.')
    await refreshStatus()
  }catch(e){
    addMessage('bot', 'Error al salir: ' + e.message)
  }
}

function initMenu(){
  const dropdown = document.querySelector('.dropdown')
  const btn = document.getElementById('menuBtn')
  btn.addEventListener('click', () => dropdown.classList.toggle('open'))
  document.addEventListener('click', (e) => {
    if(!dropdown.contains(e.target)){ dropdown.classList.remove('open') }
  })
}

function bindUI(){
  document.getElementById('btnStartServer').addEventListener('click', startServer)
  document.getElementById('btnStopServer').addEventListener('click', stopServer)
  document.getElementById('btnConnect').addEventListener('click', connectClient)
  document.getElementById('btnDisconnect').addEventListener('click', disconnectClient)
  document.getElementById('btnExitApp').addEventListener('click', exitApp)
  document.getElementById('composer').addEventListener('submit', sendMessage)
  document.getElementById('btnToggleHistory').addEventListener('click', () => {
    document.getElementById('historyPanel').classList.toggle('hidden')
  })
  document.getElementById('btnClearHistory').addEventListener('click', () => {
    state.history = []; saveHistoryLocal(); addMessage('bot', 'Historial local borrado.')
  })

  // Restore local history
  try{
    const raw = localStorage.getItem('qa_history')
    if(raw){ state.history = JSON.parse(raw) || [] }
  }catch{}
  renderHistory()
}

window.addEventListener('DOMContentLoaded', async () => {
  initMenu()
  bindUI()
  await refreshStatus()
})
