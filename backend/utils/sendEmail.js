const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: 'smtpout.secureserver.net',
  port: 465,
  secure: true,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

async function sendEmail({ to, subject, html }) {
  const mailOptions = {
    from: `"Kota Stone Factory" <${process.env.EMAIL_USER}>`,
    to,
    subject,
    html
  };
  await transporter.sendMail(mailOptions);
}

module.exports = sendEmail;