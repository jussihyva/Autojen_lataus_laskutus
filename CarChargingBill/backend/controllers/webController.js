const path = require('path');

function homePage(req, res) {
    console.log(`homePage: ${req}`)
    res.render(path.join(__dirname, '../../frontend/public/index.ejs'), { content: 'home' })
}

function aboutPage(req, res) {
    res.send('About us page');
}

function contactPage(req, res) {
    res.send('Contact us page');
}

module.exports = {
    homePage,
    aboutPage,
    contactPage
};
