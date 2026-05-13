const mongoose = require('mongoose');

const quoteSchema = new mongoose.Schema({
  name:        { type: String, required: true, trim: true },
  email:       { type: String, required: true, trim: true, lowercase: true },
  phone:       { type: String, trim: true, default: '' },
  productType: { type: String, trim: true, default: '' },
  quantity:    { type: String, trim: true, default: '' },
  location:    { type: String, trim: true, default: '' },
  message:     { type: String, trim: true, default: '' },
  createdAt:   { type: Date, default: Date.now }
});

module.exports = mongoose.model('Quote', quoteSchema);