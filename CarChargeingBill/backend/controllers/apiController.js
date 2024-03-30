const { error } = require('console');
const fs = require('fs')
const path = require('path')

function getCarParkingPlaces(req, res) {
    const jsonFilePath =  path.join(__dirname, '..', '..', 'python/data/Chargeing_point_name.json')
    console.log(jsonFilePath)
    fs.readFile(jsonFilePath, 'utf8', (err, data) => {
        if (err) {
            console.log(err)
            res.status(500).send(`Error reading the JSON file: ${err}`);
            return;
        }
        try {
            const jsonData = JSON.parse(data);
            res.json(jsonData);
        } catch (parseErr) {
            console.log(`Invalid JSON format: ${parseErr}`);
            res.status(400).send('Invalid JSON format');
        }
      });
}

module.exports = {
    getCarParkingPlaces
};
