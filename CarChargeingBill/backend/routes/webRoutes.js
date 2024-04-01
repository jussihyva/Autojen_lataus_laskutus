const express = require('express');
const router = express.Router();
const webController = require('../controllers/webController');
const oauthRoutes = require('./oauthRoutes')

router.get('/', oauthRoutes.ensureAuthenticated, webController.homePage);
router.get('/home', oauthRoutes.ensureAuthenticated, webController.homePage);
router.get('/about', webController.aboutPage);
router.get('/contact', webController.contactPage);

module.exports = {
    router
};
