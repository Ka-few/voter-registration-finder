require('dotenv').config({ path: '../.env' });
const express = require('express');
const rateLimit = require('express-rate-limit');
const axios = require('axios');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Phase 5: Rate Limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: "Too many requests, please try again later."
});
app.use(limiter);

const AT_USERNAME = process.env.AT_USERNAME || 'sandbox';
const AT_API_KEY = process.env.AT_API_KEY || 'fake';

const africastalking = require('africastalking')({
    apiKey: AT_API_KEY,
    username: AT_USERNAME
});
const sms = africastalking.SMS;

const AGENT_URL = `http://localhost:${process.env.AGENT_PORT || 8000}/chat`;

app.post('/sms/incoming', async (req, res) => {
    res.status(200).send('OK');

    const { from, text, to } = req.body;
    if (!from || !text) return;

    try {
        console.log(`Received SMS from ${from}: ${text}`);
        const response = await axios.post(AGENT_URL, {
            phone_number: from,
            message: text
        });

        const reply = response.data.reply;
        console.log(`Agent reply to ${from}: ${reply}`);

        await sms.send({
            to: [from],
            message: reply,
            from: to || ''
        });

    } catch (error) {
        console.error('Error handling incoming SMS:', error.message);
    }
});

app.post('/whatsapp/incoming', async (req, res) => {
    res.status(200).send('OK');
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Node.js Gateway running on port ${port}`);
});
