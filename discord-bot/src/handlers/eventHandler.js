import { readdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { pathToFileURL } from 'url';
import logger from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function loadEvents(client) {
  const eventsPath = path.join(__dirname, '../events');
  const eventFiles = readdirSync(eventsPath).filter(file => file.endsWith('.js'));
  
  let loadedCount = 0;
  
  for (const file of eventFiles) {
    const filePath = path.join(eventsPath, file);
    const fileUrl = pathToFileURL(filePath).href;
    
    try {
      const event = await import(fileUrl);
      const eventData = event.default;
      
      if (!eventData || !eventData.name) {
        logger.warn(`Event file ${file} does not export a valid event object`);
        continue;
      }
      
      if (eventData.once) {
        client.once(eventData.name, (...args) => eventData.execute(...args, client));
      } else {
        client.on(eventData.name, (...args) => eventData.execute(...args, client));
      }
      
      loadedCount++;
      logger.debug(`Loaded event: ${eventData.name} from ${file}`);
    } catch (error) {
      logger.error(`Failed to load event ${file}:`, error);
    }
  }
  
  logger.info(`Loaded ${loadedCount} events`);
}
