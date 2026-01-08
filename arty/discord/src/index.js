import { Client, GatewayIntentBits, Collection, Partials, ActivityType } from 'discord.js';
import { config } from 'dotenv';
import { readFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './utils/logger.js';
import { loadCommands } from './handlers/commandHandler.js';
import { loadEvents } from './handlers/eventHandler.js';
import { initializeDatabase } from './utils/database.js';
import { startCronJobs } from './services/cronService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
config();

// Load configuration
let botConfig;
try {
  const configPath = path.join(path.dirname(__dirname), 'config.json');
  botConfig = JSON.parse(readFileSync(configPath, 'utf-8'));
} catch (error) {
  const examplePath = path.join(path.dirname(__dirname), 'config.example.json');
  botConfig = JSON.parse(readFileSync(examplePath, 'utf-8'));
  logger.warn('config.json not found, using config.example.json. Please create config.json from config.example.json');
}

// Create Discord client with all necessary intents
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildModeration,
    GatewayIntentBits.GuildEmojisAndStickers,
    GatewayIntentBits.GuildIntegrations,
    GatewayIntentBits.GuildWebhooks,
    GatewayIntentBits.GuildInvites,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildPresences,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.GuildMessageTyping,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.DirectMessageReactions,
    GatewayIntentBits.DirectMessageTyping,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildScheduledEvents,
    GatewayIntentBits.AutoModerationConfiguration,
    GatewayIntentBits.AutoModerationExecution,
  ],
  partials: [
    Partials.Message,
    Partials.Channel,
    Partials.Reaction,
    Partials.User,
    Partials.GuildMember,
    Partials.ThreadMember,
    Partials.GuildScheduledEvent,
  ],
  allowedMentions: {
    parse: ['users', 'roles'],
    repliedUser: true
  }
});

// Initialize collections
client.commands = new Collection();
client.slashCommands = new Collection();
client.cooldowns = new Collection();
client.config = botConfig;
client.logger = logger;

// Music queue system
client.queues = new Collection();
client.voiceStates = new Collection();

// Economy and leveling data cache
client.economy = new Collection();
client.levels = new Collection();

// Moderation tracking
client.warnings = new Collection();
client.tempBans = new Collection();
client.tempMutes = new Collection();

// Rate limiting
client.rateLimits = new Collection();

// Tickets
client.tickets = new Collection();

// Giveaways
client.giveaways = new Collection();

// Polls
client.polls = new Collection();

// Reminders
client.reminders = new Collection();

// Initialize bot
async function initializeBot() {
  try {
    // Initialize database
    logger.info('Initializing database...');
    await initializeDatabase();
    
    // Load commands
    logger.info('Loading commands...');
    await loadCommands(client);
    
    // Load events
    logger.info('Loading events...');
    await loadEvents(client);
    
    // Start cron jobs
    logger.info('Starting cron jobs...');
    await startCronJobs(client);
    
    // Login to Discord
    logger.info('Logging in to Discord...');
    await client.login(process.env.DISCORD_TOKEN);
    
  } catch (error) {
    logger.error('Failed to initialize bot:', error);
    process.exit(1);
  }
}

// Handle process events
process.on('unhandledRejection', (error) => {
  logger.error('Unhandled promise rejection:', error);
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception:', error);
  process.exit(1);
});

process.on('SIGINT', async () => {
  logger.info('Received SIGINT, shutting down gracefully...');
  await client.destroy();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Received SIGTERM, shutting down gracefully...');
  await client.destroy();
  process.exit(0);
});

// Start the bot
initializeBot();

export default client;
