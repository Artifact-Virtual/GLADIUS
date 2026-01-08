import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export default {
  name: 'serverinfo',
  description: 'Display information about the server',
  aliases: ['si', 'server', 'guildinfo'],
  cooldown: 5000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('serverinfo')
    .setDescription('Display information about the server'),
  
  async execute(interaction, client) {
    const guild = interaction.guild;
    
    // Fetch owner
    const owner = await guild.fetchOwner();
    
    // Count channels by type
    const textChannels = guild.channels.cache.filter(c => c.type === 0).size;
    const voiceChannels = guild.channels.cache.filter(c => c.type === 2).size;
    const categories = guild.channels.cache.filter(c => c.type === 4).size;
    
    // Count members
    const totalMembers = guild.memberCount;
    const bots = guild.members.cache.filter(m => m.user.bot).size;
    const humans = totalMembers - bots;
    
    // Get boost info
    const boostLevel = guild.premiumTier;
    const boostCount = guild.premiumSubscriptionCount || 0;
    
    // Get verification level
    const verificationLevels = {
      0: 'None',
      1: 'Low',
      2: 'Medium',
      3: 'High',
      4: 'Very High'
    };
    
    const embed = new EmbedBuilder()
      .setColor(client.config.bot.embedColor || '#5865F2')
      .setTitle(`📋 ${guild.name} - Server Information`)
      .setThumbnail(guild.iconURL({ dynamic: true, size: 1024 }))
      .addFields(
        { name: '👑 Owner', value: `${owner.user.tag}`, inline: true },
        { name: '🆔 Server ID', value: guild.id, inline: true },
        { name: '📅 Created', value: `<t:${Math.floor(guild.createdTimestamp / 1000)}:R>`, inline: true },
        { name: '👥 Members', value: `Total: ${totalMembers}\nHumans: ${humans}\nBots: ${bots}`, inline: true },
        { name: '📁 Channels', value: `Total: ${guild.channels.cache.size}\nText: ${textChannels}\nVoice: ${voiceChannels}\nCategories: ${categories}`, inline: true },
        { name: '🎭 Roles', value: guild.roles.cache.size.toString(), inline: true },
        { name: '😀 Emojis', value: `${guild.emojis.cache.size} / ${guild.premiumTier === 0 ? '50' : guild.premiumTier === 1 ? '100' : guild.premiumTier === 2 ? '150' : '250'}`, inline: true },
        { name: '💎 Boost Status', value: `Level ${boostLevel}\n${boostCount} boost${boostCount !== 1 ? 's' : ''}`, inline: true },
        { name: '🔒 Verification Level', value: verificationLevels[guild.verificationLevel], inline: true }
      )
      .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
      .setTimestamp();
    
    if (guild.banner) {
      embed.setImage(guild.bannerURL({ size: 1024 }));
    }
    
    if (guild.description) {
      embed.setDescription(guild.description);
    }
    
    await interaction.reply({ embeds: [embed] });
  }
};
