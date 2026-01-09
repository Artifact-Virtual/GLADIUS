const { Telegraf } = require('telegraf');
require('dotenv').config();
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

if (!process.env.TELEGRAM_BOT_TOKEN) {
    logger.error('TELEGRAM_BOT_TOKEN is missing in .env');
    process.exit(1);
}

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

bot.start((ctx) => ctx.reply('Welcome to Arty Telegram Bot!'));
bot.help((ctx) => ctx.reply('Send me a message!'));
bot.on('text', (ctx) => {
    logger.info(`Received message from ${ctx.from.username}: ${ctx.message.text}`);
    ctx.reply('Message received');
});

bot.launch(() => {
    logger.info('Telegram bot started');
});

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
