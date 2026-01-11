import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'daily',
  description: 'Claim your daily reward',
  aliases: [],
  cooldown: 3000,
  data: new SlashCommandBuilder()
    .setName('daily')
    .setDescription('Claim your daily reward'),
  
  async execute(interaction, client) {
    if (!client.config.features.economy?.enabled) {
      return interaction.reply({ content: '❌ Economy system is disabled.', ephemeral: true });
    }
    
    const userId = interaction.user.id;
    const guildId = interaction.guild.id;
    const now = Math.floor(Date.now() / 1000);
    
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
    
    // Check cooldown (24 hours)
    const cooldown = 24 * 60 * 60; // 24 hours in seconds
    const timeSinceLastDaily = now - (economyData.last_daily || 0);
    
    if (timeSinceLastDaily < cooldown) {
      const timeLeft = cooldown - timeSinceLastDaily;
      const hours = Math.floor(timeLeft / 3600);
      const minutes = Math.floor((timeLeft % 3600) / 60);
      
      return interaction.reply({
        content: `⏰ You've already claimed your daily reward! Come back in **${hours}h ${minutes}m**.`,
        ephemeral: true
      });
    }
    
    // Calculate reward
    const dailyReward = client.config.features.economy.dailyReward || 100;
    const newBalance = economyData.balance + dailyReward;
    
    // Update database
    queries.upsertEconomy(userId, guildId, {
      balance: newBalance,
      last_daily: now
    });
    
    const currencyName = client.config.features.economy.currency?.name || 'coins';
    const currencySymbol = client.config.features.economy.currency?.symbol || '🪙';
    
    const embed = new EmbedBuilder()
      .setColor('#00ff00')
      .setTitle('🎁 Daily Reward Claimed!')
      .setDescription(`You received **${currencySymbol} ${dailyReward.toLocaleString()} ${currencyName}**!`)
      .addFields(
        { name: 'New Balance', value: `${currencySymbol} ${newBalance.toLocaleString()} ${currencyName}`, inline: true }
      )
      .setFooter({ text: 'Come back tomorrow for another reward!' })
      .setTimestamp();
    
    await interaction.reply({ embeds: [embed] });
  }
};
