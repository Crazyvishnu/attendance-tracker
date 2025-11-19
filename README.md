# College Attendance Tracker

Automated attendance tracking system that:
- Scrapes attendance from college portal (https://mgit.winnou.net/index.php)
- Sends WhatsApp notifications
- Stores historical data in GitHub
- Runs automatically at 8 AM and 4 PM IST

## Setup Instructions

### 1. Set Up GitHub Secrets

Go to repository **Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:
- `COLLEGE_USERNAME`: Your college portal username
- `COLLEGE_PASSWORD`: Your college portal password
- `WHATSAPP_PHONE`: Your WhatsApp number (e.g., +919440911008)
- `TWILIO_ACCOUNT_SID`: Get from https://www.twilio.com/console
- `TWILIO_AUTH_TOKEN`: Get from https://www.twilio.com/console
- `TWILIO_WHATSAPP_FROM`: Twilio WhatsApp number (e.g., whatsapp:+14155238886)

### 2. Configure Twilio WhatsApp

1. Sign up at https://www.twilio.com/
2. Get a Twilio phone number with WhatsApp enabled
3. Follow Twilio's WhatsApp sandbox setup: https://www.twilio.com/docs/whatsapp/sandbox
4. Send the join code from your WhatsApp to activate

### 3. Update Scraping Selectors ⚠️ IMPORTANT

You MUST update the web scraping selectors in `attendance_tracker.py`:

1. Open your college website in Chrome
2. Right-click → Inspect Element
3. Find the HTML elements for:
   - Username field (currently using ID: "username")
   - Password field (currently using ID: "password")
   - Login button (currently using ID: "login")
   - Attendance data (tables/divs showing percentages)
4. Update the selectors in `attendance_tracker.py` (lines marked with `# TODO`)

**Critical sections to update:**
- Lines 45-48: Login form selectors
- Lines 68-85: Attendance data extraction

### 4. Test Manually

Trigger the workflow manually:
1. Go to **Actions** tab
2. Select "College Attendance Tracker"
3. Click "Run workflow"
4. Check logs for any errors

### 5. Verify Schedule

The workflow runs automatically:
- **8:00 AM IST** (2:30 AM UTC)
- **4:00 PM IST** (10:30 AM UTC)

## Project Structure

```
attendance-tracker/
├── .github/
│   └── workflows/
│       └── attendance.yml          # GitHub Actions workflow
├── data/
│   └── attendance_log.json         # Historical attendance data
├── attendance_tracker.py           # Main Python script
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Data Format

Attendance data is stored in `data/attendance_log.json`:

```json
[
  {
    "timestamp": "2024-01-15T08:00:00",
    "attendance": {
      "overall_percentage": "85%",
      "subjects": {
        "Math": "90%",
        "Physics": "85%"
      }
    }
  }
]
```

## Troubleshooting

### Workflow fails with login error
- Check GitHub Secrets are set correctly
- Verify credentials work on college website
- Update login selectors in code

### No WhatsApp message received
- Verify Twilio credentials
- Check you've joined Twilio WhatsApp sandbox
- Check workflow logs for errors

### Scraping returns empty data
- Update selectors to match your college portal
- Use browser inspector to find correct elements
- Add print statements for debugging

## Next Steps

1. ✅ Repository created
2. ✅ Files added
3. ⚠️ **Set up GitHub Secrets** (required!)
4. ⚠️ **Set up Twilio WhatsApp** (required!)
5. ⚠️ **Update web scraping selectors** (critical!)
6. ✅ Test manually in Actions tab

## License

MIT
