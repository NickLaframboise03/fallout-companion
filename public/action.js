// action.js


// --- State Model ---

const state = {

  characters: {},   // { [id]: { id, name, currentHP, maxHP, caps, luck } }

  currentTurn: {

    charId: null,

    AP: { move:0, major:0, minor:0, reaction:0 },

    luck: 0

  },

  actionLog: []     // [{ time, text }]

};


// --- Load characters (with fallback sample data) ---

async function loadCharacters() {

  try {

    const res = await fetch('/api/characters');

    if (!res.ok) throw new Error();

    const list = await res.json();

    list.forEach(c => state.characters[c.id] = c);

  } catch (e) {

    // Fallback sample so UI still shows something

    state.characters = {

      char1: { id:'char1', name:'Vault Dweller',    currentHP:12, maxHP:14, caps:50, luck:2 },

      char2: { id:'char2', name:'Brotherhood Paladin', currentHP:10, maxHP:12, caps:30, luck:3 }

    };

  }

}


// --- Helpers ---

function currentName() {

  const c = state.characters[state.currentTurn.charId];

  return c ? c.name : 'N/A';

}

function addLog(text) {

  const time = new Date().toLocaleTimeString();

  state.actionLog.unshift({ time, text });

  renderLog();

}


// --- Renderers ---

function renderCombatantSelect() {

  const sel = document.getElementById('select-combatant');

  sel.innerHTML = '';

  Object.values(state.characters).forEach(c => {

    const o = document.createElement('option');

    o.value = c.id;

    o.textContent = c.name;

    sel.append(o);

  });

  document.getElementById('btn-start').disabled = false;

}


function renderAPDisplay() {

  document.getElementById('ap-move').textContent     = state.currentTurn.AP.move;

  document.getElementById('ap-major').textContent    = state.currentTurn.AP.major;

  document.getElementById('ap-minor').textContent    = state.currentTurn.AP.minor;

  document.getElementById('ap-reaction').textContent = state.currentTurn.AP.reaction;

  document.getElementById('luck').textContent        = state.currentTurn.luck;

}


function renderSnapshot() {

  const snapName = document.getElementById('snap-name');

  const fill     = document.querySelector('.hp-fill');

  const snapCaps = document.getElementById('snap-caps');

  const c = state.characters[state.currentTurn.charId] || {};

  snapName.textContent = c.name || '–';

  const pct = c.maxHP ? (c.currentHP / c.maxHP * 100) : 0;

  fill.style.width = pct + '%';

  snapCaps.textContent = c.caps || 0;

}


function renderLog() {

  const ul = document.getElementById('log-list');

  if (!state.actionLog.length) {

    ul.innerHTML = '<li>No actions logged yet.</li>';

    return;

  }

  ul.innerHTML = state.actionLog

    .map(e => `<li>[${e.time}] ${e.text}</li>`)

    .join('');

}


// --- Event Handlers ---

function onStartTurn() {

  const id = document.getElementById('select-combatant').value;

  if (!id) return;

  state.currentTurn.charId = id;

  state.currentTurn.AP = { move:1, major:1, minor:1, reaction:1 };

  state.currentTurn.luck = state.characters[id].luck;

  // enable all action buttons

  document.querySelectorAll('#action-menu button').forEach(b => b.disabled = false);

  document.getElementById('btn-end').disabled = false;

  renderAPDisplay();

  renderSnapshot();

  addLog(`${currentName()} starts their turn.`);

}


function onEndTurn() {

  // simple round‐robin

  const ids = Object.keys(state.characters);

  let idx = ids.indexOf(state.currentTurn.charId);

  idx = (idx + 1) % ids.length;

  document.getElementById('select-combatant').value = ids[idx];

  onStartTurn();

}


function onMove() {

  const dist = parseInt(document.getElementById('move-dist').value, 10) || 0;

  if (state.currentTurn.AP.move <= 0) return alert('No Move AP left');

  state.currentTurn.AP.move -= 1;

  renderAPDisplay();

  addLog(`${currentName()} moves ${dist} tiles.`);

}


function onAttack() {

  if (state.currentTurn.AP.major <= 0) return alert('No Major AP left');

  state.currentTurn.AP.major -= 1;

  renderAPDisplay();

  addLog(`${currentName()} performs an Attack.`);

}


// stub handlers for other actions...

function onSkill()  { addLog(`${currentName()} does a Skill Check.`); }

function onAim()    { addLog(`${currentName()} takes aim.`); }

function onUseItem(){ addLog(`${currentName()} uses an item.`); }

function onReload() { addLog(`${currentName()} reloads their weapon.`); }

function onSwap()   { addLog(`${currentName()} swaps weapon.`); }

function onOverwatch() { addLog(`${currentName()} sets Overwatch.`); }

function onDodge()  { addLog(`${currentName()} Dodges.`); }

function onInterrupt(){ addLog(`${currentName()} Interrupts.`); }


// --- Bootstrap ---

async function init() {

  await loadCharacters();

  renderCombatantSelect();

  document.getElementById('btn-start').addEventListener('click', onStartTurn);

  document.getElementById('btn-end').addEventListener('click', onEndTurn);

  document.getElementById('do-move').addEventListener('click', onMove);

  document.getElementById('do-attack').addEventListener('click', onAttack);

  document.getElementById('do-skill').addEventListener('click', onSkill);

  document.getElementById('do-aim').addEventListener('click', onAim);

  document.getElementById('do-use-item').addEventListener('click', onUseItem);

  document.getElementById('do-reload').addEventListener('click', onReload);

  document.getElementById('do-swap').addEventListener('click', onSwap);

  document.getElementById('do-overwatch').addEventListener('click', onOverwatch);

  document.getElementById('do-dodge').addEventListener('click', onDodge);

  document.getElementById('do-interrupt').addEventListener('click', onInterrupt);

  // initial render

  renderAPDisplay();

  renderSnapshot();

  renderLog();

}


document.addEventListener('DOMContentLoaded', init);

