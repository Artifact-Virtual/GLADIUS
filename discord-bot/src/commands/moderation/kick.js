import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'kick',
  description: 'Kick a member from the server',
  aliases: [],
  permissions: [PermissionFlagsBits.KickMembers],
  botPermissions: [PermissionFlagsBits.KickMembers],
  cooldown: 3000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('kick')
    .setDescription('Kick a member from the server')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to kick')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for kicking')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.KickMembers),
  
  async execute(interaction, client) {
    const target = interaction.options.getMember('user');
    const reason = interaction.options.getString('reason') || 'No reason provided';
    
    if (!target) {
      return interaction.reply({ content: '❌ User not found in this server.', ephemeral: true });
    }
    
    if (target.id === interaction.user.id) {
      return interaction.reply({ content: '❌ You cannot kick yourself!', ephemeral: true });
    }
    
    if (target.id === client.user.id) {
      return interaction.reply({ content: '❌ I cannot kick myself!', ephemeral: true });
    }
    
    if (target.roles.highest.position >= interaction.member.roles.highest.position) {
      return interaction.reply({ content: '❌ You cannot kick this user due to role hierarchy.', ephemeral: true });
    }
    
    if (!target.kickable) {
      return interaction.reply({ content: '❌ I cannot kick this user.', ephemeral: true });
    }
    
    try {
      // Log to database
      queries.addModLog(interaction.guild.id, 'KICK', interaction.user.id, target.id, reason);
      
      // DM the user
      try {
        await target.send({
          embeds: [{
            color: 0xff9900,
            title: '👢 You were kicked',
            description: `You have been kicked from **${interaction.guild.name}**`,
            fields: [
              { name: 'Reason', value: reason },
              { name: 'Moderator', value: interaction.user.tag }
            ],
            timestamp: new Date()
          }]
        });
      } catch (error) {
        // User has DMs disabled
      }
      
      // Kick the user
      await target.kick(reason);
      
      // Send confirmation
      const embed = new EmbedBuilder()
        .setColor('#00ff00')
        .setTitle('✅ Member Kicked')
        .addFields(
          { name: 'User', value: `${target.user.tag} (${target.id})`, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
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
      client.logger.error('Error kicking user:', error);
      return interaction.reply({ content: '❌ Failed to kick the user.', ephemeral: true });
    }
  }
};
