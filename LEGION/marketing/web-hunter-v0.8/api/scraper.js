import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import { pipeline } from '@xenova/transformers';

puppeteer.use(StealthPlugin());

// Load NER and summarization pipelines once
let nerPipe, sumPipe;
async function getNerPipe() {
  if (!nerPipe) nerPipe = await pipeline('ner', 'Xenova/bert-base-NER');
  return nerPipe;
}
async function getSumPipe() {
  if (!sumPipe) sumPipe = await pipeline('summarization', 'Xenova/distilbart-cnn-6-6');
  return sumPipe;
}

function extractEmails(text) {
  return text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || [];
}

export async function scrapeAndExtract(url) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2' });
  const text = await page.evaluate(() => document.body.innerText);
  const emails = extractEmails(text);
  // Named Entity Recognition
  const ner = await (await getNerPipe())(text, { aggregation_strategy: 'simple' });
  const entities = ner.map(e => ({ entity: e.entity_group, word: e.word }));
  // Summarization
  const summary = (await (await getSumPipe())(text.slice(0, 2000))).summary_text;
  await browser.close();
  return {
    url,
    emails,
    namedEntities: entities,
    summary,
    timestamp: new Date().toISOString()
  };
}
