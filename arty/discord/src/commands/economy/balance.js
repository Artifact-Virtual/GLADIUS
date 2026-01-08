import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'balance',
  description: 'Check your or another user\'s balance',
  aliases: ['bal', 'money', 'coins'],
  cooldown: 3000,
  data: new SlashCommandBuilder()
    .setName('balance')
    .setDescription('Check your or another user\'s balance')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to check')
        .setRequired(false)),
  
  async execute(interaction, client) {
    if (!client.config.features.economy?.enabled) {
      return interaction.reply({ content: '❌ Economy system is disabled.', ephemeral: true });
    }
    
    const target = interaction.options?.getUser('user') || interaction.user;
    const userId = target.id;
    const guildId = interaction.guild.id;
    
    // Get economy data
    let economyData = queries.getEconomy(userId, guildId);
    
    if (!economyData) {
      // Initialize economy data
      queries.upsertEconomy(userId, guildId, {
        balance: 0,
        bank: 0,
        last_daily: 0,
        last_work: 0,
        inventory: '[]'
      });
      economyData = queries.getEconomy(userId, guildId);
    }
    
    const currencyName = client.config.features.economy.currency?.name || 'coins';
    const currencySymbol = client.config.features.economy.currency?.symbol || '🪙';
    
    const embed = new EmbedBuilder()
      .setColor(client.config.bot.embedColor || '#5865F2')
      .setTitle(`${currencySymbol} ${target.username}'s Balance`)
      .setThumbnail(target.displayAvatarURL({ dynamic: true }))
      .addFields(
        { name: 'Wallet', value: `${currencySymbol} ${economyData.balance.toLocaleString()} ${currencyName}`, inline: true },
        { name: 'Bank', value: `${currencySymbol} ${economyData.bank.toLocaleString()} ${currencyName}`, inline: true },
        { name: 'Total', value: `${currencySymbol} ${(economyData.balance + economyData.bank).toLocaleString()} ${currencyName}`, inline: true }
      )
      .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
      .setTimestamp();
    
    await interaction.reply({ embeds: [embed] });
  }
};
