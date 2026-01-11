import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits, ChannelType } from 'discord.js';
import { queries } from '../../utils/database.js';

export default {
  name: 'setup',
  description: 'Configure bot settings for this server',
  aliases: ['config', 'configure'],
  permissions: [PermissionFlagsBits.Administrator],
  cooldown: 5000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('setup')
    .setDescription('Configure bot settings for this server')
    .addSubcommand(subcommand =>
      subcommand
        .setName('welcome')
        .setDescription('Set up welcome messages')
        .addChannelOption(option =>
          option.setName('channel')
            .setDescription('Channel for welcome messages')
            .addChannelTypes(ChannelType.GuildText)
            .setRequired(true)))
    .addSubcommand(subcommand =>
      subcommand
        .setName('goodbye')
        .setDescription('Set up goodbye messages')
        .addChannelOption(option =>
          option.setName('channel')
            .setDescription('Channel for goodbye messages')
            .addChannelTypes(ChannelType.GuildText)
            .setRequired(true)))
    .addSubcommand(subcommand =>
      subcommand
        .setName('logs')
        .setDescription('Set up logging channel')
        .addChannelOption(option =>
          option.setName('channel')
            .setDescription('Channel for general logs')
            .addChannelTypes(ChannelType.GuildText)
            .setRequired(true)))
    .addSubcommand(subcommand =>
      subcommand
        .setName('modlogs')
        .setDescription('Set up moderation logs channel')
        .addChannelOption(option =>
          option.setName('channel')
            .setDescription('Channel for moderation logs')
            .addChannelTypes(ChannelType.GuildText)
            .setRequired(true)))
    .addSubcommand(subcommand =>
      subcommand
        .setName('prefix')
        .setDescription('Set custom command prefix')
        .addStringOption(option =>
          option.setName('prefix')
            .setDescription('New prefix (e.g., !, ?, .)')
            .setRequired(true)
            .setMaxLength(5)))
    .addSubcommand(subcommand =>
      subcommand
        .setName('view')
        .setDescription('View current server configuration'))
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
  
  async execute(interaction, client) {
    const subcommand = interaction.options.getSubcommand();
    const guildId = interaction.guild.id;
    
    switch (subcommand) {
      case 'welcome': {
        const channel = interaction.options.getChannel('channel');
        
        queries.upsertGuild(guildId, { welcome_channel_id: channel.id });
        
        const embed = new EmbedBuilder()
          .setColor('#00ff00')
          .setTitle('✅ Welcome Channel Set')
          .setDescription(`Welcome messages will now be sent to ${channel.toString()}`)
          .addFields({ name: 'Next Steps', value: 'Customize welcome messages in `config.json`' })
          .setTimestamp();
        
        await interaction.reply({ embeds: [embed] });
        break;
      }
      
      case 'goodbye': {
        const channel = interaction.options.getChannel('channel');
        
        queries.upsertGuild(guildId, { goodbye_channel_id: channel.id });
        
        const embed = new EmbedBuilder()
          .setColor('#00ff00')
          .setTitle('✅ Goodbye Channel Set')
          .setDescription(`Goodbye messages will now be sent to ${channel.toString()}`)
          .addFields({ name: 'Next Steps', value: 'Customize goodbye messages in `config.json`' })
          .setTimestamp();
        
        await interaction.reply({ embeds: [embed] });
        break;
      }
      
      case 'logs': {
        const channel = interaction.options.getChannel('channel');
        
        queries.upsertGuild(guildId, { log_channel_id: channel.id });
        
        const embed = new EmbedBuilder()
          .setColor('#00ff00')
          .setTitle('✅ Log Channel Set')
          .setDescription(`General logs will now be sent to ${channel.toString()}`)
          .setTimestamp();
        
        await interaction.reply({ embeds: [embed] });
        break;
      }
      
      case 'modlogs': {
        const channel = interaction.options.getChannel('channel');
        
        queries.upsertGuild(guildId, { mod_log_channel_id: channel.id });
        
        const embed = new EmbedBuilder()
          .setColor('#00ff00')
          .setTitle('✅ Moderation Log Channel Set')
          .setDescription(`Moderation logs will now be sent to ${channel.toString()}`)
          .setTimestamp();
        
        await interaction.reply({ embeds: [embed] });
        break;
      }
      
      case 'prefix': {
        const prefix = interaction.options.getString('prefix');
        
        queries.upsertGuild(guildId, { prefix });
        
        const embed = new EmbedBuilder()
          .setColor('#00ff00')
          .setTitle('✅ Prefix Updated')
          .setDescription(`Command prefix has been set to: \`${prefix}\``)
          .addFields({ name: 'Example', value: `\`${prefix}help\``, inline: true })
          .setTimestamp();
        
        await interaction.reply({ embeds: [embed] });
        break;
      }
      
      case 'view': {
        const guildData = queries.getGuild(guildId);
        
        if (!guildData) {
          return interaction.reply({ 
            content: '❌ No configuration found. Use setup commands to configure the bot.',
            ephemeral: true 
          });
        }
        
        const embed = new EmbedBuilder()
          .setColor(client.config.bot.embedColor || '#5865F2')
          .setTitle('⚙️ Server Configuration')
          .addFields(
            { 
              name: 'Prefix', 
              value: guildData.prefix || process.env.PREFIX || '!', 
              inline: true 
            },
            { 
              name: 'Welcome Channel', 
              value: guildData.welcome_channel_id ? `<#${guildData.welcome_channel_id}>` : 'Not set', 
              inline: true 
            },
            { 
              name: 'Goodbye Channel', 
              value: guildData.goodbye_channel_id ? `<#${guildData.goodbye_channel_id}>` : 'Not set', 
              inline: true 
            },
            { 
              name: 'Log Channel', 
              value: guildData.log_channel_id ? `<#${guildData.log_channel_id}>` : 'Not set', 
              inline: true 
            },
            { 
              name: 'Mod Log Channel', 
              value: guildData.mod_log_channel_id ? `<#${guildData.mod_log_channel_id}>` : 'Not set', 
              inline: true 
            },
            { 
              name: 'Muted Role', 
              value: guildData.muted_role_id ? `<@&${guildData.muted_role_id}>` : 'Not set', 
              inline: true 
            }
          )
          .setFooter({ text: 'Use /setup to change these settings' })
          .setTimestamp();
        
        await interaction.reply({ embeds: [embed] });
        break;
      }
    }
  }
};
