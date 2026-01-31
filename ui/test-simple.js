console.log('Process type:', process.type);
console.log('Is main process:', process.type === 'browser');

if (process.type === 'browser') {
    const { app } = require('electron');
    console.log('app loaded:', typeof app);
} else {
    console.log('Not running in Electron main process!');
}
