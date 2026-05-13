# Kota Stone Factory — Backend API

Node.js + Express backend for the Kota Stone Factory website.  
Handles contact forms, newsletter signups, and quote requests.

---

## Features

- **POST /api/contact** — saves enquiry to MongoDB, emails owner + auto-replies to customer
- **POST /api/subscribe** — saves newsletter email (duplicate-safe), sends welcome email
- **POST /api/quote** — saves quote request, emails owner + sends confirmation to customer
- Rate limiting (5 requests / 15 min per IP)
- Input validation and sanitization
- CORS protection

---

## 1. Install Dependencies

```bash
cd backend
npm install
```

---

## 2. Set Up MongoDB Atlas (Free Cloud Database)

1. Go to [https://www.mongodb.com/atlas](https://www.mongodb.com/atlas) and create a free account
2. Click **"Build a Database"** → choose **Free (M0)** → select any region → click **Create**
3. Set a **username and password** (save these!)
4. Under **"Where would you like to connect from?"** choose **"My Local Environment"**
   - Add IP address: `0.0.0.0/0` (allows all IPs — needed for Railway hosting)
   - Click **Add Entry**, then **Finish and Close**
5. Click **"Connect"** on your cluster → **"Drivers"** → copy the connection string
6. It looks like:  
   `mongodb+srv://harshit:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
7. Replace `<password>` with your actual password and add your database name:  
   `mongodb+srv://harshit:mypassword@cluster0.xxxxx.mongodb.net/kotastone?retryWrites=true&w=majority`
8. Paste this as `MONGO_URI` in your `.env` file

---

## 3. Set Up Gmail App Password

Gmail requires an **App Password** (not your regular password) for sending emails from code.

1. Go to your Google Account → [https://myaccount.google.com](https://myaccount.google.com)
2. Click **Security** → make sure **2-Step Verification is ON** (required)
3. Search for **"App passwords"** in the search bar
4. Click **App passwords** → select app: **Mail** → select device: **Other** → type "Kota Stone"
5. Click **Generate** → Google gives you a **16-character password** like `abcd efgh ijkl mnop`
6. Copy it (remove the spaces) and paste as `EMAIL_PASS` in your `.env` file

---

## 4. Create Your .env File

```bash
cp .env.example .env
```

Then open `.env` and fill in all values:

```
MONGO_URI=mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/kotastone?retryWrites=true&w=majority
EMAIL_USER=youremail@gmail.com
EMAIL_PASS=abcdefghijklmnop
OWNER_EMAIL=harshit@kotastonefactory.com
PORT=3000
FRONTEND_URL=https://harshitdhaker-cc.github.io
```

---

## 5. Run Locally

```bash
npm run dev
```

You should see:
```
✅  MongoDB connected
✅  Server running on http://localhost:3000
   POST /api/contact
   POST /api/subscribe
   POST /api/quote
```

Test it with a tool like **Thunder Client** (VS Code extension) or **Postman**:

```
POST http://localhost:3000/api/contact
Content-Type: application/json

{
  "name": "Test User",
  "email": "test@example.com",
  "phone": "+91 98765 43210",
  "enquiry": "Flooring",
  "message": "I need 500 sq ft of polished Kota Stone."
}
```

---

## 6. Update Frontend API URL

In `script.js`, find this line near the top of the contact form section:

```js
const API_BASE = 'http://localhost:3000';
```

After deploying, replace it with your Railway URL:

```js
const API_BASE = 'https://kota-stone-backend.up.railway.app';
```

---

## 7. Deploy on Railway (Free Hosting)

1. Go to [https://railway.app](https://railway.app) and sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repo (`Kota-Stone-Factory`) → Railway will detect Node.js automatically
4. Click your deployment → go to **Variables** tab
5. Add all your `.env` values one by one (MONGO_URI, EMAIL_USER, EMAIL_PASS, etc.)
6. Go to **Settings** → **Networking** → click **"Generate Domain"**
7. Your backend URL will be something like `https://kota-stone-backend.up.railway.app`
8. Copy that URL and update `API_BASE` in `script.js`
9. Push the updated `script.js` to GitHub — your frontend will now use the live backend!

---

## API Reference

### POST /api/contact
| Field | Type | Required |
|-------|------|----------|
| name | string | ✅ |
| email | string | ✅ |
| phone | string | ❌ |
| enquiry | string | ❌ |
| message | string | ✅ |

### POST /api/subscribe
| Field | Type | Required |
|-------|------|----------|
| email | string | ✅ |

### POST /api/quote
| Field | Type | Required |
|-------|------|----------|
| name | string | ✅ |
| email | string | ✅ |
| phone | string | ❌ |
| productType | string | ❌ |
| quantity | string | ❌ |
| location | string | ❌ |
| message | string | ❌ |

All routes return:
```json
{ "success": true, "message": "..." }
{ "success": false, "message": "..." }
```

---

## Project Structure

```
backend/
├── server.js          ← entry point, connects DB, registers routes
├── .env               ← your secrets (never commit this!)
├── .env.example       ← template (safe to commit)
├── package.json
├── models/
│   ├── Contact.js     ← MongoDB schema for contact form
│   ├── Subscriber.js  ← MongoDB schema for newsletter
│   └── Quote.js       ← MongoDB schema for quote requests
├── routes/
│   ├── contact.js     ← POST /api/contact
│   ├── subscribe.js   ← POST /api/subscribe
│   └── quote.js       ← POST /api/quote
└── utils/
    └── sendEmail.js   ← Nodemailer helper
```
