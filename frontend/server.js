const express = require('express');
const path = require('path');

const app = express();
const PORT = 3000;

app.get('/app', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'app.html'));
});

app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, () => {
    console.log(`Frontend server running at http://localhost:${PORT}`);
});
