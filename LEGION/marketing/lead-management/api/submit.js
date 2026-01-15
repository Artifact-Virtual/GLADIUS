// api/submit.js
const fetch = require('node-fetch');

const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/YOUR_DEPLOYED_SCRIPT_ID/exec';

module.exports = async (req, res) => {
  const { name, email, phone } = req.body;

  try {
    const response = await fetch(GOOGLE_SCRIPT_URL, {
      method: 'POST',
      body: JSON.stringify({ name, email, phone }),
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) throw new Error("Failed to submit to Google Sheet");
    res.status(200).json({ success: true, msg: 'Submitted successfully' });
  } catch (err) {
    res.status(500).json({ success: false, msg: err.message });
  }
};
