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
const SCOPE = 'w_member_social';  // Just posting scope

const authCode = process.argv[2];

if (!authCode) {
    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${encodeURIComponent(SCOPE)}`;
    console.log('\n🔵 LinkedIn OAuth - w_member_social\n');
    console.log('Open this URL:\n');
    console.log(authUrl);
    console.log('\nPaste the code you get here.\n');
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

        // Save token
        let envContent = fs.readFileSync(envPath, 'utf-8');
        envContent = envContent.replace(/LINKEDIN_ACCESS_TOKEN=.*/, `LINKEDIN_ACCESS_TOKEN=${accessToken}`);
        fs.writeFileSync(envPath, envContent);
        console.log('✅ Token saved to .env\n');

        // Try to get member info using /v2/me
        console.log('🔄 Attempting to get member info...\n');

        try {
            const meResponse = await axios.get('https://api.linkedin.com/v2/me', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'X-Restli-Protocol-Version': '2.0.0'
                }
            });

            const memberId = meResponse.data.id;
            const personUrn = `urn:li:person:${memberId}`;

            console.log('✅ Got member info!');
            console.log(`   Member ID: ${memberId}`);
            console.log(`   Person URN: ${personUrn}\n`);

            // Save person URN
            envContent = fs.readFileSync(envPath, 'utf-8');
            envContent = envContent.replace(/LINKEDIN_PERSON_URN=.*/, `LINKEDIN_PERSON_URN=${personUrn}`);
            fs.writeFileSync(envPath, envContent);
            console.log('✅ Person URN saved to .env\n');
            console.log('🎉 Setup complete! Run: npm run linkedin:start\n');

        } catch (meError) {
            console.log('⚠️  Could not get member info (expected without profile scope)\n');
            console.log('Trying to introspect token...\n');

            // Try token introspection
            try {
                const introResponse = await axios.post(
                    'https://www.linkedin.com/oauth/v2/introspectToken',
                    new URLSearchParams({
                        'token': accessToken,
                        'client_id': CLIENT_ID,
                        'client_secret': CLIENT_SECRET
                    }),
                    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
                );
                console.log('Token info:', introResponse.data);
                if (introResponse.data.authorized_member) {
                    const memberId = introResponse.data.authorized_member;
                    envContent = fs.readFileSync(envPath, 'utf-8');
                    envContent = envContent.replace(/LINKEDIN_PERSON_URN=.*/, `LINKEDIN_PERSON_URN=urn:li:member:${memberId}`);
                    fs.writeFileSync(envPath, envContent);
                    console.log(`✅ Member ID found and saved: urn:li:member:${memberId}\n`);
                }
            } catch (intErr) {
                console.log('Token introspection also failed:', intErr.response?.data || intErr.message);
            }

            console.log('\n⚠️  Manual setup required:');
            console.log('You need to find your LinkedIn member ID manually.');
            console.log('One way: Go to LinkedIn, view page source, search for your numeric member ID.\n');
        }

    } catch (error) {
        console.error('❌ Error:', error.response?.data || error.message);
    }
})();
