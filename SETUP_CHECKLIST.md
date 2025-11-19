# 📝 Setup Checklist - MGIT Attendance Tracker

## ✅ Repository Created

✓ Your repo is ready: https://github.com/Crazyvishnu/attendance-tracker

---

## 🔧 3 Quick Steps to Complete

### Step 1: Enable Workflow Permissions (30 seconds)

**Go to**: [Actions Settings](https://github.com/Crazyvishnu/attendance-tracker/settings/actions)

1. Scroll to **"Workflow permissions"**
2. Select **"Read and write permissions"**
3. Click **"Save"**

❌ **Current Status**: Not enabled (causes 403 error)
✅ **After This**: Workflow can commit attendance data

---

### Step 2: Add GitHub Secrets (3 minutes)

**Go to**: [Secrets Settings](https://github.com/Crazyvishnu/attendance-tracker/settings/secrets/actions)

Click **"New repository secret"** and add these 6 secrets:

| Secret Name | What to Enter |
|------------|---------------|
| `COLLEGE_USERNAME` | Your college login username |
| `COLLEGE_PASSWORD` | Your college login password |
| `WHATSAPP_PHONE` | Your WhatsApp number with country code |
| `TWILIO_ACCOUNT_SID` | From Twilio console |
| `TWILIO_AUTH_TOKEN` | From Twilio console |
| `TWILIO_WHATSAPP_FROM` | Format: `whatsapp:+14155238886` |

**Important**: The secret **names** must be EXACTLY as shown (copy-paste them)

❌ **Current Status**: Secrets not added (script can't login)
✅ **After This**: Script can login and scrape attendance

---

### Step 3: Join Twilio WhatsApp Sandbox (2 minutes)

**Go to**: [Twilio Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)

1. Find the join code (looks like: `join happy-dog`)
2. Send that message from your WhatsApp to Twilio's number
3. Wait for confirmation

❌ **Current Status**: Not joined (WhatsApp won't work)
✅ **After This**: You'll receive WhatsApp notifications

---

## 🧪 Test It!

After completing all 3 steps above:

**Link**: [Run Workflow](https://github.com/Crazyvishnu/attendance-tracker/actions/workflows/attendance.yml)

1. Click "Run workflow" button
2. Wait 1-2 minutes
3. Check the results!

---

## 📊 What You'll Get

The workflow will:
1. Login to mgit.winnou.net
2. Click "Student Info"
3. Find your attendance (74.5%)
4. Save to `data/attendance_log.json`
5. Send WhatsApp notification
6. Run automatically at 8 AM & 4 PM daily

---

## 📂 Your Attendance Data

All saved in your repository:
- **[attendance_log.json](https://github.com/Crazyvishnu/attendance-tracker/blob/main/data/attendance_log.json)** - History with timestamps
- **[screenshots/](https://github.com/Crazyvishnu/attendance-tracker/tree/main/data/screenshots)** - Visual proof
- **Commits** - Every update is tracked

---

## ✅ Quick Verification

Before running, verify:
- [ ] Step 1 done: Write permissions enabled
- [ ] Step 2 done: 6 secrets added
- [ ] Step 3 done: Twilio sandbox joined

Then run the workflow!

---

## 🐛 Common Issues

**"Credentials not found"**
→ Add GitHub Secrets (Step 2)

**"Permission denied (403)"**
→ Enable write permissions (Step 1)

**"WhatsApp error"**
→ Join Twilio sandbox (Step 3)

**"Can't find attendance"**
→ Check screenshots and HTML files in data/ folder
→ Script saves everything for you to review

---

Good luck! The hard part (code) is done. Just complete these 3 setup steps! 🚀
