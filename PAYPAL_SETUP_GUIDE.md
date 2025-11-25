# PayPal Setup Guide for Weekly Pot

## 🎯 Quick Overview

You need PayPal **only if using "Weekly Pot" mode**. If playing for fun, skip this entirely!

---

## 📋 Step-by-Step Setup

### Step 1: Get PayPal Business Account (Free)

1. **Visit**: https://www.paypal.com/uk/business
2. **Sign up** for Business account (or upgrade personal to business)
3. **Verify** your email and bank details
4. **Note**: This is FREE - no monthly fees

### Step 2: Create API Credentials

1. **Login** to https://developer.paypal.com
2. **Go to**: Dashboard → My Apps & Credentials
3. **Choose**: 
   - **Sandbox** (for testing with fake money)
   - **Live** (for real money)
4. **Create App**:
   - Click "Create App"
   - Name it "Football Predictions"
   - Select "Merchant" type
5. **Copy credentials**:
   - Client ID (looks like: `AbCdEf123...`)
   - Secret (looks like: `XyZ789...`)

### Step 3: Add to Your App

Edit `/app/backend/.env`:

```env
# For Testing (Sandbox)
PAYPAL_CLIENT_ID="your_sandbox_client_id"
PAYPAL_SECRET="your_sandbox_secret"
PAYPAL_MODE="sandbox"

# For Real Money (Live) - switch when ready
PAYPAL_CLIENT_ID="your_live_client_id"
PAYPAL_SECRET="your_live_secret"
PAYPAL_MODE="live"
```

### Step 4: Restart Backend

```bash
sudo supervisorctl restart backend
```

### Step 5: Test It!

1. Use **sandbox** mode first
2. Create test PayPal accounts at https://developer.paypal.com/dashboard/accounts
3. Make test payments
4. Verify everything works
5. Switch to **live** mode when ready

---

## 💰 How Payments Work

### Weekly Payment Flow

1. **User clicks "Pay Now"** in app
2. **App creates PayPal order** for £2/£3/£5
3. **User redirected** to PayPal
4. **User pays** via PayPal account
5. **User redirected back** to app
6. **Payment confirmed**, user entered in competition

### Payout Flow

1. **Admin declares winner** each Monday
2. **Winner gets paid** via PayPal
3. **10% automatically** deducted for admin
4. **Records kept** in database

---

## 🔒 Security

- ✅ PayPal handles all credit card details
- ✅ You never see card numbers
- ✅ Secure checkout process
- ✅ Buyer and seller protection
- ✅ Credentials stored in `.env` (not in code)

---

## 💡 Alternative: Manual Mode

**Don't want to set up PayPal?**

You can handle payments manually:

1. **Keep app in "manual tracking" mode**
2. **App shows** who paid/who won
3. **You handle** money offline:
   - Bank transfers
   - Cash at pub
   - Venmo/other apps
4. **App just tracks** winners and scores

This works perfectly fine for small friend groups!

---

## 📊 Cost Breakdown

### PayPal Fees (UK)
- **Receiving money**: 2.9% + 20p per transaction
- **Sending money** (to winner): Free if from PayPal balance

### Example (10 players × £5):
```
Total collected: £50
PayPal receiving fees: (£0.145 × 10) + (£0.20 × 10) = £1.45 + £2.00 = £3.45
Net received: £50 - £3.45 = £46.55
Your 10% admin fee: £5 (calculated before PayPal fees)
Winner gets: £41.55

Better approach: Add £0.50 to cover fees
Stake: £5.50 instead of £5
```

**Or** just absorb fees as part of admin costs.

---

## 🎯 Sandbox vs Live

### Sandbox (Testing)
- **Use**: For testing before going live
- **Money**: Fake test money
- **Accounts**: Create test buyer/seller accounts
- **Perfect**: For development and testing

### Live (Real Money)
- **Use**: When ready for real competitions
- **Money**: Real transactions
- **Accounts**: Real PayPal users
- **Switch**: Just change `PAYPAL_MODE="live"`

---

## ❓ Troubleshooting

### "Payment failed"
- Check credentials are correct
- Ensure mode matches (sandbox/live)
- Check PayPal account is verified

### "Insufficient funds"
- User needs money in PayPal
- Or linked card/bank account

### "Integration not working"
- Restart backend after adding credentials
- Check `.env` file has correct format
- View logs: `tail -f /var/log/supervisor/backend.err.log`

---

## 🎁 Pro Tips

1. **Start with Sandbox**: Test everything first
2. **Clear Communication**: Tell team about PayPal requirement
3. **Payment Deadline**: Set clear weekly deadline
4. **Backup Plan**: Have manual payment option
5. **Fee Transparency**: Be upfront about all fees

---

## 📞 PayPal Support

**Issues with PayPal itself?**
- UK Support: 0800 358 7911
- Help Center: https://www.paypal.com/uk/smarthelp/home
- Developer Docs: https://developer.paypal.com/docs/

---

## 🚀 You're Ready!

Once set up:
- ✅ Secure payments
- ✅ Automatic tracking
- ✅ Easy payouts
- ✅ Professional setup
- ✅ Happy team members!

**No PayPal? No problem!** Use manual mode and handle money your way.
