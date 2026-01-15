import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { scrapeAndExtract } from './scraper.js';

const app = express();
app.use(cors());
app.use(express.json());

const DATA_PATH = path.join(path.resolve(), 'api', 'results.json');

app.post('/api/scrape', async (req, res) => {
  try {
    let urls = req.body.urls || [];
    if (!Array.isArray(urls)) {
      if (typeof req.body.url === 'string') urls = [req.body.url];
      else return res.status(400).json({ error: 'Missing urls' });
    }
    const results = [];
    for (const url of urls) {
      try {
        const result = await scrapeAndExtract(url);
        results.push(result);
      } catch (err) {
        results.push({ url, error: err.message });
      }
    }
    let allResults = [];
    if (fs.existsSync(DATA_PATH)) {
      allResults = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
    }
    allResults.push(...results);
    fs.writeFileSync(DATA_PATH, JSON.stringify(allResults, null, 2));
    res.json({ success: true, data: results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/results', (req, res) => {
  if (!fs.existsSync(DATA_PATH)) return res.json([]);
  const results = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
  res.json(results);
});

const PORT = 5174;
app.listen(PORT, () => console.log(`API server running on port ${PORT}`));
