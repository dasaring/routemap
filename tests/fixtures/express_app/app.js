const express = require('express');
const app = express();

app.use(express.json());

// Health check defined directly on app
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/version', (req, res) => {
  res.json({ version: '1.0.0' });
});

app.post('/login', async (req, res) => {
  // auth logic
  res.json({ token: 'abc123' });
});

const usersRouter = require('./routes/users');
app.use('/api', usersRouter);

module.exports = app;
