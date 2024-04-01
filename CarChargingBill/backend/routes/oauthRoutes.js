const express = require('express');
const router = express.Router();
const oauthController = require('../controllers/oauthController');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
passport.use(new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: process.env.GOOGLE_CALLBACK_URL
    },
    function(accessToken, refreshToken, profile, cb) {
      // In this example, the user's Google profile is supplied as the profile.
      // Normally, you would associate the Google account with a user record in your database.
      // Here, we're just passing the profile provided by Google to the callback.
      return cb(null, profile);
    }
));
passport.serializeUser(function(user, cb) {
    cb(null, user);
});
passport.deserializeUser(function(obj, cb) {
    cb(null, obj);
});
const ensureAuthenticated = (req, res, next) => {
  console.log('1: ensureAuthenticated')
  if (req.isAuthenticated()) {
    console.log('2: isAuthenticated')
    return next();
  }
  console.log('3: Do Authentication')
  res.redirect('/oauth/google');
};


router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }))
router.get('/google/callback', passport.authenticate('google', { scope: ['profile', 'email'] }), oauthController.googleCallback)

module.exports = {
    router,
    passport,
    ensureAuthenticated
};
