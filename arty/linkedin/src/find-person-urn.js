import axios from 'axios';
import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

config({ path: path.join(__dirname, '../../.env') });

const token = process.env.LINKEDIN_ACCESS_TOKEN;

async function getPersonURN() {
    try {
        // Try to create a test post to get the author URN from the response
        const response = await axios.post(
            'https://api.linkedin.com/v2/ugcPosts',
            {
                author: 'urn:li:person:PLACEHOLDER',
                lifecycleState: 'DRAFT',
                specificContent: {
                    'com.linkedin.ugc.ShareContent': {
                        shareCommentary: {
                            text: 'Test'
                        },
                        shareMediaCategory: 'NONE'
                    }
                },
                visibility: {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            },
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-Restli-Protocol-Version': '2.0.0'
                }
            }
        );
        console.log('Response:', response.data);
    } catch (error) {
        if (error.response) {
            console.log('Error response:', error.response.data);
            console.log('Status:', error.response.status);
        } else {
            console.log('Error:', error.message);
        }
    }
}

console.log('\n🔍 Attempting to discover Person URN...\n');
console.log('Please go to your LinkedIn profile page and look at the URL.');
console.log('It should be: https://www.linkedin.com/in/YOUR-PROFILE-NAME/');
console.log('\nYour Person URN format is: urn:li:person:ENCODED_ID');
console.log('\nTo find your numeric ID:');
console.log('1. Go to: https://www.linkedin.com/');
console.log('2. Click on "Me" dropdown');
console.log('3. Right-click "View Profile" and inspect element');
console.log('4. Look for data-member-id or similar attribute\n');

getPersonURN();
