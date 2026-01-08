import cron from 'node-cron';
import logger from '../utils/logger.js';
import { getDatabase } from '../utils/database.js';

export async function startCronJobs(client) {
  logger.info('Starting cron jobs...');
  
  // Check reminders every minute
  cron.schedule('* * * * *', async () => {
    await checkReminders(client);
  });
  
  // Check temp bans/mutes every minute
  cron.schedule('* * * * *', async () => {
    await checkTempModeration(client);
  });
  
  // Check giveaways every minute
  cron.schedule('* * * * *', async () => {
    await checkGiveaways(client);
  });
  
  // Check polls every minute
  cron.schedule('* * * * *', async () => {
    await checkPolls(client);
  });
  
  // Update statistics every 5 minutes
  cron.schedule('*/5 * * * *', async () => {
    await updateStatistics(client);
  });
  
  // Backup data (if enabled) - daily at 2 AM
  if (client.config.features.backups?.enabled) {
    cron.schedule('0 2 * * *', async () => {
      await createBackups(client);
    });
  }
  
  logger.info('Cron jobs started');
}

async function checkReminders(client) {
  try {
    const db = getDatabase();
    const now = Math.floor(Date.now() / 1000);
    
    const reminders = db.prepare('SELECT * FROM reminders WHERE remind_at <= ? AND completed = 0').all(now);
    
    for (const reminder of reminders) {
      try {
        const channel = await client.channels.fetch(reminder.channel_id);
        const user = await client.users.fetch(reminder.user_id);
        
        if (channel && user) {
          await channel.send({
            content: `⏰ ${user}, reminder: ${reminder.message}`
          });
          
          // Mark as completed
          db.prepare('UPDATE reminders SET completed = 1 WHERE id = ?').run(reminder.id);
        }
      } catch (error) {
        logger.error(`Failed to send reminder ${reminder.id}:`, error);
      }
    }
  } catch (error) {
    logger.error('Error checking reminders:', error);
  }
}

async function checkTempModeration(client) {
  try {
    const db = getDatabase();
    const now = Math.floor(Date.now() / 1000);
    
    // Check temp mutes
    const expiredMutes = db.prepare('SELECT * FROM mutes WHERE expires_at IS NOT NULL AND expires_at <= ?').all(now);
    
    for (const mute of expiredMutes) {
      try {
        const guild = await client.guilds.fetch(mute.guild_id);
        const member = await guild.members.fetch(mute.user_id);
        
        // Get muted role
        const guildData = db.prepare('SELECT muted_role_id FROM guilds WHERE guild_id = ?').get(guild.id);
        if (guildData?.muted_role_id) {
          const mutedRole = guild.roles.cache.get(guildData.muted_role_id);
          if (mutedRole && member.roles.cache.has(mutedRole.id)) {
            await member.roles.remove(mutedRole);
            logger.info(`Unmuted ${member.user.tag} in ${guild.name} (temp mute expired)`);
          }
        }
        
        // Remove from database
        db.prepare('DELETE FROM mutes WHERE user_id = ? AND guild_id = ?').run(mute.user_id, mute.guild_id);
      } catch (error) {
        logger.error(`Failed to unmute user ${mute.user_id}:`, error);
      }
    }
    
    // Check temp bans
    const expiredBans = db.prepare('SELECT * FROM bans WHERE expires_at IS NOT NULL AND expires_at <= ?').all(now);
    
    for (const ban of expiredBans) {
      try {
        const guild = await client.guilds.fetch(ban.guild_id);
        await guild.members.unban(ban.user_id, 'Temporary ban expired');
        
        logger.info(`Unbanned user ${ban.user_id} in ${guild.name} (temp ban expired)`);
        
        // Remove from database
        db.prepare('DELETE FROM bans WHERE user_id = ? AND guild_id = ?').run(ban.user_id, ban.guild_id);
      } catch (error) {
        logger.error(`Failed to unban user ${ban.user_id}:`, error);
      }
    }
  } catch (error) {
    logger.error('Error checking temp moderation:', error);
  }
}

async function checkGiveaways(client) {
  try {
    const db = getDatabase();
    const now = Math.floor(Date.now() / 1000);
    
    const endedGiveaways = db.prepare('SELECT * FROM giveaways WHERE ends_at <= ? AND ended = 0').all(now);
    
    for (const giveaway of endedGiveaways) {
      try {
        const channel = await client.channels.fetch(giveaway.channel_id);
        const message = await channel.messages.fetch(giveaway.message_id);
        
        // Get reactions
        const reaction = message.reactions.cache.get('🎉');
        if (reaction) {
          const users = await reaction.users.fetch();
          const participants = users.filter(u => !u.bot);
          
          if (participants.size > 0) {
            // Pick winners
            const winners = [];
            const participantsArray = Array.from(participants.values());
            
            for (let i = 0; i < giveaway.winner_count && i < participantsArray.length; i++) {
              const randomIndex = Math.floor(Math.random() * participantsArray.length);
              winners.push(participantsArray.splice(randomIndex, 1)[0]);
            }
            
            // Announce winners
            const winnerMentions = winners.map(w => w.toString()).join(', ');
            await channel.send(`🎉 **Giveaway ended!** Congratulations ${winnerMentions}! You won **${giveaway.prize}**!`);
          } else {
            await channel.send(`🎉 **Giveaway ended!** No valid participants for **${giveaway.prize}**.`);
          }
        }
        
        // Mark as ended
        db.prepare('UPDATE giveaways SET ended = 1 WHERE message_id = ?').run(giveaway.message_id);
      } catch (error) {
        logger.error(`Failed to end giveaway ${giveaway.message_id}:`, error);
      }
    }
  } catch (error) {
    logger.error('Error checking giveaways:', error);
  }
}

async function checkPolls(client) {
  try {
    const db = getDatabase();
    const now = Math.floor(Date.now() / 1000);
    
    const endedPolls = db.prepare('SELECT * FROM polls WHERE ends_at IS NOT NULL AND ends_at <= ? AND ended = 0').all(now);
    
    for (const poll of endedPolls) {
      try {
        const channel = await client.channels.fetch(poll.channel_id);
        const message = await channel.messages.fetch(poll.message_id);
        
        // Calculate results
        const options = JSON.parse(poll.options);
        const results = [];
        
        for (let i = 0; i < options.length; i++) {
          const emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'][i];
          const reaction = message.reactions.cache.get(emoji);
          const count = reaction ? reaction.count - 1 : 0; // Subtract bot's reaction
          results.push({ option: options[i], votes: count });
        }
        
        // Sort by votes
        results.sort((a, b) => b.votes - a.votes);
        
        // Announce results
        const resultsText = results.map((r, i) => `${i + 1}. **${r.option}** - ${r.votes} vote(s)`).join('\n');
        await channel.send(`📊 **Poll ended!**\n\n**${poll.question}**\n\n${resultsText}`);
        
        // Mark as ended
        db.prepare('UPDATE polls SET ended = 1 WHERE message_id = ?').run(poll.message_id);
      } catch (error) {
        logger.error(`Failed to end poll ${poll.message_id}:`, error);
      }
    }
  } catch (error) {
    logger.error('Error checking polls:', error);
  }
}

async function updateStatistics(client) {
  try {
    const config = client.config.features.statistics;
    if (!config?.enabled) return;
    
    for (const guild of client.guilds.cache.values()) {
      try {
        // Update member count
        if (config.channels.totalMembers) {
          const channel = guild.channels.cache.get(config.channels.totalMembers);
          if (channel) {
            await channel.setName(`👥 Members: ${guild.memberCount}`);
          }
        }
        
        // Update online count
        if (config.channels.onlineMembers) {
          const onlineCount = guild.members.cache.filter(m => m.presence?.status !== 'offline').size;
          const channel = guild.channels.cache.get(config.channels.onlineMembers);
          if (channel) {
            await channel.setName(`🟢 Online: ${onlineCount}`);
          }
        }
        
        // Update bot count
        if (config.channels.botCount) {
          const botCount = guild.members.cache.filter(m => m.user.bot).size;
          const channel = guild.channels.cache.get(config.channels.botCount);
          if (channel) {
            await channel.setName(`🤖 Bots: ${botCount}`);
          }
        }
        
        // Update channel count
        if (config.channels.channelCount) {
          const channel = guild.channels.cache.get(config.channels.channelCount);
          if (channel) {
            await channel.setName(`📁 Channels: ${guild.channels.cache.size}`);
          }
        }
        
        // Update role count
        if (config.channels.roleCount) {
          const channel = guild.channels.cache.get(config.channels.roleCount);
          if (channel) {
            await channel.setName(`🎭 Roles: ${guild.roles.cache.size}`);
          }
        }
      } catch (error) {
        logger.error(`Failed to update statistics for ${guild.name}:`, error);
      }
    }
  } catch (error) {
    logger.error('Error updating statistics:', error);
  }
}

async function createBackups(client) {
  try {
    logger.info('Creating server backups...');
    
    const db = getDatabase();
    
    for (const guild of client.guilds.cache.values()) {
      try {
        const backup = {
          name: guild.name,
          icon: guild.iconURL(),
          roles: guild.roles.cache.map(r => ({
            id: r.id,
            name: r.name,
            color: r.color,
            permissions: r.permissions.bitfield,
            position: r.position
          })),
          channels: guild.channels.cache.map(c => ({
            id: c.id,
            name: c.name,
            type: c.type,
            position: c.position,
            parentId: c.parentId
          })),
          timestamp: Date.now()
        };
        
        db.prepare('INSERT INTO backups (guild_id, backup_data, created_by) VALUES (?, ?, ?)')
          .run(guild.id, JSON.stringify(backup), client.user.id);
        
        logger.info(`Created backup for ${guild.name}`);
        
        // Clean old backups
        const maxBackups = client.config.features.backups.maxBackups || 5;
        const oldBackups = db.prepare('SELECT id FROM backups WHERE guild_id = ? ORDER BY created_at DESC LIMIT -1 OFFSET ?')
          .all(guild.id, maxBackups);
        
        for (const old of oldBackups) {
          db.prepare('DELETE FROM backups WHERE id = ?').run(old.id);
        }
      } catch (error) {
        logger.error(`Failed to backup ${guild.name}:`, error);
      }
    }
    
    logger.info('Backup process completed');
  } catch (error) {
    logger.error('Error creating backups:', error);
  }
}
