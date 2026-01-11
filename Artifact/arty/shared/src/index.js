const winston = require('winston');

// Configuration for shared logger
const createLogger = (serviceName) => {
    return winston.createLogger({
        level: 'info',
        defaultMeta: { service: serviceName },
        format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json()
        ),
        transports: [
            new winston.transports.Console(),
            new winston.transports.File({ filename: 'error.log', level: 'error' }),
            new winston.transports.File({ filename: 'combined.log' }),
        ],
    });
};

module.exports = {
    createLogger
};
