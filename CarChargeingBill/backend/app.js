const express = require('express');
const app = express();
const apiRoutes = require('./routes/apiRoutes');
const webRoutes = require('./routes/webRoutes');
const path = require('path');
const staticPath = path.join(__dirname, '..', 'frontend')
console.log(`1: ${staticPath}`)

// Middleware for parsing JSON requests
app.use(express.json());
app.use(express.static(staticPath));
app.set('view engine', 'ejs');
app.set('views', path.join(staticPath, 'public'));

// API routes
app.use('/api', apiRoutes);

// Web routes
app.use('/', webRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something went wrong!');
});

// Start the server
const PORT = process.env.PORT || 4242;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
