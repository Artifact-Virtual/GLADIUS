const puppeteer = require('puppeteer');
const logger = require('../utils/logger');
const nlp = require('compromise');

class Scraper {
    constructor() {
        this.browser = null;
    }

    async init() {
        this.browser = await puppeteer.launch({ headless: true });
        logger.info('Browser launched');
    }

    async scrape(url) {
        try {
            const page = await this.browser.newPage();
            await page.goto(url, { waitUntil: 'networkidle2' });
            logger.info(`Navigated to ${url}`);

            // Scrape all visible text
            const pageText = await page.evaluate(() => document.body.innerText);

            // Extract emails and phone numbers
            const emails = pageText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || [];
            const phones = pageText.match(/\+?\d[\d\s().-]{7,}\d/g) || [];

            // Use NLP to extract nouns
            const doc = nlp(pageText);
            const nouns = doc.nouns().out('array');

            // Collect insights (simple keyword-based for now)
            const projectDetails = pageText.match(/project[s]?[:\-\s][^\n]+/gi) || [];

            const data = {
                url,
                emails,
                phones,
                nouns: Array.from(new Set(nouns)),
                projectDetails,
                timestamp: new Date().toISOString()
            };

            logger.info(`Smart scraped data from ${url}`);
            await page.close();
            return data;
        } catch (error) {
            logger.error(`Error scraping ${url}: ${error.message}`);
            throw error;
        }
    }

    async close() {
        await this.browser.close();
        logger.info('Browser closed');
    }
}

module.exports = Scraper;