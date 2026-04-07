require('dotenv').config({ path: '../.env' });
const express = require('express');
const rateLimit = require('express-rate-limit');
const axios = require('axios');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Fix for ngrok/proxy rate limiting
app.set('trust proxy', true);

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

// Twilio Setup
const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID || 'fake';
const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN || 'fake';
const twilioClient = require('twilio')(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);

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
    // 1. Immediately reply to Twilio with empty TwiML to prevent timeouts
    const MessagingResponse = require('twilio').twiml.MessagingResponse;
    const twiml = new MessagingResponse();
    res.type('text/xml').send(twiml.toString());

    // 2. Parse incoming user message asynchronously
    const { From, Body, To } = req.body;
    if (!From || !Body) return;

    try {
        console.log(`Received WhatsApp from ${From}: ${Body}`);
        const response = await axios.post(AGENT_URL, {
            phone_number: From,
            message: Body
        });

        const reply = response.data.reply;
        console.log(`Agent reply to ${From}: ${reply}`);

        // 3. Send response back effectively interactive using Twilio client
        await twilioClient.messages.create({
            from: To,
            to: From,
            body: reply
        });

    } catch (error) {
        console.error('Error handling incoming WhatsApp:', error.message);
    }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Node.js Gateway running on port ${port}`);
});
