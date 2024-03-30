const path = require('path');

function homePage(req, res) {
    console.log(__dirname)
    // res.sendFile(path.join(__dirname, '../../frontend/public/index.html'));
    res.render(path.join(__dirname, '../../frontend/public/charging-points.ejs'));
    // res.render('charging-points.ejs');
    // res.render('charging-points', { chargingPoints: chargingPointsData });
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
