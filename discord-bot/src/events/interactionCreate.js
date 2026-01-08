import { PermissionFlagsBits } from 'discord.js';
import logger from '../utils/logger.js';
import { queries } from '../utils/database.js';

export default {
  name: 'interactionCreate',
  async execute(interaction, client) {
    // Handle slash commands
    if (interaction.isChatInputCommand()) {
      await handleSlashCommand(interaction, client);
    }
    
    // Handle button interactions
    else if (interaction.isButton()) {
      await handleButton(interaction, client);
    }
    
    // Handle select menus
    else if (interaction.isStringSelectMenu()) {
      await handleSelectMenu(interaction, client);
    }
    
    // Handle modal submits
    else if (interaction.isModalSubmit()) {
      await handleModal(interaction, client);
    }
    
    // Handle context menus
    else if (interaction.isContextMenuCommand()) {
      await handleContextMenu(interaction, client);
    }
  }
};

async function handleSlashCommand(interaction, client) {
  const command = client.slashCommands.get(interaction.commandName);
  
  if (!command) {
    return await interaction.reply({
      content: '❌ This command is not available.',
      ephemeral: true
    });
  }
  
  try {
    // Check if command requires permissions
    if (command.permissions) {
      if (!interaction.member.permissions.has(command.permissions)) {
        return await interaction.reply({
          content: '❌ You do not have permission to use this command.',
          ephemeral: true
        });
      }
    }
    
    // Check if bot has required permissions
    if (command.botPermissions) {
      if (!interaction.guild.members.me.permissions.has(command.botPermissions)) {
        return await interaction.reply({
          content: '❌ I do not have the required permissions to execute this command.',
          ephemeral: true
        });
      }
    }
    
    // Check cooldown
    if (command.cooldown) {
      const cooldownKey = `${interaction.user.id}-${command.data.name}`;
      const cooldowns = client.cooldowns;
      
      if (cooldowns.has(cooldownKey)) {
        const expirationTime = cooldowns.get(cooldownKey);
        const timeLeft = (expirationTime - Date.now()) / 1000;
        
        if (timeLeft > 0) {
          return await interaction.reply({
            content: `⏰ Please wait ${timeLeft.toFixed(1)} seconds before using this command again.`,
            ephemeral: true
          });
        }
      }
      
      cooldowns.set(cooldownKey, Date.now() + command.cooldown);
      setTimeout(() => cooldowns.delete(cooldownKey), command.cooldown);
    }
    
    // Execute command
    await command.execute(interaction, client);
    
    // Log command usage
    logger.command(
      interaction.user,
      interaction.guild,
      interaction.commandName,
      interaction.options.data.map(opt => `${opt.name}:${opt.value}`)
    );
    
  } catch (error) {
    logger.error(`Error executing slash command ${interaction.commandName}:`, error);
    
    const errorMessage = {
      content: '❌ An error occurred while executing this command.',
      ephemeral: true
    };
    
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp(errorMessage);
    } else {
      await interaction.reply(errorMessage);
    }
  }
}

async function handleButton(interaction, client) {
  const [action, ...params] = interaction.customId.split('_');
  
  try {
    switch (action) {
      case 'ticket':
        await handleTicketButton(interaction, client, params);
        break;
      case 'verify':
        await handleVerifyButton(interaction, client);
        break;
      case 'poll':
        await handlePollButton(interaction, client, params);
        break;
      case 'giveaway':
        await handleGiveawayButton(interaction, client);
        break;
      default:
        logger.warn(`Unknown button interaction: ${action}`);
    }
  } catch (error) {
    logger.error(`Error handling button ${action}:`, error);
    await interaction.reply({
      content: '❌ An error occurred while processing your request.',
      ephemeral: true
    });
  }
}

async function handleSelectMenu(interaction, client) {
  const [action, ...params] = interaction.customId.split('_');
  
  try {
    switch (action) {
      case 'ticket':
        await handleTicketSelect(interaction, client, params);
        break;
      case 'roles':
        await handleRoleSelect(interaction, client);
        break;
      default:
        logger.warn(`Unknown select menu interaction: ${action}`);
    }
  } catch (error) {
    logger.error(`Error handling select menu ${action}:`, error);
    await interaction.reply({
      content: '❌ An error occurred while processing your request.',
      ephemeral: true
    });
  }
}

async function handleModal(interaction, client) {
  const [action, ...params] = interaction.customId.split('_');
  
  try {
    switch (action) {
      case 'ticket':
        await handleTicketModal(interaction, client, params);
        break;
      default:
        logger.warn(`Unknown modal interaction: ${action}`);
    }
  } catch (error) {
    logger.error(`Error handling modal ${action}:`, error);
    await interaction.reply({
      content: '❌ An error occurred while processing your request.',
      ephemeral: true
    });
  }
}

async function handleContextMenu(interaction, client) {
  // Handle context menu commands (right-click menu)
  const command = client.slashCommands.get(interaction.commandName);
  
  if (!command) {
    return await interaction.reply({
      content: '❌ This command is not available.',
      ephemeral: true
    });
  }
  
  try {
    await command.execute(interaction, client);
  } catch (error) {
    logger.error(`Error executing context menu ${interaction.commandName}:`, error);
    await interaction.reply({
      content: '❌ An error occurred while executing this command.',
      ephemeral: true
    });
  }
}

// Placeholder handlers for button/select interactions
async function handleTicketButton(interaction, client, params) {
  // Ticket system button handling
  await interaction.reply({ content: 'Ticket system coming soon!', ephemeral: true });
}

async function handleVerifyButton(interaction, client) {
  // Verification button handling
  await interaction.reply({ content: 'Verification system coming soon!', ephemeral: true });
}

async function handlePollButton(interaction, client, params) {
  // Poll voting button handling
  await interaction.reply({ content: 'Poll system coming soon!', ephemeral: true });
}

async function handleGiveawayButton(interaction, client) {
  // Giveaway entry button handling
  await interaction.reply({ content: 'Giveaway system coming soon!', ephemeral: true });
}

async function handleTicketSelect(interaction, client, params) {
  // Ticket type selection handling
  await interaction.reply({ content: 'Ticket system coming soon!', ephemeral: true });
}

async function handleRoleSelect(interaction, client) {
  // Role selection menu handling
  await interaction.reply({ content: 'Role selection coming soon!', ephemeral: true });
}

async function handleTicketModal(interaction, client, params) {
  // Ticket creation modal handling
  await interaction.reply({ content: 'Ticket system coming soon!', ephemeral: true });
}
