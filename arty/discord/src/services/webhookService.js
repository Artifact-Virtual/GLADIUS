import { WebhookClient, EmbedBuilder } from 'discord.js';
import logger from '../utils/logger.js';

class WebhookService {
  constructor(client) {
    this.client = client;
    this.webhooks = {
      logging: null,
      moderation: null,
      announcements: null,
      welcome: null
    };
    
    this.initializeWebhooks();
  }
  
  initializeWebhooks() {
    const config = this.client.config.webhooks;
    
    // Initialize webhook clients
    for (const [name, settings] of Object.entries(config)) {
      if (settings.enabled && settings.url) {
        try {
          this.webhooks[name] = new WebhookClient({ url: settings.url });
          logger.info(`Initialized ${name} webhook`);
        } catch (error) {
          logger.error(`Failed to initialize ${name} webhook:`, error);
        }
      }
    }
  }
  
  async sendLog(message, options = {}) {
    return this.send('logging', message, options);
  }
  
  async sendModeration(embed, options = {}) {
    return this.send('moderation', null, { embeds: [embed], ...options });
  }
  
  async sendAnnouncement(content, options = {}) {
    return this.send('announcements', content, options);
  }
  
  async sendWelcome(embed, options = {}) {
    return this.send('welcome', null, { embeds: [embed], ...options });
  }
  
  async send(webhookName, content, options = {}) {
    const webhook = this.webhooks[webhookName];
    
    if (!webhook) {
      logger.warn(`Webhook ${webhookName} is not configured or disabled`);
      return null;
    }
    
    try {
      const payload = {
        content,
        username: options.username || this.client.config.bot.name || 'Gladius Bot',
        avatarURL: options.avatarURL || this.client.user.displayAvatarURL(),
        ...options
      };
      
      const message = await webhook.send(payload);
      logger.debug(`Sent webhook message via ${webhookName}`);
      return message;
    } catch (error) {
      logger.error(`Failed to send webhook via ${webhookName}:`, error);
      return null;
    }
  }
  
  async sendEmbed(webhookName, embedData) {
    const embed = new EmbedBuilder(embedData);
    return this.send(webhookName, null, { embeds: [embed] });
  }
  
  // Utility method to create formatted log embeds
  createLogEmbed(title, description, color = '#5865F2', fields = []) {
    return new EmbedBuilder()
      .setColor(color)
      .setTitle(title)
      .setDescription(description)
      .addFields(fields)
      .setTimestamp()
      .setFooter({ text: this.client.config.bot.footer || 'Gladius Bot' });
  }
  
  // Moderation log via webhook
  async logModeration(action, moderator, target, reason) {
    const embed = this.createLogEmbed(
      `🛡️ Moderation: ${action}`,
      `Action taken against ${target.tag}`,
      '#ff9900',
      [
        { name: 'Moderator', value: `${moderator.tag} (${moderator.id})`, inline: true },
        { name: 'Target', value: `${target.tag} (${target.id})`, inline: true },
        { name: 'Action', value: action, inline: true },
        { name: 'Reason', value: reason || 'No reason provided', inline: false }
      ]
    );
    
    return this.sendModeration(embed);
  }
  
  // Message log via webhook
  async logMessage(action, message, extraInfo = '') {
    const embed = this.createLogEmbed(
      `📝 Message ${action}`,
      `Message ${action} in ${message.channel.toString()}`,
      action === 'deleted' ? '#ff0000' : '#ff9900',
      [
        { name: 'Author', value: `${message.author.tag} (${message.author.id})`, inline: true },
        { name: 'Channel', value: message.channel.toString(), inline: true },
        { name: 'Content', value: message.content.substring(0, 1000) || '*No content*', inline: false }
      ]
    );
    
    if (extraInfo) {
      embed.addFields({ name: 'Additional Info', value: extraInfo, inline: false });
    }
    
    return this.sendLog(null, { embeds: [embed] });
  }
  
  // Member log via webhook
  async logMember(action, member, extraInfo = '') {
    const embed = this.createLogEmbed(
      `👤 Member ${action}`,
      `${member.user.tag} ${action} the server`,
      action === 'joined' ? '#00ff00' : '#ff0000',
      [
        { name: 'User', value: `${member.user.tag} (${member.id})`, inline: true },
        { name: 'Account Created', value: `<t:${Math.floor(member.user.createdTimestamp / 1000)}:R>`, inline: true }
      ]
    );
    
    if (extraInfo) {
      embed.addFields({ name: 'Additional Info', value: extraInfo, inline: false });
    }
    
    return this.sendLog(null, { embeds: [embed] });
  }
}

export default WebhookService;
