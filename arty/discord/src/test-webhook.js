import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import axios from 'axios';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Calculate path: src -> discord -> arty
const envPath = path.resolve(__dirname, '../../.env');
console.log(`Debug: Creating .env path at: ${envPath}`);

// Load centralized .env
config({ path: envPath });

async function testWebhook() {
    const webhookUrl = process.env.WEBHOOK_URL;

    if (!webhookUrl) {
        if (fs.existsSync(envPath)) {
            console.log("File exists but var not found.");
        } else {
            console.log("File does not exist at path.");
        }
        console.error('❌ No WEBHOOK_URL found in process.env');
        process.exit(1);
    }

    console.log(`Testing Webhook: ${webhookUrl.substring(0, 50)}...`);

    try {
        await axios.post(webhookUrl, {
            content: "✅ **Arty Integration Test**\nWebhook successfully connected!",
            username: "Arty System"
        });
        console.log('✅ Webhook test successful! Message sent.');
    } catch (error) {
        console.error('❌ Webhook test failed:', error.message);
        if (error.response) {
            console.error('Status:', error.response.status);
        }
    }
}

testWebhook();
