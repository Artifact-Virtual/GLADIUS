import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export default {
  name: 'userinfo',
  description: 'Display information about a user',
  aliases: ['ui', 'user', 'whois'],
  cooldown: 3000,
  guildOnly: true,
  data: new SlashCommandBuilder()
    .setName('userinfo')
    .setDescription('Display information about a user')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to get info about')
        .setRequired(false)),
  
  async execute(interaction, client) {
    const target = interaction.options?.getUser('user') || interaction.user;
    const member = await interaction.guild.members.fetch(target.id).catch(() => null);
    
    if (!member) {
      return interaction.reply({ content: '❌ User not found in this server.', ephemeral: true });
    }
    
    // Get user badges
    const flags = target.flags?.toArray() || [];
    const badges = {
      Staff: '👨‍💼',
      Partner: '🤝',
      Hypesquad: '🎉',
      BugHunterLevel1: '🐛',
      BugHunterLevel2: '🐛🐛',
      HypeSquadOnlineHouse1: '🏠',
      HypeSquadOnlineHouse2: '🏠',
      HypeSquadOnlineHouse3: '🏠',
      PremiumEarlySupporter: '💎',
      VerifiedBot: '✅',
      VerifiedDeveloper: '⚒️',
      CertifiedModerator: '🛡️',
      ActiveDeveloper: '⚡'
    };
    
    const userBadges = flags.map(flag => badges[flag] || flag).join(' ') || 'None';
    
    // Get roles
    const roles = member.roles.cache
      .filter(role => role.id !== interaction.guild.id)
      .sort((a, b) => b.position - a.position)
      .map(role => role.toString())
      .slice(0, 10);
    
    const rolesText = roles.length > 0 ? roles.join(', ') : 'None';
    const moreRoles = member.roles.cache.size - 1 > 10 ? `\n+${member.roles.cache.size - 11} more` : '';
    
    // Get permissions
    const keyPermissions = [];
    if (member.permissions.has('Administrator')) keyPermissions.push('Administrator');
    else {
      if (member.permissions.has('ManageGuild')) keyPermissions.push('Manage Server');
      if (member.permissions.has('ManageRoles')) keyPermissions.push('Manage Roles');
      if (member.permissions.has('ManageChannels')) keyPermissions.push('Manage Channels');
      if (member.permissions.has('KickMembers')) keyPermissions.push('Kick Members');
      if (member.permissions.has('BanMembers')) keyPermissions.push('Ban Members');
      if (member.permissions.has('ModerateMembers')) keyPermissions.push('Timeout Members');
    }
    
    const permissionsText = keyPermissions.length > 0 ? keyPermissions.join(', ') : 'None';
    
    // Get activity status
    const presence = member.presence;
    const status = {
      online: '🟢 Online',
      idle: '🟡 Idle',
      dnd: '🔴 Do Not Disturb',
      offline: '⚫ Offline'
    };
    
    const userStatus = status[presence?.status || 'offline'];
    
    // Get activities
    let activities = 'None';
    if (presence?.activities && presence.activities.length > 0) {
      activities = presence.activities
        .map(activity => {
          if (activity.type === 0) return `Playing ${activity.name}`;
          if (activity.type === 1) return `Streaming ${activity.name}`;
          if (activity.type === 2) return `Listening to ${activity.name}`;
          if (activity.type === 3) return `Watching ${activity.name}`;
          if (activity.type === 4) return activity.state || activity.name;
          if (activity.type === 5) return `Competing in ${activity.name}`;
          return activity.name;
        })
        .join('\n');
    }
    
    const embed = new EmbedBuilder()
      .setColor(member.displayHexColor || client.config.bot.embedColor || '#5865F2')
      .setTitle(`👤 ${target.username}'s Information`)
      .setThumbnail(target.displayAvatarURL({ dynamic: true, size: 512 }))
      .addFields(
        { name: '📝 Username', value: target.tag, inline: true },
        { name: '🆔 User ID', value: target.id, inline: true },
        { name: '🤖 Bot', value: target.bot ? 'Yes' : 'No', inline: true },
        { name: '📅 Account Created', value: `<t:${Math.floor(target.createdTimestamp / 1000)}:F>\n(<t:${Math.floor(target.createdTimestamp / 1000)}:R>)`, inline: true },
        { name: '📥 Joined Server', value: member.joinedAt ? `<t:${Math.floor(member.joinedTimestamp / 1000)}:F>\n(<t:${Math.floor(member.joinedTimestamp / 1000)}:R>)` : 'Unknown', inline: true },
        { name: '💭 Status', value: userStatus, inline: true },
        { name: '🎮 Activities', value: activities, inline: false },
        { name: '🏅 Badges', value: userBadges, inline: false },
        { name: `🎭 Roles [${member.roles.cache.size - 1}]`, value: rolesText + moreRoles, inline: false }
      )
      .setFooter({ text: client.config.bot.footer || 'Gladius Bot' })
      .setTimestamp();
    
    if (keyPermissions.length > 0) {
      embed.addFields({ name: '🔑 Key Permissions', value: permissionsText, inline: false });
    }
    
    if (member.premiumSince) {
      embed.addFields({ 
        name: '💎 Boosting Since', 
        value: `<t:${Math.floor(member.premiumSinceTimestamp / 1000)}:R>`, 
        inline: true 
      });
    }
    
    if (target.banner) {
      embed.setImage(target.bannerURL({ size: 1024 }));
    }
    
    await interaction.reply({ embeds: [embed] });
  }
};
