# HadFun Football Prediction App - Deployment Guide

## 🚀 Step 1: Deploy to Production

1. **Click the "Deploy" button** in the top-right corner of your Emergent chat interface
2. Click **"Deploy Now"** to publish your application
3. Wait **~10 minutes** for deployment to complete
4. You'll receive a public URL where your app is live
5. **Cost**: 50 credits/month per deployed app

## 🌐 Step 2: Link Custom Domain (hadfun.co.uk)

### In Emergent Platform:
1. Go to your **Deployments** section
2. Find **Custom Domain** section
3. Click **"Link Domain"**
4. Enter: `hadfun.co.uk`
5. Click **"Next"** - you'll receive DNS configuration details

### In Your Domain Registrar (GoDaddy/Namecheap/etc):
1. Log into your domain provider
2. Go to **DNS Management**
3. **Important**: Delete or remove the old A record pointing to your previous deployment
4. Add new **A Record**:
   - **Type**: A
   - **Host**: @ (for root) or www
   - **Value**: [IP address provided by Emergent]
   - **TTL**: 300 seconds

### Back in Emergent:
1. Click **"Check Status"**
2. Wait 5-15 minutes for verification
3. DNS propagation may take up to 24 hours globally

## 🔄 Step 3: Set Up Automated Fixture Updates

Since Emergent doesn't support cron jobs, use one of these options:

### Option A: GitHub Actions (Recommended)

Create a `.github/workflows/update-fixtures.yml` file in your GitHub repo:

```yaml
name: Update Fixtures Daily

on:
  schedule:
    - cron: '0 6 * * *'  # Run at 6 AM UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Update Fixtures
        run: |
          curl -X POST https://hadfun.co.uk/api/admin/refresh-fixtures
```

### Option B: Cron-Job.org (Free Service)

1. Go to https://cron-job.org
2. Create a free account
3. Create new cron job:
   - **URL**: `https://hadfun.co.uk/api/admin/refresh-fixtures`
   - **Schedule**: Daily at 6:00 AM
   - **Method**: POST

### Option C: Zapier / IFTTT

1. Create a scheduled automation
2. Set it to call your API endpoint daily
3. URL: `https://hadfun.co.uk/api/admin/refresh-fixtures`

## ✅ Post-Deployment Checklist

### Test These:
- [ ] App loads at hadfun.co.uk
- [ ] All 13 leagues showing
- [ ] Login/signup working
- [ ] Make a prediction
- [ ] View leaderboard
- [ ] Check scores displaying correctly
- [ ] Test on mobile device
- [ ] Verify custom domain SSL certificate is active

### Monitor:
- [ ] Check fixture updates are running daily
- [ ] Monitor API-Football usage (should stay under 100/day)
- [ ] Watch for any error logs

## 🔧 Manual Fixture Update

If you need to manually update fixtures, you can:

1. **Via API** (use Postman or curl):
```bash
curl -X POST https://hadfun.co.uk/api/admin/refresh-fixtures
```

2. **Or SSH into server** (if available):
```bash
cd /app/backend
python3 update_fixtures_endpoint.py
```

## 📊 API Usage

- **Initial full import**: ~13 API calls (one per league)
- **Daily updates**: ~13-20 API calls (only updates last 7 days)
- **Free tier limit**: 100 calls/day
- **Current usage**: Well within limits ✅

## 🆘 Troubleshooting

### Domain not working?
- Wait 24 hours for DNS propagation
- Check you removed old A records
- Verify A record points to correct IP

### Fixtures not updating?
- Test endpoint manually: `curl -X POST https://hadfun.co.uk/api/admin/refresh-fixtures`
- Check API-Football key is still valid
- Verify cron job is running

### App not loading?
- Check deployment status in Emergent
- Verify backend is running
- Check MongoDB connection

## 📞 Support

If you encounter issues:
1. Check Emergent platform logs
2. Test in Preview mode first
3. Contact Emergent support if needed

---

**Your app is production-ready!** 🎉

Once deployed:
- Users can access it 24/7 at hadfun.co.uk
- Fixtures update automatically daily
- Scale to handle thousands of users
- Focus on building the social features next!
