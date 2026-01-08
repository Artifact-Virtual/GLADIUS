import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export default {
  name: 'avatar',
  description: 'Display a user\'s avatar',
  aliases: ['av', 'pfp', 'icon'],
  cooldown: 3000,
  data: new SlashCommandBuilder()
    .setName('avatar')
    .setDescription('Display a user\'s avatar')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user whose avatar to display')
        .setRequired(false)),
  
  async execute(interaction, client) {
    const target = interaction.options?.getUser('user') || interaction.user;
    
    // Get member to get server avatar if available
    let member = null;
    if (interaction.guild) {
      member = await interaction.guild.members.fetch(target.id).catch(() => null);
    }
    
    const embed = new EmbedBuilder()
      .setColor(client.config.bot.embedColor || '#5865F2')
      .setTitle(`${target.username}'s Avatar`)
      .setDescription(`[PNG](${target.displayAvatarURL({ extension: 'png', size: 4096 })}) | [JPG](${target.displayAvatarURL({ extension: 'jpg', size: 4096 })}) | [WEBP](${target.displayAvatarURL({ extension: 'webp', size: 4096 })})`)
      .setImage(target.displayAvatarURL({ dynamic: true, size: 4096 }))
      .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
      .setTimestamp();
    
    // Add server avatar if different from user avatar
    if (member && member.avatar) {
      const serverAvatar = member.displayAvatarURL({ dynamic: true, size: 4096 });
      embed.addFields({
        name: '🖼️ Server Avatar',
        value: `[PNG](${member.displayAvatarURL({ extension: 'png', size: 4096 })}) | [JPG](${member.displayAvatarURL({ extension: 'jpg', size: 4096 })}) | [WEBP](${member.displayAvatarURL({ extension: 'webp', size: 4096 })})`,
        inline: false
      });
      embed.setThumbnail(serverAvatar);
    }
    
    await interaction.reply({ embeds: [embed] });
  }
};
