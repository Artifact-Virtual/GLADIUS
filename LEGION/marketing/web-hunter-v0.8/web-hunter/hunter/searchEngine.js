const puppeteer = require('puppeteer');

async function searchGoogle(query) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(`https://www.google.com/search?q=${encodeURIComponent(query)}`);
    
    const results = await page.evaluate(() => {
        const items = Array.from(document.querySelectorAll('h3'));
        return items.map(item => ({
            title: item.innerText,
            link: item.parentElement.href
        }));
    });

    await browser.close();
    return results;
}

async function searchBing(query) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(`https://www.bing.com/search?q=${encodeURIComponent(query)}`);
    
    const results = await page.evaluate(() => {
        const items = Array.from(document.querySelectorAll('h2'));
        return items.map(item => ({
            title: item.innerText,
            link: item.parentElement.href
        }));
    });

    await browser.close();
    return results;
}

module.exports = {
    searchGoogle,
    searchBing
};