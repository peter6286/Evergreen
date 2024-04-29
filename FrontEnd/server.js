const express = require('express');
const AWSIoT = require('aws-iot-device-sdk');
const cors = require('cors');
require('dotenv').config({ path: '/Users/loriasun/Desktop/CS 598 Smart City/598_EverGreen/FrontEnd/local.env' });


const app = express();
app.use(cors());
const port = process.env.PORT || 3000;

// Load MQTT client credentials from environment variables
const device = AWSIoT.device({
    keyPath: process.env.KEY_PATH,
    certPath: process.env.CERT_PATH,
    caPath: process.env.CA_PATH,
    clientId: process.env.CLIENT_ID,
    host: process.env.AWS_IOT_ENDPOINT
});

device.on('connect', () => {
    console.log('Connected to AWS IoT');
});

app.use(express.static('public'));  // Serve static files from 'public' directory

app.get('/trigger-device-function', (req, res) => {
    console.log('trigger water pump!!!')
    const command = JSON.stringify({ 'command': "start_pump" });  // Define your command structure
    device.publish('topic/command', command, { qos: 0 }, (err) => {
        if (err) {
            res.status(500).send('Failed to send command');
            console.error('Failed to publish message:', err);
        } else {
            res.send('Command sent successfully');
        }
    });
});

app.listen(port, () => {
  console.log(`Server running on port http://127.0.0.1:${port}`);
});
