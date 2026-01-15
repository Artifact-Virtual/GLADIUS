# Artifact Web Hunter 2.0 (blackwidow)

Artifact Web Hunter 2.0 (blackwidow) is a next-generation, stealthy, and intelligent web scraping platform. It features:

- Advanced Puppeteer-based scraping with stealth plugins for undetectable operation
- NLP-based extraction of nouns, emails, phone numbers, and project details
- Bulk scraping: input and process multiple URLs at once
- Niche/industry researcher (coming soon): discover and scrape websites by industry
- REST API for scraping and results
- Modern React front end for viewing/searching data
- Modular, extensible codebase
- Logging and error handling
- Ready for future AI/LLM integration

## Getting Started

### Prerequisites
- Node.js 18+
- npm

### Installation

```bash
npm install
```

### Running the Application

1. **Start the backend API:**
   ```bash
   node ./api/index.js
   ```
2. **Start the React front end:**
   ```bash
   npm run dev
   ```
3. Open [http://localhost:5173](http://localhost:5173) in your browser.

## Usage

- Enter one or more URLs (one per line) and click "Scrape" to extract data from all sites.
- View results in the UI, including emails, phone numbers, nouns, and project details.

## Bulk Scraping
- Paste or type multiple URLs (one per line) in the input box.
- The backend will process each URL and return all results.

## Requirements
All backend dependencies are listed in `requirements.txt` and `package.json`.

## Branding
Artifact branding is consistent throughout the UI and documentation.

## Contributing
Pull requests and issues are welcome! Please follow the code style and contribute to the Artifact ecosystem.

## License
MIT License. See LICENSE file for details.

---

*This project is a next-generation, modular, and extensible web intelligence platform.*
