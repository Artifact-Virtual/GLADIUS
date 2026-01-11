import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'timeout',
  description: 'Timeout (mute) a member for a specified duration',
  aliases: ['mute', 'to'],
  permissions: [PermissionFlagsBits.ModerateMembers],
  botPermissions: [PermissionFlagsBits.ModerateMembers],
  cooldown: 3000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('timeout')
    .setDescription('Timeout (mute) a member for a specified duration')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to timeout')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('duration')
        .setDescription('Timeout duration (e.g., 10m, 1h, 1d)')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for timeout')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
  
  async execute(interaction, client) {
    const target = interaction.options.getMember('user');
    const duration = interaction.options.getString('duration');
    const reason = interaction.options.getString('reason') || 'No reason provided';
    
    if (!target) {
      return interaction.reply({ content: '❌ User not found in this server.', ephemeral: true });
    }
    
    if (target.id === interaction.user.id) {
      return interaction.reply({ content: '❌ You cannot timeout yourself!', ephemeral: true });
    }
    
    if (target.id === client.user.id) {
      return interaction.reply({ content: '❌ I cannot timeout myself!', ephemeral: true });
    }
    
    if (target.roles.highest.position >= interaction.member.roles.highest.position) {
      return interaction.reply({ content: '❌ You cannot timeout this user due to role hierarchy.', ephemeral: true });
    }
    
    if (!target.moderatable) {
      return interaction.reply({ content: '❌ I cannot timeout this user.', ephemeral: true });
    }
    
    // Parse duration
    const ms = parseDuration(duration);
    if (!ms || ms < 1000 || ms > 28 * 24 * 60 * 60 * 1000) {
      return interaction.reply({ 
        content: '❌ Invalid duration. Use formats like: 10s, 5m, 1h, 1d (max 28 days)',
        ephemeral: true 
      });
    }
    
    try {
      // Apply timeout
      await target.timeout(ms, reason);
      
      // Log to database
      queries.addModLog(interaction.guild.id, 'TIMEOUT', interaction.user.id, target.id, reason);
      
      const db = (await import('../../utils/database.js')).getDatabase();
      const expiresAt = Math.floor((Date.now() + ms) / 1000);
      db.prepare('INSERT OR REPLACE INTO mutes (user_id, guild_id, moderator_id, reason, expires_at) VALUES (?, ?, ?, ?, ?)')
        .run(target.id, interaction.guild.id, interaction.user.id, reason, expiresAt);
      
      // DM the user
      try {
        await target.send({
          embeds: [{
            color: 0xff9900,
            title: '⏱️ You were timed out',
            description: `You have been timed out in **${interaction.guild.name}**`,
            fields: [
              { name: 'Duration', value: duration },
              { name: 'Reason', value: reason },
              { name: 'Moderator', value: interaction.user.tag },
              { name: 'Expires', value: `<t:${expiresAt}:R>` }
            ],
            timestamp: new Date()
          }]
        });
      } catch (error) {
        // User has DMs disabled
      }
      
      // Send confirmation
      const embed = new EmbedBuilder()
        .setColor('#ff9900')
        .setTitle('⏱️ Member Timed Out')
        .addFields(
          { name: 'User', value: `${target.user.tag} (${target.id})`, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
          { name: 'Duration', value: duration, inline: true },
          { name: 'Expires', value: `<t:${expiresAt}:R>`, inline: true },
          { name: 'Reason', value: reason, inline: false }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
      // Log to mod channel
      const guildData = queries.getGuild(interaction.guild.id);
      if (guildData?.mod_log_channel_id) {
        const logChannel = interaction.guild.channels.cache.get(guildData.mod_log_channel_id);
        if (logChannel) {
          await logChannel.send({ embeds: [embed] });
        }
      }
      
    } catch (error) {
      client.logger.error('Error timing out user:', error);
      return interaction.reply({ content: '❌ Failed to timeout the user.', ephemeral: true });
    }
  }
};

function parseDuration(duration) {
  const regex = /^(\d+)([smhd])$/;
  const match = duration.toLowerCase().match(regex);
  
  if (!match) return null;
  
  const value = parseInt(match[1]);
  const unit = match[2];
  
  const multipliers = {
    's': 1000,
    'm': 60 * 1000,
    'h': 60 * 60 * 1000,
    'd': 24 * 60 * 60 * 1000
  };
  
  return value * multipliers[unit];
}
