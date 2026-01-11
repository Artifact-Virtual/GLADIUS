import { ActivityType } from 'discord.js';
import logger from '../utils/logger.js';

export default {
  name: 'ready',
  once: true,
  async execute(client) {
    logger.info(`Bot is ready! Logged in as ${client.user.tag}`);
    logger.info(`Connected to ${client.guilds.cache.size} guilds`);
    logger.info(`Serving ${client.guilds.cache.reduce((a, g) => a + g.memberCount, 0)} users`);
    
    // Set bot status
    updateStatus(client);
    
    // Rotate status if enabled
    if (client.config.status?.enabled && client.config.status?.rotationInterval) {
      setInterval(() => updateStatus(client), client.config.status.rotationInterval);
    }
    
    logger.info('Bot initialization complete!');
  }
};

function updateStatus(client) {
  const config = client.config.status;
  
  if (!config?.enabled || !config.activities || config.activities.length === 0) {
    return;
  }
  
  // Get random activity or cycle through them
  const activities = config.activities;
  const activity = activities[Math.floor(Math.random() * activities.length)];
  
  // Replace placeholders
  const text = activity
    .replace('{memberCount}', client.guilds.cache.reduce((a, g) => a + g.memberCount, 0))
    .replace('{guildCount}', client.guilds.cache.size)
    .replace('{userCount}', client.users.cache.size);
  
  // Get activity type
  let type = ActivityType.Playing;
  switch (config.type?.toUpperCase()) {
    case 'PLAYING':
      type = ActivityType.Playing;
      break;
    case 'WATCHING':
      type = ActivityType.Watching;
      break;
    case 'LISTENING':
      type = ActivityType.Listening;
      break;
    case 'STREAMING':
      type = ActivityType.Streaming;
      break;
    case 'COMPETING':
      type = ActivityType.Competing;
      break;
  }
  
  client.user.setPresence({
    activities: [{ name: text, type }],
    status: 'online'
  });
}
