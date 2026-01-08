import { REST, Routes } from 'discord.js';
import { config } from 'dotenv';
import { readdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

config();

const commands = [];
const commandsPath = path.join(__dirname, 'commands');
const commandFolders = readdirSync(commandsPath);

// Load all slash commands
console.log('Loading slash commands...');
for (const folder of commandFolders) {
  const folderPath = path.join(commandsPath, folder);
  const commandFiles = readdirSync(folderPath).filter(file => file.endsWith('.js'));
  
  for (const file of commandFiles) {
    const filePath = path.join(folderPath, file);
    const fileUrl = pathToFileURL(filePath).href;
    
    try {
      const command = await import(fileUrl);
      const commandData = command.default;
      
      if (commandData?.data) {
        commands.push(commandData.data.toJSON());
        console.log(`✓ Loaded: ${commandData.data.name} from ${folder}/${file}`);
      }
    } catch (error) {
      console.error(`✗ Failed to load command ${file}:`, error);
    }
  }
}

console.log(`\nLoaded ${commands.length} slash commands.\n`);

// Deploy commands
const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

(async () => {
  try {
    console.log(`Started refreshing ${commands.length} application (/) commands.`);
    
    if (process.argv.includes('--global')) {
      // Deploy globally
      const data = await rest.put(
        Routes.applicationCommands(process.env.CLIENT_ID),
        { body: commands }
      );
      
      console.log(`✓ Successfully deployed ${data.length} commands globally.`);
      console.log('⚠️ Note: Global commands can take up to 1 hour to update.');
    } else if (process.env.GUILD_ID) {
      // Deploy to specific guild (instant)
      const data = await rest.put(
        Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
        { body: commands }
      );
      
      console.log(`✓ Successfully deployed ${data.length} commands to guild ${process.env.GUILD_ID}.`);
    } else {
      console.error('❌ Please provide GUILD_ID in .env or use --global flag.');
      process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ Error deploying commands:', error);
    process.exit(1);
  }
})();
