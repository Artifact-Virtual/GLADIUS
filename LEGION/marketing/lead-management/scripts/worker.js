// scripts/worker.js
const fs = require('fs');
const { default: fetch } = require('node-fetch');

async function enrichLead({ name, email }) {
  const company = email?.split('@')[1]?.split('.')[0];
  const enriched = {
    name,
    email,
    company,
    location: '📍 Simulated City',
    tags: ['lead', 'new'],
    score: Math.floor(Math.random() * 100)
  };

  console.log(`🔍 Enriched: ${JSON.stringify(enriched)}`);
  return enriched;
}

async function run() {
  console.log('🧠 Worker started…');
  const leads = JSON.parse(fs.readFileSync('./data/leads.json', 'utf8'));

  for (const lead of leads) {
    const enriched = await enrichLead(lead);
    fs.appendFileSync('./data/enriched.json', JSON.stringify(enriched) + ',\n');
  }
}

run();
