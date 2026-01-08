import { EmbedBuilder } from 'discord.js';
import logger from '../utils/logger.js';
import { queries } from '../utils/database.js';

export default {
  name: 'guildMemberAdd',
  async execute(member, client) {
    try {
      const guildId = member.guild.id;
      const config = client.config.features.welcome;
      
      // Log member join
      logger.info(`${member.user.tag} joined ${member.guild.name}`);
      
      // Get guild data
      const guildData = queries.getGuild(guildId);
      
      // Send welcome message
      if (config?.enabled) {
        const channelId = guildData?.welcome_channel_id || config.channelId;
        const channel = member.guild.channels.cache.get(channelId);
        
        if (channel) {
          const welcomeMessage = (config.message || 'Welcome {user} to {server}!')
            .replace('{user}', member.toString())
            .replace('{server}', member.guild.name)
            .replace('{memberCount}', member.guild.memberCount.toString());
          
          if (config.embedEnabled) {
            const embed = new EmbedBuilder()
              .setColor(client.config.bot.embedColor || '#5865F2')
              .setTitle((config.embedTitle || 'Welcome to {server}!').replace('{server}', member.guild.name))
              .setDescription((config.embedDescription || 'Welcome {user}!')
                .replace('{user}', member.toString())
                .replace('{server}', member.guild.name)
                .replace('{memberCount}', member.guild.memberCount.toString()))
              .setTimestamp();
            
            if (config.embedThumbnail) {
              embed.setThumbnail(member.user.displayAvatarURL({ dynamic: true }));
            }
            
            await channel.send({ embeds: [embed] });
          } else {
            await channel.send(welcomeMessage);
          }
        }
      }
      
      // Assign auto-roles
      if (config?.assignRoles && config.assignRoles.length > 0) {
        for (const roleId of config.assignRoles) {
          const role = member.guild.roles.cache.get(roleId);
          if (role) {
            await member.roles.add(role).catch(error => {
              logger.error(`Failed to assign role ${roleId} to ${member.user.tag}:`, error);
            });
          }
        }
      }
      
      // Assign autorole from database
      if (guildData?.autorole_id) {
        const role = member.guild.roles.cache.get(guildData.autorole_id);
        if (role) {
          await member.roles.add(role).catch(error => {
            logger.error(`Failed to assign autorole to ${member.user.tag}:`, error);
          });
        }
      }
      
      // DM welcome message
      if (config?.dmWelcome) {
        const dmMessage = `Welcome to **${member.guild.name}**! We're glad to have you here.`;
        await member.send(dmMessage).catch(() => {
          logger.debug(`Could not send DM to ${member.user.tag}`);
        });
      }
      
      // Log to logging channel
      const loggingConfig = client.config.features.logging;
      if (loggingConfig?.enabled && loggingConfig.events.memberJoin) {
        const logChannelId = loggingConfig.channels.members || guildData?.log_channel_id;
        const logChannel = member.guild.channels.cache.get(logChannelId);
        
        if (logChannel) {
          const embed = new EmbedBuilder()
            .setColor('#00ff00')
            .setTitle('📥 Member Joined')
            .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
            .addFields(
              { name: 'User', value: `${member.user.tag} (${member.user.id})`, inline: true },
              { name: 'Account Created', value: `<t:${Math.floor(member.user.createdTimestamp / 1000)}:R>`, inline: true },
              { name: 'Member Count', value: member.guild.memberCount.toString(), inline: true }
            )
            .setTimestamp();
          
          await logChannel.send({ embeds: [embed] });
        }
      }
      
    } catch (error) {
      logger.error('Error in guildMemberAdd event:', error);
    }
  }
};
