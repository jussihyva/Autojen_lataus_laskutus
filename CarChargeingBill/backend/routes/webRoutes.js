// backend/routes/webRoutes.js

const express = require('express');
const router = express.Router();
const webController = require('../controllers/webController');

// Define web routes
router.get('/', webController.homePage);
router.get('/home', webController.homePage);
router.get('/about', webController.aboutPage);
router.get('/contact', webController.contactPage);

module.exports = router;
