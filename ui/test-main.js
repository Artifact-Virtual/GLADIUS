const { app, BrowserWindow } = require('electron');

console.log('app:', typeof app);

if (typeof app === 'undefined') {
    console.log('ERROR: app is undefined - electron not loading properly');
    process.exit(1);
}

app.whenReady().then(() => {
    console.log('Electron app ready!');
    const win = new BrowserWindow({ width: 800, height: 600, show: false });
    win.loadURL('data:text/html,<h1>GLADIUS Test</h1>');
    setTimeout(() => {
        console.log('Success! Quitting...');
        app.quit();
    }, 1000);
});

app.on('window-all-closed', () => app.quit());
