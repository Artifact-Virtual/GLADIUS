// server.js
const express = require('express');
const bodyParser = require('body-parser');
const submitLead = require('./api/submit');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static('public'));

app.post('/api/submit', submitLead);

app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
});
