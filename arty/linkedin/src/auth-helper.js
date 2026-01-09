import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import axios from 'axios';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const envPath = path.resolve(__dirname, '../../.env');

// Parse .env
let envVars = {};
if (fs.existsSync(envPath)) {
    fs.readFileSync(envPath, 'utf-8').split('\n').forEach(line => {
        const parts = line.split('=');
        if (parts.length >= 2) {
            const key = parts[0].trim();
            const value = parts.slice(1).join('=').trim();
            if (key && !key.startsWith('#')) envVars[key] = value;
        }
    });
}

const CLIENT_ID = envVars.LINKEDIN_CLIENT_ID;
const CLIENT_SECRET = envVars.LINKEDIN_CLIENT_SECRET;
const REDIRECT_URI = envVars.LINKEDIN_REDIRECT_URI || 'https://www.linkedin.com/developers/tools/oauth/redirect';
const SCOPE = 'w_member_social';

const authCode = process.argv[2];

if (!authCode) {
    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${encodeURIComponent(SCOPE)}`;
    console.log('\n🔵 LinkedIn OAuth - w_member_social only\n');
    console.log('Open this URL:\n');
    console.log(authUrl);
    console.log('\nThen run: node auth-helper.js YOUR_CODE\n');
    process.exit(0);
}

(async () => {
    try {
        console.log('\n🔄 Exchanging code for token...\n');

        const params = new URLSearchParams();
        params.append('grant_type', 'authorization_code');
        params.append('code', authCode);
        params.append('redirect_uri', REDIRECT_URI);
        params.append('client_id', CLIENT_ID);
        params.append('client_secret', CLIENT_SECRET);

        const response = await axios.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            params,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );

        const accessToken = response.data.access_token;
        console.log('✅ Access Token obtained!\n');
        console.log(`Token: ${accessToken}\n`);

        // Save to .env
        let envContent = fs.readFileSync(envPath, 'utf-8');
        envContent = envContent.replace(/LINKEDIN_ACCESS_TOKEN=.*/, `LINKEDIN_ACCESS_TOKEN=${accessToken}`);
        fs.writeFileSync(envPath, envContent);

        console.log('✅ Token saved to .env\n');
        console.log('='.repeat(60));
        console.log('\n⚠️  IMPORTANT: You need to set your Person URN manually.\n');
        console.log('To find it:');
        console.log('1. Go to https://www.linkedin.com/in/YOUR-PROFILE/');
        console.log('2. Open browser DevTools (F12) → Console');
        console.log('3. Run: document.body.innerHTML.match(/urn:li:fsd_profile:([^"]+)/)[1]');
        console.log('4. Copy that ID and add to .env:');
        console.log('   LINKEDIN_PERSON_URN=urn:li:person:YOUR_ID\n');
        console.log('='.repeat(60) + '\n');

    } catch (error) {
        console.error('❌ Error:', error.response?.data || error.message);
    }
})();
