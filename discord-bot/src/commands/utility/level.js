import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'level',
  description: 'Check your or another user\'s level',
  aliases: ['rank', 'lvl', 'xp'],
  cooldown: 3000,
  data: new SlashCommandBuilder()
    .setName('level')
    .setDescription('Check your or another user\'s level')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to check')
        .setRequired(false)),
  
  async execute(interaction, client) {
    if (!client.config.features.leveling?.enabled) {
      return interaction.reply({ content: '❌ Leveling system is disabled.', ephemeral: true });
    }
    
    const target = interaction.options?.getUser('user') || interaction.user;
    const userId = target.id;
    const guildId = interaction.guild.id;
    
    // Get level data
    let levelData = queries.getLevel(userId, guildId);
    
    if (!levelData) {
      // Initialize level data
      queries.upsertLevel(userId, guildId, {
        xp: 0,
        level: 0,
        last_xp_time: 0,
        messages: 0
      });
      levelData = queries.getLevel(userId, guildId);
    }
    
    // Calculate required XP for next level
    const currentLevel = levelData.level;
    const currentXP = levelData.xp;
    const requiredXP = calculateRequiredXP(currentLevel);
    const progress = Math.floor((currentXP / requiredXP) * 100);
    
    // Get server leaderboard position
    const db = (await import('../../utils/database.js')).getDatabase();
    const allLevels = db.prepare('SELECT user_id, level, xp FROM levels WHERE guild_id = ? ORDER BY level DESC, xp DESC').all(guildId);
    const position = allLevels.findIndex(l => l.user_id === userId) + 1;
    
    // Create progress bar
    const progressBar = createProgressBar(progress);
    
    const embed = new EmbedBuilder()
      .setColor(client.config.bot.embedColor || '#5865F2')
      .setTitle(`📊 ${target.username}'s Level`)
      .setThumbnail(target.displayAvatarURL({ dynamic: true }))
      .addFields(
        { name: 'Level', value: `${currentLevel}`, inline: true },
        { name: 'XP', value: `${currentXP.toLocaleString()} / ${requiredXP.toLocaleString()}`, inline: true },
        { name: 'Rank', value: `#${position} / ${allLevels.length}`, inline: true },
        { name: 'Progress', value: `${progressBar} ${progress}%`, inline: false },
        { name: 'Messages', value: `${levelData.messages.toLocaleString()}`, inline: true }
      )
      .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
      .setTimestamp();
    
    await interaction.reply({ embeds: [embed] });
  }
};

function calculateRequiredXP(level) {
  // XP formula: 5 * (level ^ 2) + 50 * level + 100
  return 5 * Math.pow(level, 2) + 50 * level + 100;
}

function createProgressBar(percentage, length = 10) {
  const filled = Math.floor((percentage / 100) * length);
  const empty = length - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}
