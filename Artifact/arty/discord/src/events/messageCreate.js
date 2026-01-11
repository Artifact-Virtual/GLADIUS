import { PermissionFlagsBits } from 'discord.js';
import logger from '../utils/logger.js';
import { queries } from '../utils/database.js';

export default {
  name: 'messageCreate',
  async execute(message, client) {
    // Ignore bot messages
    if (message.author.bot) return;
    
    // Ignore DMs (unless you want to handle them)
    if (!message.guild) return;
    
    // Handle leveling system
    if (client.config.features.leveling?.enabled) {
      await handleLeveling(message, client);
    }
    
    // Handle auto-moderation
    if (client.config.features.automod?.enabled) {
      const shouldDelete = await handleAutoMod(message, client);
      if (shouldDelete) return;
    }
    
    // Get guild prefix
    const guildData = queries.getGuild(message.guild.id);
    const prefix = guildData?.prefix || process.env.PREFIX || client.config.bot.prefix || '!';
    
    // Check if message starts with prefix
    if (!message.content.startsWith(prefix)) return;
    
    // Parse command and arguments
    const args = message.content.slice(prefix.length).trim().split(/ +/);
    const commandName = args.shift().toLowerCase();
    
    // Get command
    const command = client.commands.get(commandName);
    if (!command) return;
    
    try {
      // Check if command requires guild only
      if (command.guildOnly && !message.guild) {
        return message.reply('❌ This command can only be used in a server.');
      }
      
      // Check permissions
      if (command.permissions) {
        if (!message.member.permissions.has(command.permissions)) {
          return message.reply('❌ You do not have permission to use this command.');
        }
      }
      
      // Check bot permissions
      if (command.botPermissions) {
        if (!message.guild.members.me.permissions.has(command.botPermissions)) {
          return message.reply('❌ I do not have the required permissions to execute this command.');
        }
      }
      
      // Check cooldown
      if (command.cooldown) {
        const cooldownKey = `${message.author.id}-${command.name}`;
        const cooldowns = client.cooldowns;
        
        if (cooldowns.has(cooldownKey)) {
          const expirationTime = cooldowns.get(cooldownKey);
          const timeLeft = (expirationTime - Date.now()) / 1000;
          
          if (timeLeft > 0) {
            return message.reply(`⏰ Please wait ${timeLeft.toFixed(1)} seconds before using this command again.`);
          }
        }
        
        cooldowns.set(cooldownKey, Date.now() + command.cooldown);
        setTimeout(() => cooldowns.delete(cooldownKey), command.cooldown);
      }
      
      // Execute command
      await command.execute(message, args, client);
      
      // Log command usage
      logger.command(message.author, message.guild, commandName, args);
      
    } catch (error) {
      logger.error(`Error executing command ${commandName}:`, error);
      message.reply('❌ An error occurred while executing this command.');
    }
  }
};

async function handleLeveling(message, client) {
  try {
    const userId = message.author.id;
    const guildId = message.guild.id;
    
    // Get user level data
    let levelData = queries.getLevel(userId, guildId);
    
    // Check cooldown
    const now = Date.now();
    const cooldown = client.config.features.leveling.cooldown || 60000;
    
    if (levelData && now - levelData.last_xp_time < cooldown) {
      return;
    }
    
    // Generate random XP
    const xpMin = client.config.features.leveling.xpPerMessage?.min || 15;
    const xpMax = client.config.features.leveling.xpPerMessage?.max || 25;
    const xpGained = Math.floor(Math.random() * (xpMax - xpMin + 1)) + xpMin;
    
    // Calculate new XP and level
    const currentXP = (levelData?.xp || 0) + xpGained;
    const currentLevel = levelData?.level || 0;
    const requiredXP = calculateRequiredXP(currentLevel);
    
    let newLevel = currentLevel;
    let remainingXP = currentXP;
    
    // Check if leveled up
    if (currentXP >= requiredXP) {
      newLevel = currentLevel + 1;
      remainingXP = currentXP - requiredXP;
      
      // Send level up message
      if (client.config.features.leveling.sendLevelUpMessage) {
        const levelUpMsg = client.config.features.leveling.levelUpMessage
          .replace('{user}', message.author.toString())
          .replace('{level}', newLevel);
        
        message.channel.send(levelUpMsg).catch(() => {});
      }
      
      // Check for level rewards
      const rewards = client.config.features.leveling.rewards || [];
      const reward = rewards.find(r => r.level === newLevel);
      
      if (reward && reward.roleId) {
        const role = message.guild.roles.cache.get(reward.roleId);
        if (role) {
          message.member.roles.add(role).catch(() => {});
        }
      }
    }
    
    // Update database
    queries.upsertLevel(userId, guildId, {
      xp: remainingXP,
      level: newLevel,
      last_xp_time: now,
      messages: (levelData?.messages || 0) + 1
    });
    
  } catch (error) {
    logger.error('Error in leveling system:', error);
  }
}

function calculateRequiredXP(level) {
  // XP formula: 5 * (level ^ 2) + 50 * level + 100
  return 5 * Math.pow(level, 2) + 50 * level + 100;
}

async function handleAutoMod(message, client) {
  try {
    const config = client.config.features.automod;
    const content = message.content;
    let shouldDelete = false;
    let reason = '';
    
    // Check for spam (excessive mentions)
    const mentions = message.mentions.users.size + message.mentions.roles.size;
    if (mentions > config.maxMentions) {
      shouldDelete = true;
      reason = `Too many mentions (${mentions}/${config.maxMentions})`;
    }
    
    // Check for excessive emoji
    const emojiCount = (content.match(/<a?:\w+:\d+>/g) || []).length;
    if (emojiCount > config.maxEmoji) {
      shouldDelete = true;
      reason = `Too many emojis (${emojiCount}/${config.maxEmoji})`;
    }
    
    // Check for excessive lines
    const lines = content.split('\n').length;
    if (lines > config.maxLines) {
      shouldDelete = true;
      reason = `Too many lines (${lines}/${config.maxLines})`;
    }
    
    // Check for bad words
    if (config.badWords && config.badWords.length > 0) {
      const lowerContent = content.toLowerCase();
      const foundBadWord = config.badWords.some(word => lowerContent.includes(word.toLowerCase()));
      if (foundBadWord) {
        shouldDelete = true;
        reason = 'Inappropriate language';
      }
    }
    
    // Check for links (if not whitelisted)
    const linkRegex = /(https?:\/\/[^\s]+)/g;
    const links = content.match(linkRegex);
    if (links && links.length > 0) {
      const whitelist = config.linkWhitelist || [];
      const hasUnauthorizedLink = links.some(link => {
        return !whitelist.some(allowed => link.includes(allowed));
      });
      
      if (hasUnauthorizedLink && whitelist.length > 0) {
        shouldDelete = true;
        reason = 'Unauthorized link';
      }
    }
    
    // Take action if needed
    if (shouldDelete && config.actions.delete) {
      await message.delete().catch(() => {});
      
      // Warn user
      if (config.actions.warn) {
        message.channel.send(`⚠️ ${message.author}, your message was deleted: ${reason}`)
          .then(msg => setTimeout(() => msg.delete().catch(() => {}), 5000))
          .catch(() => {});
      }
      
      // Log to moderation channel
      const guildData = queries.getGuild(message.guild.id);
      if (guildData?.mod_log_channel_id) {
        const logChannel = message.guild.channels.cache.get(guildData.mod_log_channel_id);
        if (logChannel) {
          logChannel.send({
            embeds: [{
              color: 0xff9900,
              title: '🛡️ Auto-Moderation',
              fields: [
                { name: 'User', value: message.author.tag, inline: true },
                { name: 'Channel', value: message.channel.toString(), inline: true },
                { name: 'Reason', value: reason, inline: false },
                { name: 'Message', value: content.substring(0, 1000), inline: false }
              ],
              timestamp: new Date()
            }]
          }).catch(() => {});
        }
      }
      
      logger.info(`Auto-mod deleted message from ${message.author.tag}: ${reason}`);
      return true;
    }
    
    return false;
  } catch (error) {
    logger.error('Error in auto-moderation:', error);
    return false;
  }
}
