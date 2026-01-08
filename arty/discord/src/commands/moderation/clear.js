import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';

export default {
  name: 'clear',
  description: 'Clear messages from a channel',
  aliases: ['purge', 'delete', 'clean'],
  permissions: [PermissionFlagsBits.ManageMessages],
  botPermissions: [PermissionFlagsBits.ManageMessages],
  cooldown: 5000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('clear')
    .setDescription('Clear messages from a channel')
    .addIntegerOption(option =>
      option.setName('amount')
        .setDescription('Number of messages to delete (1-100)')
        .setMinValue(1)
        .setMaxValue(100)
        .setRequired(true))
    .addUserOption(option =>
      option.setName('user')
        .setDescription('Only delete messages from this user')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages),
  
  async execute(interaction, client) {
    const amount = interaction.options.getInteger('amount');
    const targetUser = interaction.options.getUser('user');
    
    await interaction.deferReply({ ephemeral: true });
    
    try {
      // Fetch messages
      let messages = await interaction.channel.messages.fetch({ limit: Math.min(amount, 100) });
      
      // Filter by user if specified
      if (targetUser) {
        messages = messages.filter(msg => msg.author.id === targetUser.id);
      }
      
      // Filter out messages older than 14 days (Discord API limitation)
      const twoWeeks = 14 * 24 * 60 * 60 * 1000;
      messages = messages.filter(msg => Date.now() - msg.createdTimestamp < twoWeeks);
      
      if (messages.size === 0) {
        return interaction.editReply({ 
          content: '❌ No messages found to delete (messages must be less than 14 days old).',
          ephemeral: true 
        });
      }
      
      // Bulk delete messages
      const deleted = await interaction.channel.bulkDelete(messages, true);
      
      // Send confirmation
      const embed = new EmbedBuilder()
        .setColor('#00ff00')
        .setTitle('🧹 Messages Cleared')
        .setDescription(`Successfully deleted **${deleted.size}** message${deleted.size !== 1 ? 's' : ''}${targetUser ? ` from ${targetUser.tag}` : ''}.`)
        .addFields(
          { name: 'Channel', value: interaction.channel.toString(), inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true }
        )
        .setTimestamp();
      
      await interaction.editReply({ embeds: [embed], ephemeral: true });
      
      // Log to database
      const { queries } = await import('../../utils/database.js');
      queries.addModLog(
        interaction.guild.id,
        'CLEAR',
        interaction.user.id,
        targetUser?.id || 'all',
        `Deleted ${deleted.size} messages in ${interaction.channel.name}`
      );
      
      // Log to mod channel
      const guildData = queries.getGuild(interaction.guild.id);
      if (guildData?.mod_log_channel_id) {
        const logChannel = interaction.guild.channels.cache.get(guildData.mod_log_channel_id);
        if (logChannel && logChannel.id !== interaction.channel.id) {
          const logEmbed = new EmbedBuilder()
            .setColor('#ff9900')
            .setTitle('🧹 Messages Cleared')
            .addFields(
              { name: 'Channel', value: interaction.channel.toString(), inline: true },
              { name: 'Moderator', value: interaction.user.tag, inline: true },
              { name: 'Amount', value: deleted.size.toString(), inline: true }
            )
            .setTimestamp();
          
          if (targetUser) {
            logEmbed.addFields({ name: 'User Filter', value: targetUser.tag, inline: true });
          }
          
          await logChannel.send({ embeds: [logEmbed] });
        }
      }
      
      // Auto-delete confirmation after 5 seconds
      setTimeout(async () => {
        try {
          await interaction.deleteReply();
        } catch (error) {
          // Reply may already be deleted
        }
      }, 5000);
      
    } catch (error) {
      client.logger.error('Error clearing messages:', error);
      
      if (error.code === 50034) {
        return interaction.editReply({ 
          content: '❌ Cannot delete messages older than 14 days.',
          ephemeral: true 
        });
      }
      
      return interaction.editReply({ 
        content: '❌ Failed to clear messages.',
        ephemeral: true 
      });
    }
  }
};
