// cron.js
const cron = require('node-cron');
const fs = require('fs');
const { hunt } = require('./hunter/scheduler');
const profiles = require('./config/profiles.json');

// Logger
function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  fs.appendFileSync('./logs/cron.log', line);
}

// 🧠 Schedule per profile
profiles.forEach(profile => {
  let schedule = profile.interval === 'daily' ? '0 6 * * *' :
                 profile.interval === 'weekly' ? '0 8 * * MON' : '0 */12 * * *';

  cron.schedule(schedule, async () => {
    log(`🔍 Running profile: ${profile.topic}`);
    try {
      const urls = profile.keywords.map(keyword =>
        `https://www.google.com/search?q=${encodeURIComponent(keyword)}+site:${profile.domains.join('+')}`
      );
      await hunt(urls);
      log(`✅ Completed: ${profile.topic}`);
    } catch (err) {
      log(`❌ Failed: ${profile.topic} - ${err.message}`);
    }
  });
});
