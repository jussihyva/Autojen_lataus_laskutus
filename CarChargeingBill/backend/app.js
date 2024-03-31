const express = require('express');
const session = require('express-session');
const https = require('https');
const fs = require('fs');
const cors = require('cors')
const oauthRoutes = require('./routes/oauthRoutes');
const apiRoutes = require('./routes/apiRoutes');
const webRoutes = require('./routes/webRoutes');
const path = require('path');

const PORT = process.env.PORT || 4242;
const cert_options = {
  key: fs.readFileSync('/home/juhani/.ssh/privkey.pem'),
  cert: fs.readFileSync('/etc/ssl/certs/cert.pem')
};
const staticPath = path.join(__dirname, '..', 'frontend')
console.log(`1: ${staticPath}`)

const app = express();
app.use(express.json());
app.use(cors())
app.use(express.static(staticPath));
app.set('view engine', 'ejs');
app.set('views', path.join(staticPath, 'public'));
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false }));
app.use(oauthRoutes.passport.initialize());
app.use(oauthRoutes.passport.session());
const ensureAuthenticated = (req, res, next) => {
  console.log('1: ensureAuthenticated')
  if (req.isAuthenticated()) {
    console.log('2: isAuthenticated')
    return next();
  }
  console.log('3: Do Authentication')
  res.redirect('/oauth/google');
};

app.use('/oauth', oauthRoutes.router);
app.use('/api', ensureAuthenticated, apiRoutes.router);
app.use('/', ensureAuthenticated, webRoutes.router);

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something went wrong!');
});

https.createServer(cert_options, app, (req, res) => {
  res.writeHead(200);
  res.end('hello world\n');
}).listen(PORT, () => {
  console.log(`Server is running on https://localhost:${PORT}`);
});
