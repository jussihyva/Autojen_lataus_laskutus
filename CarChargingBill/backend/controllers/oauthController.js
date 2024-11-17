const path = require('path');

function googleCallback(req, res, next) {
    res.redirect('/');
}

module.exports = {
    googleCallback
};
