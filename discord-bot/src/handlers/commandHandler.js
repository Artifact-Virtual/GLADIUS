import { readdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { pathToFileURL } from 'url';
import logger from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function loadCommands(client) {
  const commandsPath = path.join(__dirname, '../commands');
  const commandFolders = readdirSync(commandsPath);
  
  let loadedCount = 0;
  
  for (const folder of commandFolders) {
    const folderPath = path.join(commandsPath, folder);
    const commandFiles = readdirSync(folderPath).filter(file => file.endsWith('.js'));
    
    for (const file of commandFiles) {
      const filePath = path.join(folderPath, file);
      const fileUrl = pathToFileURL(filePath).href;
      
      try {
        const command = await import(fileUrl);
        const commandData = command.default;
        
        if (!commandData) {
          logger.warn(`Command file ${file} does not export a default object`);
          continue;
        }
        
        // Load prefix command
        if (commandData.name) {
          client.commands.set(commandData.name, commandData);
          
          // Load aliases
          if (commandData.aliases && Array.isArray(commandData.aliases)) {
            commandData.aliases.forEach(alias => {
              client.commands.set(alias, commandData);
            });
          }
        }
        
        // Load slash command
        if (commandData.data) {
          client.slashCommands.set(commandData.data.name, commandData);
        }
        
        loadedCount++;
        logger.debug(`Loaded command: ${commandData.name || commandData.data?.name} from ${folder}/${file}`);
      } catch (error) {
        logger.error(`Failed to load command ${file}:`, error);
      }
    }
  }
  
  logger.info(`Loaded ${loadedCount} commands from ${commandFolders.length} categories`);
}

export function reloadCommand(client, commandName) {
  // Implementation for hot-reloading commands
  const command = client.commands.get(commandName) || client.slashCommands.get(commandName);
  if (!command) {
    return false;
  }
  
  // Clear from cache
  client.commands.delete(commandName);
  client.slashCommands.delete(commandName);
  
  // Reload would require dynamic import with cache busting
  return true;
}
