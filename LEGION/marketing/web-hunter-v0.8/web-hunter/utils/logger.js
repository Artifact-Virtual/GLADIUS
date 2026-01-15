const fs = require('fs');

class Logger {
    constructor(logFilePath) {
        this.logFilePath = logFilePath;
    }

    log(message) {
        const timestamp = new Date().toISOString();
        const logMessage = `${timestamp} - ${message}\n`;
        fs.appendFileSync(this.logFilePath, logMessage, 'utf8');
    }

    info(message) {
        this.log(`INFO: ${message}`);
    }

    warn(message) {
        this.log(`WARN: ${message}`);
    }

    error(message) {
        this.log(`ERROR: ${message}`);
    }
}

const logger = new Logger('application.log');
module.exports = logger;