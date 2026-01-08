import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import os from 'os';
import { version as djsVersion } from 'discord.js';

export default {
  name: 'ping',
  description: 'Check the bot\'s latency and status',
  aliases: ['latency', 'status'],
  cooldown: 3000,
  data: new SlashCommandBuilder()
    .setName('ping')
    .setDescription('Check the bot\'s latency and status'),
  
  async execute(interaction, client) {
    const sent = await interaction.reply({ content: '🏓 Pinging...', fetchReply: true });
    
    const uptime = process.uptime();
    const days = Math.floor(uptime / 86400);
    const hours = Math.floor(uptime / 3600) % 24;
    const minutes = Math.floor(uptime / 60) % 60;
    const seconds = Math.floor(uptime % 60);
    
    const embed = new EmbedBuilder()
      .setColor(client.config.bot.embedColor || '#5865F2')
      .setTitle('🏓 Pong!')
      .addFields(
        { name: '📡 Websocket Latency', value: `\`${client.ws.ping}ms\``, inline: true },
        { name: '🔄 Roundtrip Latency', value: `\`${sent.createdTimestamp - interaction.createdTimestamp}ms\``, inline: true },
        { name: '⏱️ Uptime', value: `\`${days}d ${hours}h ${minutes}m ${seconds}s\``, inline: true },
        { name: '💾 Memory Usage', value: `\`${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB\``, inline: true },
        { name: '📊 Servers', value: `\`${client.guilds.cache.size}\``, inline: true },
        { name: '👥 Users', value: `\`${client.guilds.cache.reduce((a, g) => a + g.memberCount, 0)}\``, inline: true },
        { name: '📦 Node.js', value: `\`${process.version}\``, inline: true },
        { name: '🤖 Discord.js', value: `\`v${djsVersion}\``, inline: true },
        { name: '🖥️ OS', value: `\`${os.type()} ${os.release()}\``, inline: true }
      )
      .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
      .setTimestamp();
    
    await interaction.editReply({ content: null, embeds: [embed] });
  }
};
