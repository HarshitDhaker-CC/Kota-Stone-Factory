require('dotenv').config();
const express   = require('express');
const mongoose  = require('mongoose');
const cors      = require('cors');

const app = express();

// ── CORS ────────────────────────────────────────────────────────────────────
const allowedOrigins = [
  process.env.FRONTEND_URL,
  'http://127.0.0.1:5500',   // Live Server (VS Code)
  'http://localhost:5500',
  'http://localhost:3000'
].filter(Boolean);

app.use(cors({
  origin: function (origin, callback) {
    // Allow requests with no origin (mobile apps, curl, Postman)
    if (!origin) return callback(null, true);
    if (allowedOrigins.includes(origin)) return callback(null, true);
    callback(new Error(`CORS policy: origin ${origin} not allowed`));
  },
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));

// ── BODY PARSER ──────────────────────────────────────────────────────────────
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ── ROUTES ───────────────────────────────────────────────────────────────────
app.use('/api/contact',   require('./routes/contact'));
app.use('/api/subscribe', require('./routes/subscribe'));
app.use('/api/quote',     require('./routes/quote'));

// ── HEALTH CHECK ─────────────────────────────────────────────────────────────
app.get('/', (req, res) => {
  res.json({ status: 'OK', message: 'Kota Stone Factory API is running' });
});

// ── 404 HANDLER ──────────────────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ success: false, message: 'Route not found' });
});

// ── GLOBAL ERROR HANDLER ─────────────────────────────────────────────────────
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err.message);
  res.status(500).json({ success: false, message: 'Internal server error' });
});

// ── MONGODB + SERVER START ────────────────────────────────────────────────────
const PORT     = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI;

if (!MONGO_URI) {
  console.error('❌  MONGO_URI is missing. Copy .env.example to .env and fill in your values.');
  process.exit(1);
}

mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log('✅  MongoDB connected');
    app.listen(PORT, () => {
      console.log(`✅  Server running on http://localhost:${PORT}`);
      console.log(`   POST /api/contact`);
      console.log(`   POST /api/subscribe`);
      console.log(`   POST /api/quote`);
    });
  })
  .catch(err => {
    console.error('❌  MongoDB connection failed:', err.message);
    process.exit(1);
  });
