# Artifact Web Hunter

Artifact Web Hunter is a web scraping and lead enrichment tool designed to automate the process of gathering and enhancing contact information from various online sources. This project utilizes Puppeteer for web scraping and provides a structured approach to managing leads.

## Project Structure

```
artifact-web-hunter/
├── config/
│   └── profiles.json        # Search targets and tracking intents
├── data/
│   ├── leads.json           # Raw scraped contacts
│   └── enriched.json        # Enriched and scored leads
├── hunter/
│   ├── searchEngine.js      # Google/Bing search with Puppeteer
│   ├── scraper.js           # Dynamic site crawler
│   ├── enrich.js            # Lead enrichment logic
│   └── scheduler.js         # Queue, retry, and async handling
├── utils/
│   └── logger.js            # Custom logging
├── server.js                # Optional REST API for status or manual start
└── README.md                # Docs and instructions
```

## Installation

1. Unzip the project archive into your desired directory.

2. Navigate to the project directory:
   ```
   cd artifact-web-hunter
   ```

3. Install the dependencies:
   ```
   npm install
   ```

## Configuration

Before running the application, configure your search targets and tracking intents in the `config/profiles.json` file.

## Usage

To start the application, you can run the following command:
```
node server.js
```

This will start the optional REST API, allowing you to check the status or manually trigger scraping processes.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.