const express = require('express');
const router  = express.Router();
const { body, validationResult } = require('express-validator');
const { rateLimit } = require('express-rate-limit');

const Subscriber = require('../models/Subscriber');
const sendEmail  = require('../utils/sendEmail');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { success: false, message: 'Too many requests. Please try again after 15 minutes.' }
});

const validateSubscribe = [
  body('email').isEmail().withMessage('Valid email is required').normalizeEmail()
];

router.post('/', limiter, validateSubscribe, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, errors: errors.array() });
  }

  const { email } = req.body;

  try {
    // Check for duplicate
    const existing = await Subscriber.findOne({ email });
    if (existing) {
      return res.json({ success: true, message: "You're already subscribed!" });
    }

    await Subscriber.create({ email });

    // Welcome email
    await sendEmail({
      to: email,
      subject: 'Welcome to Kota Stone Factory Newsletter',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #8B4513;">Welcome to Our Newsletter!</h2>
          <p>Thank you for subscribing to the Kota Stone Factory newsletter.</p>
          <p>You'll be the first to receive:</p>
          <ul>
            <li>New product launches and finishes</li>
            <li>Price updates and special offers</li>
            <li>Project inspiration and case studies</li>
            <li>Tips for using and maintaining Kota Stone</li>
          </ul>
          <hr style="border:none; border-top:1px solid #eee; margin: 20px 0;"/>
          <p>📞 <strong>+91 86194 59354</strong> &nbsp;|&nbsp; <strong>+91 90797 75779</strong></p>
          <p style="color:#888; font-size:12px;">To unsubscribe, reply to this email with "Unsubscribe".</p>
          <p style="color:#888; font-size:12px;">Kota Stone Factory, Kota, Rajasthan, India</p>
        </div>
      `
    });

    res.json({ success: true, message: "You're subscribed! Thank you." });

  } catch (err) {
    console.error('Subscribe route error:', err);
    res.status(500).json({ success: false, message: 'Something went wrong. Please try again.' });
  }
});

module.exports = router;
