import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'warn',
  description: 'Warn a member',
  aliases: ['warning'],
  permissions: [PermissionFlagsBits.ModerateMembers],
  botPermissions: [],
  cooldown: 3000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('warn')
    .setDescription('Warn a member')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to warn')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for warning')
        .setRequired(true))
    .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
  
  async execute(interaction, client) {
    const target = interaction.options.getMember('user');
    const reason = interaction.options.getString('reason');
    
    if (!target) {
      return interaction.reply({ content: '❌ User not found in this server.', ephemeral: true });
    }
    
    if (target.id === interaction.user.id) {
      return interaction.reply({ content: '❌ You cannot warn yourself!', ephemeral: true });
    }
    
    if (target.id === client.user.id) {
      return interaction.reply({ content: '❌ You cannot warn me!', ephemeral: true });
    }
    
    if (target.roles.highest.position >= interaction.member.roles.highest.position) {
      return interaction.reply({ content: '❌ You cannot warn this user due to role hierarchy.', ephemeral: true });
    }
    
    try {
      // Add warning to database
      queries.addWarning(target.id, interaction.guild.id, interaction.user.id, reason);
      
      // Get all warnings for this user
      const warnings = queries.getWarnings(target.id, interaction.guild.id);
      const warnCount = warnings.length;
      
      // DM the user
      try {
        await target.send({
          embeds: [{
            color: 0xff9900,
            title: '⚠️ You received a warning',
            description: `You have been warned in **${interaction.guild.name}**`,
            fields: [
              { name: 'Reason', value: reason },
              { name: 'Moderator', value: interaction.user.tag },
              { name: 'Total Warnings', value: warnCount.toString() }
            ],
            timestamp: new Date()
          }]
        });
      } catch (error) {
        // User has DMs disabled
      }
      
      // Check for automatic actions based on warning thresholds
      const kickThreshold = parseInt(process.env.WARN_THRESHOLD_KICK) || 3;
      const banThreshold = parseInt(process.env.WARN_THRESHOLD_BAN) || 5;
      
      let autoAction = '';
      
      if (warnCount >= banThreshold && interaction.guild.members.me.permissions.has(PermissionFlagsBits.BanMembers)) {
        await target.ban({ reason: `Exceeded warning threshold (${warnCount} warnings)` });
        autoAction = `\n\n⚠️ User has been **banned** automatically (${warnCount}/${banThreshold} warnings)`;
      } else if (warnCount >= kickThreshold && interaction.guild.members.me.permissions.has(PermissionFlagsBits.KickMembers)) {
        await target.kick(`Exceeded warning threshold (${warnCount} warnings)`);
        autoAction = `\n\n⚠️ User has been **kicked** automatically (${warnCount}/${kickThreshold} warnings)`;
      }
      
      // Send confirmation
      const embed = new EmbedBuilder()
        .setColor('#ff9900')
        .setTitle('⚠️ Warning Issued')
        .setDescription(`${target.toString()} has been warned.${autoAction}`)
        .addFields(
          { name: 'User', value: `${target.user.tag} (${target.id})`, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
          { name: 'Total Warnings', value: warnCount.toString(), inline: true },
          { name: 'Reason', value: reason, inline: false }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
      // Log to database
      queries.addModLog(interaction.guild.id, 'WARN', interaction.user.id, target.id, reason);
      
      // Log to mod channel
      const guildData = queries.getGuild(interaction.guild.id);
      if (guildData?.mod_log_channel_id) {
        const logChannel = interaction.guild.channels.cache.get(guildData.mod_log_channel_id);
        if (logChannel) {
          await logChannel.send({ embeds: [embed] });
        }
      }
      
    } catch (error) {
      client.logger.error('Error warning user:', error);
      return interaction.reply({ content: '❌ Failed to warn the user.', ephemeral: true });
    }
  }
};
