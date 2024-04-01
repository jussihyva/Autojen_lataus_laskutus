const path = require('path');

function googleCallback(req, res) {
    res.redirect('/home');
}

module.exports = {
    googleCallback
};
