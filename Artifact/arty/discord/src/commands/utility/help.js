import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder } from 'discord.js';

export default {
  name: 'help',
  description: 'Display all commands and bot information',
  aliases: ['commands', 'h'],
  cooldown: 3000,
  data: new SlashCommandBuilder()
    .setName('help')
    .setDescription('Display all commands and bot information')
    .addStringOption(option =>
      option.setName('command')
        .setDescription('Get detailed info about a specific command')
        .setRequired(false)),
  
  async execute(interaction, client) {
    const commandName = interaction.options?.getString('command');
    
    if (commandName) {
      return showCommandHelp(interaction, client, commandName);
    }
    
    const embed = new EmbedBuilder()
      .setColor(client.config.bot.embedColor || '#5865F2')
      .setTitle(`${client.config.bot.name || 'Discord Bot'} - Help`)
      .setDescription(`Comprehensive Discord server management bot with extensive features.\n\nUse the dropdown menu below to explore command categories.`)
      .addFields(
        { name: '📊 Statistics', value: `**Servers:** ${client.guilds.cache.size}\n**Users:** ${client.guilds.cache.reduce((a, g) => a + g.memberCount, 0)}\n**Commands:** ${client.commands.size}`, inline: true },
        { name: '🔗 Links', value: `[Invite Bot](${client.config.bot.inviteUrl || 'N/A'}) • [Support Server](${client.config.bot.supportServerId || 'N/A'})`, inline: true },
        { name: '💡 Prefix', value: `\`${process.env.PREFIX || client.config.bot.prefix || '!'}\` or use slash commands (\`/\`)`, inline: true }
      )
      .setThumbnail(client.user.displayAvatarURL())
      .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
      .setTimestamp();
    
    const categories = {
      moderation: { emoji: '🛡️', name: 'Moderation', description: 'Server moderation commands' },
      admin: { emoji: '⚙️', name: 'Admin', description: 'Server administration commands' },
      utility: { emoji: '🔧', name: 'Utility', description: 'Useful utility commands' },
      fun: { emoji: '🎮', name: 'Fun', description: 'Entertainment commands' },
      economy: { emoji: '💰', name: 'Economy', description: 'Currency and economy commands' },
      music: { emoji: '🎵', name: 'Music', description: 'Music playback commands' }
    };
    
    const selectMenu = new StringSelectMenuBuilder()
      .setCustomId('help_category')
      .setPlaceholder('Select a command category')
      .addOptions(
        Object.entries(categories).map(([key, cat]) => ({
          label: cat.name,
          description: cat.description,
          value: key,
          emoji: cat.emoji
        }))
      );
    
    const row = new ActionRowBuilder().addComponents(selectMenu);
    
    await interaction.reply({ embeds: [embed], components: [row] });
  }
};

async function showCommandHelp(interaction, client, commandName) {
  const command = client.commands.get(commandName) || client.slashCommands.get(commandName);
  
  if (!command) {
    return interaction.reply({ content: `❌ Command \`${commandName}\` not found.`, ephemeral: true });
  }
  
  const embed = new EmbedBuilder()
    .setColor(client.config.bot.embedColor || '#5865F2')
    .setTitle(`📖 Command: ${command.name || command.data.name}`)
    .setDescription(command.description || 'No description available')
    .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
    .setTimestamp();
  
  if (command.aliases && command.aliases.length > 0) {
    embed.addFields({ name: 'Aliases', value: command.aliases.map(a => `\`${a}\``).join(', '), inline: true });
  }
  
  if (command.cooldown) {
    embed.addFields({ name: 'Cooldown', value: `${command.cooldown / 1000}s`, inline: true });
  }
  
  if (command.permissions) {
    embed.addFields({ name: 'Required Permissions', value: command.permissions.map(p => `\`${p}\``).join(', '), inline: false });
  }
  
  await interaction.reply({ embeds: [embed] });
}
