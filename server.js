const express = require('express');
const fs = require('fs');
const path = require('path');
const http = require('http');
const { Server } = require('socket.io');

const PORT = process.env.PORT || 25560;
const CHAR_DIR = path.join(__dirname, 'characters');
const VERSION_DIR = path.join(CHAR_DIR, 'versions');
const STATE_FILE = path.join(__dirname, 'state.json');

const app = express();
const httpServer = http.createServer(app);
const io = new Server(httpServer);
app.use(express.json());

app.use(express.static(path.join(__dirname, 'public')));

function readCharacter(id) {
  const file = path.join(CHAR_DIR, `${id}.json`);
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writeCharacter(id, data) {
  fs.mkdirSync(VERSION_DIR, { recursive: true });
  const versionPath = path.join(VERSION_DIR, `${id}-${Date.now()}.json`);
  fs.writeFileSync(versionPath, JSON.stringify(data, null, 2));
  const file = path.join(CHAR_DIR, `${id}.json`);
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

let sharedState = { currentTurn: { charId: null, AP: { move:0, major:0, minor:0, reaction:0 }, luck:0 }, actionLog: [] };

function loadState() {
  try {
    sharedState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch (err) {
    sharedState = { currentTurn: { charId: null, AP: { move:0, major:0, minor:0, reaction:0 }, luck:0 }, actionLog: [] };
  }
}

function saveState() {
  fs.writeFileSync(STATE_FILE, JSON.stringify(sharedState, null, 2));
}

function addLog(text) {
  const entry = { time: new Date().toISOString(), text };
  sharedState.actionLog.unshift(entry);
  if (sharedState.actionLog.length > 50) sharedState.actionLog.pop();
  saveState();
  io.emit('state', sharedState);
}

loadState();

app.get('/api/characters', (req, res) => {
  try {
    const files = fs.readdirSync(CHAR_DIR).filter(f => f.endsWith('.json'));
    const list = files.map(f => {
      const id = path.basename(f, '.json');
      const data = JSON.parse(fs.readFileSync(path.join(CHAR_DIR, f), 'utf8'));
      return { id, name: data.character?.name || id };
    });
    res.json(list);
  } catch (err) {
    res.status(500).json({ error: 'Failed to list characters' });
  }
});

app.get('/api/characters/:id', (req, res) => {
  const id = req.params.id;
  try {
    const data = readCharacter(id);
    res.json(data);
  } catch (err) {
    res.status(404).json({ error: 'Character not found' });
  }
});

app.get('/api/characters/:id/pdf', (req, res) => {
  const id = req.params.id;
  try {
    const data = readCharacter(id);
    const name = data.character?.name || id;
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const pdfPath = path.join(__dirname, 'public', 'pdf', `${slug}.pdf`);
    if (fs.existsSync(pdfPath)) {
      res.sendFile(pdfPath);
    } else {
      res.status(404).json({ error: 'PDF not found' });
    }
  } catch (err) {
    res.status(404).json({ error: 'Character not found' });
  }
});

app.get('/api/state', (req, res) => {
  res.json(sharedState);
});

function merge(target, src) {
  for (const key of Object.keys(src)) {
    if (src[key] && typeof src[key] === 'object' && !Array.isArray(src[key])) {
      if (!target[key] || typeof target[key] !== 'object') target[key] = {};
      merge(target[key], src[key]);
    } else {
      target[key] = src[key];
    }
  }
}

app.post('/api/characters/:id/state', (req, res) => {
  const id = req.params.id;
  try {
    const data = readCharacter(id);
    merge(data, req.body);
    writeCharacter(id, data);
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: 'Failed to update character' });
  }
});

io.on('connection', (socket) => {
  socket.emit('state', sharedState);

  socket.on('startTurn', ({ charId }) => {
    try {
      const data = readCharacter(charId);
      const luck = data.derived?.luck_points || 0;
      sharedState.currentTurn = {
        charId,
        AP: { move:1, major:1, minor:1, reaction:1 },
        luck
      };
      addLog(`${data.character?.name || charId} starts their turn.`);
      saveState();
      io.emit('state', sharedState);
    } catch (err) {
      console.error('startTurn failed', err);
    }
  });

  socket.on('endTurn', () => {
    if (sharedState.currentTurn.charId) {
      addLog(`${sharedState.currentTurn.charId} ends their turn.`);
    }
    sharedState.currentTurn = { charId:null, AP:{move:0, major:0, minor:0, reaction:0}, luck:0 };
    saveState();
    io.emit('state', sharedState);
  });

  socket.on('spendAP', (type) => {
    const ap = sharedState.currentTurn.AP[type];
    if (ap > 0) {
      sharedState.currentTurn.AP[type] -= 1;
      saveState();
      io.emit('state', sharedState);
    }
  });

  socket.on('log', (text) => {
    addLog(text);
  });
});

httpServer.listen(PORT, () => {
  console.log(`🚀 Express server running at http://localhost:${PORT}`);
});
