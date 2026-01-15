const Queue = require('bull');
const logger = require('../utils/logger');
const fs = require('fs');
const path = require('path');
const Scraper = require('./scraper');

class Scheduler {
    constructor() {
        this.queue = new Queue('scrapingQueue');
        this.queue.on('completed', (job, result) => {
            logger.info(`Job completed: ${job.id}`);
        });
        this.queue.on('failed', (job, err) => {
            logger.error(`Job failed: ${job.id} with error: ${err.message}`);
        });
        // Start processing jobs
        this.processJobs(this.handleJob.bind(this));
    }

    async handleJob(data) {
        const scraper = new Scraper();
        await scraper.init();
        const result = await scraper.scrape(data.url);
        await scraper.close();
        // Save result to leads.json
        const leadsPath = path.join(__dirname, '../data/leads.json');
        let leads = { leads: [] };
        if (fs.existsSync(leadsPath)) {
            leads = JSON.parse(fs.readFileSync(leadsPath, 'utf8'));
        }
        leads.leads.push(result);
        fs.writeFileSync(leadsPath, JSON.stringify(leads, null, 2));
    }

    addJob(data) {
        this.queue.add(data);
        logger.info(`Job added: ${data}`);
    }

    processJobs(processFunction) {
        this.queue.process(async (job) => {
            try {
                await processFunction(job.data);
                logger.info(`Processed job: ${job.id}`);
            } catch (error) {
                logger.error(`Error processing job: ${job.id} - ${error.message}`);
                throw error;
            }
        });
    }

    retryJob(jobId) {
        this.queue.getJob(jobId).then(job => {
            if (job) {
                job.retry();
                logger.info(`Retrying job: ${jobId}`);
            } else {
                logger.warn(`Job not found: ${jobId}`);
            }
        });
    }
}

let lastStatus = 'idle';

async function startScraping() {
    lastStatus = 'running';
    // Load the target from config
    const configPath = path.join(__dirname, '../config/profiles.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const target = config.searchTargets[0].url;
    module.exports.addJob({ url: target });
    // Simulate async scraping process
    await new Promise(resolve => setTimeout(resolve, 2000));
    lastStatus = 'completed';
}

function getStatus() {
    return lastStatus;
}

module.exports = new Scheduler();
module.exports.startScraping = startScraping;
module.exports.getStatus = getStatus;