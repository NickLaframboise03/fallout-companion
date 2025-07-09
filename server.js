// server.js

const http = require('http');

const fs   = require('fs');

const path = require('path');


const PORT = 25560;


// Minimal mime‐type map

const MIME = {

  '.html': 'text/html',

  '.css':  'text/css',

  '.js':   'application/javascript',

  '.pdf':  'application/pdf',

  '.png':  'image/png',

  '.jpg':  'image/jpeg',

  '.ico':  'image/x-icon'

};


const server = http.createServer((req, res) => {

  // 1. Determine the file we want to serve

  //    Strip query string (e.g. ?foo=bar) and leading slashes

  let reqPath = req.url.split('?')[0].replace(/^\/+/, '');  

  if (!reqPath) reqPath = 'index.html';   // default to index.html


  const filePath = path.join(__dirname, reqPath);

  const ext      = path.extname(filePath).toLowerCase();

  const type     = MIME[ext] || 'application/octet-stream';


  // 2. Read and serve the file

  fs.readFile(filePath, (err, data) => {

    if (err) {

      // File not found or other error

      if (err.code === 'ENOENT') {

        res.writeHead(404, { 'Content-Type': 'text/plain' });

        res.end('404 Not Found');

      } else {

        res.writeHead(500, { 'Content-Type': 'text/plain' });

        res.end('500 Server Error');

      }

      return;

    }


    // 3. Send it!

    res.writeHead(200, { 'Content-Type': type });

    res.end(data);

  });

});


server.listen(PORT, () => {

  console.log(`🚀 Server running at http://localhost:${PORT}`);

});

