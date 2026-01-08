import { EmbedBuilder } from 'discord.js';
import logger from '../utils/logger.js';
import { queries } from '../utils/database.js';

export default {
  name: 'guildMemberRemove',
  async execute(member, client) {
    try {
      const guildId = member.guild.id;
      const config = client.config.features.goodbye;
      
      // Log member leave
      logger.info(`${member.user.tag} left ${member.guild.name}`);
      
      // Get guild data
      const guildData = queries.getGuild(guildId);
      
      // Send goodbye message
      if (config?.enabled) {
        const channelId = guildData?.goodbye_channel_id || config.channelId;
        const channel = member.guild.channels.cache.get(channelId);
        
        if (channel) {
          const goodbyeMessage = (config.message || 'Goodbye {user}!')
            .replace('{user}', member.user.tag)
            .replace('{server}', member.guild.name)
            .replace('{memberCount}', member.guild.memberCount.toString());
          
          if (config.embedEnabled) {
            const embed = new EmbedBuilder()
              .setColor('#ff0000')
              .setDescription(goodbyeMessage)
              .setTimestamp();
            
            await channel.send({ embeds: [embed] });
          } else {
            await channel.send(goodbyeMessage);
          }
        }
      }
      
      // Log to logging channel
      const loggingConfig = client.config.features.logging;
      if (loggingConfig?.enabled && loggingConfig.events.memberLeave) {
        const logChannelId = loggingConfig.channels.members || guildData?.log_channel_id;
        const logChannel = member.guild.channels.cache.get(logChannelId);
        
        if (logChannel) {
          const embed = new EmbedBuilder()
            .setColor('#ff0000')
            .setTitle('📤 Member Left')
            .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
            .addFields(
              { name: 'User', value: `${member.user.tag} (${member.user.id})`, inline: true },
              { name: 'Joined', value: member.joinedAt ? `<t:${Math.floor(member.joinedTimestamp / 1000)}:R>` : 'Unknown', inline: true },
              { name: 'Member Count', value: member.guild.memberCount.toString(), inline: true }
            )
            .setTimestamp();
          
          await logChannel.send({ embeds: [embed] });
        }
      }
      
    } catch (error) {
      logger.error('Error in guildMemberRemove event:', error);
    }
  }
};
