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
const REDIRECT_URI = process.env.LINKEDIN_REDIRECT_URI || 'http://localhost:3000/callback';
const SCOPE = 'w_member_social r_basicprofile';

console.log(`Debug: Using Client ID: ${CLIENT_ID}`);
// Hide secret in logs
console.log(`Debug: Using Client Secret: ${CLIENT_SECRET ? '***' + CLIENT_SECRET.slice(-4) : 'undefined'}`);


if (!CLIENT_ID || !CLIENT_SECRET || CLIENT_ID.includes('your_client_id')) {
    console.error('❌ Error: Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env first!');
    process.exit(1);
}

const server = http.createServer(async (req, res) => {
    const reqUrl = url.parse(req.url, true);

    if (reqUrl.pathname === '/callback') {
        const authCode = reqUrl.query.code;
        const error = reqUrl.query.error;
        const errorDescription = reqUrl.query.error_description;

        if (error) {
            console.error(`❌ LinkedIn Error: ${error} - ${errorDescription}`);
            res.writeHead(400, { 'Content-Type': 'text/html' });
            res.end(`<h1>Authorization Failed</h1><p>${errorDescription}</p>`);
            return;
        }

        if (authCode) {
            console.log('✅ Authorization Code Received!');
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end('<h1>Authorization Successful!</h1><p>Check your terminal for the Access Token.</p>');

            // Exchange code for token
            try {
                const params = new URLSearchParams();
                params.append('grant_type', 'authorization_code');
                params.append('code', authCode);
                params.append('redirect_uri', REDIRECT_URI);
                params.append('client_id', CLIENT_ID);
                params.append('client_secret', CLIENT_SECRET);

                console.log('Exchanging code for token...');
                const response = await axios.post('https://www.linkedin.com/oauth/v2/accessToken', params, {
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                });

                const accessToken = response.data.access_token;
                console.log('\n==========================================');
                console.log('🎉 ACCESS TOKEN GENERATED SUCCESSFULLY!');
                console.log('==========================================');
                console.log(`\nLINKEDIN_ACCESS_TOKEN=${accessToken}\n`);
                console.log('Please copy the above line into your .env file.');
                console.log('==========================================\n');

                server.close(() => {
                    console.log('Server closed. You can now exit.');
                    process.exit(0);
                });

            } catch (error) {
                console.error('❌ Error exchanging token:', error.response ? error.response.data : error.message);
                console.error('Full response:', error.response);
            }
        } else {
            res.end('No code received.');
        }
    } else {
        res.end('Arty LinkedIn Auth Server Running...');
    }
});

server.listen(3000, () => {
    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${encodeURIComponent(SCOPE)}`;

    console.log('\n🔵 Arty LinkedIn Authentication Helper');
    console.log('--------------------------------------');
    console.log('1. Ensure you have added http://localhost:3000/callback to your Redirect URIs in the LinkedIn Developer Portal.');
    console.log('2. Open the following URL in your browser to authorize Arty:\n');
    console.log(authUrl);
    console.log('\n--------------------------------------');
    console.log('3. Waiting for callback on http://localhost:3000/callback ...');
});
