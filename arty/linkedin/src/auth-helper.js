import http from 'http';
import url from 'url';
import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import axios from 'axios';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Explicitly resolve the .env path
const envPath = path.resolve(__dirname, '../../.env');
console.log(`Debug: Reading .env from: ${envPath}`);

// Manually parse the .env file if it exists to ensure freshness
let envVars = {};
if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    envContent.split('\n').forEach(line => {
        const parts = line.split('=');
        if (parts.length >= 2) {
            const key = parts[0].trim();
            const value = parts.slice(1).join('=').trim();
            if (key && !key.startsWith('#')) {
                envVars[key] = value;
            }
        }
    });
}

const CLIENT_ID = envVars.LINKEDIN_CLIENT_ID || process.env.LINKEDIN_CLIENT_ID;
const CLIENT_SECRET = envVars.LINKEDIN_CLIENT_SECRET || process.env.LINKEDIN_CLIENT_SECRET;
const REDIRECT_URI = envVars.LINKEDIN_REDIRECT_URI || process.env.LINKEDIN_REDIRECT_URI || 'https://www.linkedin.com/developers/tools/oauth/redirect';
const SCOPE = 'w_member_social';

console.log(`Debug: Using Client ID: ${CLIENT_ID}`);
console.log(`Debug: Using Client Secret: ${CLIENT_SECRET ? '***' + CLIENT_SECRET.slice(-4) : 'undefined'}`);

if (!CLIENT_ID || !CLIENT_SECRET || CLIENT_ID.includes('your_client_id')) {
    console.error('❌ Error: Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env first!');
    process.exit(1);
}

const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${encodeURIComponent(SCOPE)}`;

console.log('\n🔵 LinkedIn OAuth 2.0 Authorization');
console.log('='.repeat(60));
console.log('\n📋 Step 1: Authorize the Application');
console.log('Open this URL in your browser:\n');
console.log(authUrl);
console.log('\n📋 Step 2: Copy the Authorization Code');
console.log('After authorizing, LinkedIn will show you an authorization code.');
console.log('Copy that code.\n');
console.log('📋 Step 3: Exchange Code for Token');
console.log('Run this command (replace YOUR_CODE with the code from step 2):\n');
console.log('PowerShell:');
console.log(`$body = @{
    grant_type = "authorization_code"
    code = "YOUR_CODE"
    redirect_uri = "${REDIRECT_URI}"
    client_id = "${CLIENT_ID}"
    client_secret = "${CLIENT_SECRET}"
}
Invoke-RestMethod -Uri "https://www.linkedin.com/oauth/v2/accessToken" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
`);
console.log('\nOR using curl:');
console.log(`curl -X POST "https://www.linkedin.com/oauth/v2/accessToken" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "grant_type=authorization_code" \\
  -d "code=YOUR_CODE" \\
  -d "redirect_uri=${REDIRECT_URI}" \\
  -d "client_id=${CLIENT_ID}" \\
  -d "client_secret=${CLIENT_SECRET}"
`);
console.log('\n📋 Step 4: Save the Access Token');
console.log('Copy the "access_token" from the response and add it to your .env file:');
console.log('LINKEDIN_ACCESS_TOKEN=your_token_here\n');
console.log('='.repeat(60));
