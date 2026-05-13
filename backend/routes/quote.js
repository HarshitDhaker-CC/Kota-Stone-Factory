const express = require('express');
const router  = express.Router();
const { body, validationResult } = require('express-validator');
const { rateLimit } = require('express-rate-limit');

const Quote     = require('../models/Quote');
const sendEmail = require('../utils/sendEmail');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { success: false, message: 'Too many requests. Please try again after 15 minutes.' }
});

const validateQuote = [
  body('name').trim().notEmpty().withMessage('Name is required').escape(),
  body('email').isEmail().withMessage('Valid email is required').normalizeEmail(),
  body('phone').optional().trim().escape(),
  body('productType').optional().trim().escape(),
  body('quantity').optional().trim().escape(),
  body('location').optional().trim().escape(),
  body('message').optional().trim().escape()
];

router.post('/', limiter, validateQuote, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, errors: errors.array() });
  }

  const { name, email, phone, productType, quantity, location, message } = req.body;

  try {
    await Quote.create({ name, email, phone, productType, quantity, location, message });

    // Notification to owner
    await sendEmail({
      to: process.env.OWNER_EMAIL,
      subject: `New Quote Request from ${name} — Kota Stone Factory`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #8B4513;">New Quote Request 🪨</h2>
          <table style="width:100%; border-collapse: collapse;">
            <tr><td style="padding:8px; font-weight:bold; color:#555;">Name</td><td style="padding:8px;">${name}</td></tr>
            <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold; color:#555;">Email</td><td style="padding:8px;"><a href="mailto:${email}">${email}</a></td></tr>
            <tr><td style="padding:8px; font-weight:bold; color:#555;">Phone</td><td style="padding:8px;">${phone || 'Not provided'}</td></tr>
            <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold; color:#555;">Product Type</td><td style="padding:8px;">${productType || 'Not specified'}</td></tr>
            <tr><td style="padding:8px; font-weight:bold; color:#555;">Quantity</td><td style="padding:8px;">${quantity || 'Not specified'}</td></tr>
            <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold; color:#555;">Location</td><td style="padding:8px;">${location || 'Not specified'}</td></tr>
            <tr><td style="padding:8px; font-weight:bold; color:#555;">Message</td><td style="padding:8px;">${message || '—'}</td></tr>
          </table>
          <p style="color:#888; font-size:12px; margin-top:20px;">Received at ${new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST</p>
        </div>
      `
    });

    // Confirmation to customer
    await sendEmail({
      to: email,
      subject: 'Your Quote Request — Kota Stone Factory',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #8B4513;">We've Received Your Quote Request!</h2>
          <p>Dear ${name},</p>
          <p>Thank you for your interest. We'll review your requirements and send you a detailed quote within <strong>24–48 hours</strong>.</p>
          <p><strong>What you requested:</strong><br/>
            Product: ${productType || 'Not specified'}<br/>
            Quantity: ${quantity || 'Not specified'}<br/>
            Location: ${location || 'Not specified'}
          </p>
          <hr style="border:none; border-top:1px solid #eee; margin: 20px 0;"/>
          <p>Need it faster? Call us directly:</p>
          <p>📞 <strong>+91 86194 59354</strong> &nbsp;|&nbsp; <strong>+91 90797 75779</strong></p>
          <p>💬 <a href="https://wa.me/918619459354">Chat on WhatsApp</a></p>
          <p style="color:#888; font-size:12px; margin-top:20px;">Kota Stone Factory, Kota, Rajasthan, India</p>
        </div>
      `
    });

    res.json({ success: true, message: "Quote request received! We'll contact you within 24–48 hours." });

  } catch (err) {
    console.error('Quote route error:', err);
    res.status(500).json({ success: false, message: 'Something went wrong. Please try again.' });
  }
});

module.exports = router;
