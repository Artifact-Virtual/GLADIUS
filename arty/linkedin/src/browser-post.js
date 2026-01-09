#!/usr/bin/env node
/**
 * LinkedIn Browser Automation - Posts to COMPANY PAGE via web interface
 */

import { chromium } from 'playwright';
import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

config({ path: path.join(__dirname, '../../.env') });

const COOKIES_PATH = path.join(__dirname, '../data/linkedin-cookies.json');
const COMPANY_ID = '91370997';  // Your company page ID

async function postToCompanyPage(content) {
    console.log('\n🔵 LinkedIn Company Page Automation\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 50
    });

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });

    // Load saved cookies
    if (fs.existsSync(COOKIES_PATH)) {
        console.log('📂 Loading saved session...');
        const cookies = JSON.parse(fs.readFileSync(COOKIES_PATH, 'utf-8'));
        await context.addCookies(cookies);
    }

    const page = await context.newPage();

    try {
        // Navigate directly to company admin page
        const adminUrl = `https://www.linkedin.com/company/${COMPANY_ID}/admin/dashboard/`;
        console.log(`🌐 Navigating to company page: ${adminUrl}`);
        await page.goto(adminUrl, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(3000);

        // Check if we need to log in
        const url = page.url();
        if (url.includes('login') || url.includes('uas/login')) {
            console.log('⚠️  Not logged in. Please log in manually...');
            console.log('   Log in and press Enter when done.\n');
            await new Promise(resolve => process.stdin.once('data', resolve));

            const cookies = await context.cookies();
            fs.mkdirSync(path.dirname(COOKIES_PATH), { recursive: true });
            fs.writeFileSync(COOKIES_PATH, JSON.stringify(cookies, null, 2));
            console.log('✅ Session saved!\n');

            await page.goto(adminUrl, { waitUntil: 'domcontentloaded' });
            await page.waitForTimeout(3000);
        }

        // Look for a "Start a post" or "Create a post" button on company page
        console.log('📝 Looking for post button...');

        // Try different selectors for company page post button
        const postButtonSelectors = [
            'button[aria-label*="Start a post"]',
            'button[aria-label*="Create a post"]',
            '.share-box-feed-entry__trigger',
            '[data-control-name="share_box_trigger"]',
            'button:has-text("Start a post")',
            'button:has-text("Create")'
        ];

        let clicked = false;
        for (const selector of postButtonSelectors) {
            try {
                const btn = await page.$(selector);
                if (btn) {
                    await btn.click();
                    clicked = true;
                    console.log(`✅ Clicked: ${selector}`);
                    break;
                }
            } catch (e) { }
        }

        if (!clicked) {
            // Try clicking any visible "Start a post" text
            const startPostLink = await page.getByText('Start a post').first();
            if (startPostLink) {
                await startPostLink.click();
                clicked = true;
                console.log('✅ Clicked "Start a post" link');
            }
        }

        if (!clicked) {
            console.log('⚠️  Could not find post button. Taking screenshot...');
            await page.screenshot({ path: 'linkedin-debug.png' });
            throw new Error('Post button not found');
        }

        await page.waitForTimeout(2000);

        // Type the content
        console.log('✏️  Writing content...');
        const editorSelectors = [
            '.ql-editor',
            '[contenteditable="true"]',
            'div[role="textbox"]'
        ];

        let typed = false;
        for (const selector of editorSelectors) {
            try {
                const editor = await page.waitForSelector(selector, { timeout: 5000 });
                if (editor) {
                    await editor.click();
                    await page.keyboard.type(content, { delay: 15 });
                    typed = true;
                    console.log(`✅ Typed into: ${selector}`);
                    break;
                }
            } catch (e) { }
        }

        if (!typed) {
            throw new Error('Could not find text editor');
        }

        await page.waitForTimeout(1000);

        // Click Post button
        console.log('📤 Posting...');
        const postSubmitSelectors = [
            'button.share-actions__primary-action',
            'button[aria-label="Post"]',
            'button:has-text("Post")'
        ];

        for (const selector of postSubmitSelectors) {
            try {
                const btn = await page.$(selector);
                if (btn) {
                    await btn.click();
                    console.log(`✅ Clicked submit: ${selector}`);
                    break;
                }
            } catch (e) { }
        }

        await page.waitForTimeout(3000);

        // Save cookies
        const cookies = await context.cookies();
        fs.writeFileSync(COOKIES_PATH, JSON.stringify(cookies, null, 2));

        console.log('\n🎉 Successfully posted to company page!\n');
        console.log(`   Content: ${content.substring(0, 50)}...`);

        return { success: true };

    } catch (error) {
        console.error('\n❌ Error:', error.message);
        await page.screenshot({ path: 'linkedin-error.png' });
        return { success: false, error: error.message };
    } finally {
        await page.waitForTimeout(2000);
        await browser.close();
    }
}

const content = process.argv[2];
if (!content) {
    console.log(`
Usage: node browser-post.js "Your post content"

Posts to company page ID: ${COMPANY_ID}
`);
    process.exit(1);
}

postToCompanyPage(content);
