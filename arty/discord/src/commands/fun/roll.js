import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export default {
  name: 'roll',
  description: 'Roll dice',
  aliases: ['dice', 'random'],
  cooldown: 2000,
  data: new SlashCommandBuilder()
    .setName('roll')
    .setDescription('Roll dice')
    .addIntegerOption(option =>
      option.setName('sides')
        .setDescription('Number of sides on the die (default: 6)')
        .setMinValue(2)
        .setMaxValue(100)
        .setRequired(false))
    .addIntegerOption(option =>
      option.setName('count')
        .setDescription('Number of dice to roll (default: 1)')
        .setMinValue(1)
        .setMaxValue(10)
        .setRequired(false)),
  
  async execute(interaction, client) {
    const sides = interaction.options?.getInteger('sides') || 6;
    const count = interaction.options?.getInteger('count') || 1;
    
    const rolls = [];
    let total = 0;
    
    for (let i = 0; i < count; i++) {
      const roll = Math.floor(Math.random() * sides) + 1;
      rolls.push(roll);
      total += roll;
    }
    
    const embed = new EmbedBuilder()
      .setColor(client.config.bot.embedColor || '#5865F2')
      .setTitle('🎲 Dice Roll')
      .addFields(
        { name: 'Dice', value: `${count}d${sides}`, inline: true },
        { name: 'Result', value: rolls.join(', '), inline: true },
        { name: 'Total', value: total.toString(), inline: true }
      )
      .setFooter({ text: `Rolled by ${interaction.user.username}` })
      .setTimestamp();
    
    await interaction.reply({ embeds: [embed] });
  }
};
