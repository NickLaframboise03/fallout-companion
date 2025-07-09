const express = require('express');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 25560;
const CHAR_DIR = path.join(__dirname, 'characters');
const VERSION_DIR = path.join(CHAR_DIR, 'versions');

const app = express();
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

app.listen(PORT, () => {
  console.log(`🚀 Express server running at http://localhost:${PORT}`);
});
