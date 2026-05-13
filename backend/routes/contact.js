const express = require('express');
const router  = express.Router();
const { body, validationResult } = require('express-validator');
const { rateLimit } = require('express-rate-limit');

const Contact   = require('../models/Contact');
const sendEmail = require('../utils/sendEmail');

// Rate limit: max 5 requests per 15 minutes per IP
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { success: false, message: 'Too many requests. Please try again after 15 minutes.' }
});

// Validation rules
const validateContact = [
  body('name').trim().notEmpty().withMessage('Name is required').escape(),
  body('email').isEmail().withMessage('Valid email is required').normalizeEmail(),
  body('message').trim().notEmpty().withMessage('Message is required').escape(),
  body('phone').optional().trim().escape(),
  body('enquiry').optional().trim().escape()
];

router.post('/', limiter, validateContact, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, errors: errors.array() });
  }

  const { name, email, phone, enquiry, message } = req.body;

  try {
    // Save to MongoDB
    await Contact.create({ name, email, phone, enquiryType: enquiry, message });

    // Email to business owner
    await sendEmail({
      to: process.env.OWNER_EMAIL,
      subject: `New Enquiry from ${name} — Kota Stone Factory`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #8B4513;">New Contact Enquiry</h2>
          <table style="width:100%; border-collapse: collapse;">
            <tr><td style="padding:8px; font-weight:bold; color:#555;">Name</td><td style="padding:8px;">${name}</td></tr>
            <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold; color:#555;">Email</td><td style="padding:8px;"><a href="mailto:${email}">${email}</a></td></tr>
            <tr><td style="padding:8px; font-weight:bold; color:#555;">Phone</td><td style="padding:8px;">${phone || 'Not provided'}</td></tr>
            <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold; color:#555;">Enquiry Type</td><td style="padding:8px;">${enquiry || 'General Enquiry'}</td></tr>
            <tr><td style="padding:8px; font-weight:bold; color:#555;">Message</td><td style="padding:8px;">${message}</td></tr>
          </table>
          <p style="color:#888; font-size:12px; margin-top:20px;">Received at ${new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST</p>
        </div>
      `
    });

    // Thank-you auto-reply to customer
    await sendEmail({
      to: email,
      subject: 'Thank you for contacting Kota Stone Factory',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #8B4513;">Thank You, ${name}!</h2>
          <p>We've received your enquiry and will get back to you within <strong>24 hours</strong>.</p>
          <p><strong>Your message:</strong><br/>${message}</p>
          <hr style="border:none; border-top:1px solid #eee; margin: 20px 0;"/>
          <p>For urgent queries, call us directly:</p>
          <p>📞 <strong>+91 86194 59354</strong> &nbsp;|&nbsp; <strong>+91 90797 75779</strong></p>
          <p>💬 <a href="https://wa.me/918619459354">Chat on WhatsApp</a></p>
          <p style="color:#888; font-size:12px; margin-top:20px;">Kota Stone Factory, Kota, Rajasthan, India</p>
        </div>
      `
    });

    res.json({ success: true, message: "Thank you! We'll get back to you within 24 hours." });

  } catch (err) {
    console.error('Contact route error:', err);
    res.status(500).json({ success: false, message: 'Something went wrong. Please try again.' });
  }
});

module.exports = router;
