const { Client } = require('@notionhq/client');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });
const winston = require('winston');

const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' }),
    ],
});

if (!process.env.NOTION_API_KEY) {
    logger.error('NOTION_API_KEY is missing in .env');
    process.exit(1);
}

const notion = new Client({ auth: process.env.NOTION_API_KEY });

async function main() {
    try {
        logger.info('Arty Notion Client Initialized');

        // Example: List users
        const listUsersResponse = await notion.users.list({});
        logger.info(`Found ${listUsersResponse.results.length} users`);

        // Add more logic here

    } catch (error) {
        logger.error(error);
    }
}

main();
