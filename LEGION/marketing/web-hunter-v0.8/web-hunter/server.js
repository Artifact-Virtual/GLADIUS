const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const Scraper = require('./hunter/scraper');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(bodyParser.json());

app.get('/status', (req, res) => {
    res.json({ status: 'ready' });
});

app.post('/start', async (req, res) => {
    try {
        const configPath = path.join(__dirname, 'config/profiles.json');
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        const target = config.searchTargets[0].url;
        const scraper = new Scraper();
        await scraper.init();
        const result = await scraper.scrape(target);
        await scraper.close();
        // Save result to leads.json
        const leadsPath = path.join(__dirname, 'data/leads.json');
        let leads = { leads: [] };
        if (fs.existsSync(leadsPath)) {
            leads = JSON.parse(fs.readFileSync(leadsPath, 'utf8'));
        }
        leads.leads.push(result);
        fs.writeFileSync(leadsPath, JSON.stringify(leads, null, 2));
        res.status(200).json({ message: 'Scraping complete', data: result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});