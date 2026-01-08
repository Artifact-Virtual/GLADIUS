import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'ban',
  description: 'Ban a member from the server',
  aliases: [],
  permissions: [PermissionFlagsBits.BanMembers],
  botPermissions: [PermissionFlagsBits.BanMembers],
  cooldown: 3000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('ban')
    .setDescription('Ban a member from the server')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to ban')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for banning')
        .setRequired(false))
    .addIntegerOption(option =>
      option.setName('delete_days')
        .setDescription('Days of messages to delete (0-7)')
        .setMinValue(0)
        .setMaxValue(7)
        .setRequired(false))
    .addStringOption(option =>
      option.setName('duration')
        .setDescription('Temporary ban duration (e.g., 1d, 2h, 30m)')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
  
  async execute(interaction, client) {
    const targetUser = interaction.options.getUser('user');
    const reason = interaction.options.getString('reason') || 'No reason provided';
    const deleteDays = interaction.options.getInteger('delete_days') || 0;
    const duration = interaction.options.getString('duration');
    
    if (targetUser.id === interaction.user.id) {
      return interaction.reply({ content: '❌ You cannot ban yourself!', ephemeral: true });
    }
    
    if (targetUser.id === client.user.id) {
      return interaction.reply({ content: '❌ I cannot ban myself!', ephemeral: true });
    }
    
    // Check if user is in guild
    let target;
    try {
      target = await interaction.guild.members.fetch(targetUser.id);
    } catch (error) {
      // User not in guild, can still ban by ID
      target = null;
    }
    
    if (target) {
      if (target.roles.highest.position >= interaction.member.roles.highest.position) {
        return interaction.reply({ content: '❌ You cannot ban this user due to role hierarchy.', ephemeral: true });
      }
      
      if (!target.bannable) {
        return interaction.reply({ content: '❌ I cannot ban this user.', ephemeral: true });
      }
    }
    
    try {
      // Calculate expiration if duration provided
      let expiresAt = null;
      if (duration) {
        const ms = parseDuration(duration);
        if (!ms) {
          return interaction.reply({ content: '❌ Invalid duration format. Use formats like: 1d, 2h, 30m', ephemeral: true });
        }
        expiresAt = Math.floor((Date.now() + ms) / 1000);
      }
      
      // Log to database
      queries.addModLog(interaction.guild.id, 'BAN', interaction.user.id, targetUser.id, reason);
      
      if (expiresAt) {
        const db = client.db || (await import('../../utils/database.js')).getDatabase();
        db.prepare('INSERT INTO bans (user_id, guild_id, moderator_id, reason, expires_at) VALUES (?, ?, ?, ?, ?)')
          .run(targetUser.id, interaction.guild.id, interaction.user.id, reason, expiresAt);
      }
      
      // DM the user if in guild
      if (target) {
        try {
          await targetUser.send({
            embeds: [{
              color: 0xff0000,
              title: '🔨 You were banned',
              description: `You have been banned from **${interaction.guild.name}**`,
              fields: [
                { name: 'Reason', value: reason },
                { name: 'Moderator', value: interaction.user.tag },
                ...(duration ? [{ name: 'Duration', value: duration }] : [])
              ],
              timestamp: new Date()
            }]
          });
        } catch (error) {
          // User has DMs disabled
        }
      }
      
      // Ban the user
      await interaction.guild.members.ban(targetUser.id, { 
        reason,
        deleteMessageSeconds: deleteDays * 24 * 60 * 60
      });
      
      // Send confirmation
      const embed = new EmbedBuilder()
        .setColor('#ff0000')
        .setTitle('🔨 Member Banned')
        .addFields(
          { name: 'User', value: `${targetUser.tag} (${targetUser.id})`, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
          { name: 'Reason', value: reason, inline: false }
        )
        .setTimestamp();
      
      if (duration) {
        embed.addFields({ name: 'Duration', value: duration, inline: true });
      }
      
      if (deleteDays > 0) {
        embed.addFields({ name: 'Messages Deleted', value: `Last ${deleteDays} day(s)`, inline: true });
      }
      
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
      client.logger.error('Error banning user:', error);
      return interaction.reply({ content: '❌ Failed to ban the user.', ephemeral: true });
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
