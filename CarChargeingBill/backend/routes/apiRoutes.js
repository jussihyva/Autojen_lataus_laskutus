const express = require('express');
const router = express.Router();
const apiController = require('../controllers/apiController');

router.get('/getParkingPlaces', apiController.getCarParkingPlaces)

module.exports = {
    router
};
