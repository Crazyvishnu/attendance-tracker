# GitHub Actions Workflow Setup

The GitHub Actions workflow file couldn't be automatically created due to nested directory requirements.
Please follow these steps to add it manually:

## Step 1: Create the Workflow File

1. Go to your repository: https://github.com/Crazyvishnu/attendance-tracker
2. Click "Add file" → "Create new file"
3. In the filename box, type: `.github/workflows/attendance.yml`
   (This will automatically create the .github and workflows directories)

## Step 2: Copy This Content

Paste the following content into the file:

```yaml
name: College Attendance Tracker

on:
  schedule:
    # Run at 8:00 AM IST (2:30 AM UTC)
    - cron: '30 2 * * *'
    # Run at 4:00 PM IST (10:30 AM UTC)
    - cron: '30 10 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  track-attendance:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Install Chrome and ChromeDriver
      run: |
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
    
    - name: Run attendance tracker
      env:
        COLLEGE_USERNAME: ${{ secrets.COLLEGE_USERNAME }}
        COLLEGE_PASSWORD: ${{ secrets.COLLEGE_PASSWORD }}
        WHATSAPP_PHONE: ${{ secrets.WHATSAPP_PHONE }}
        TWILIO_ACCOUNT_SID: ${{ secrets.TWILIO_ACCOUNT_SID }}
        TWILIO_AUTH_TOKEN: ${{ secrets.TWILIO_AUTH_TOKEN }}
        TWILIO_WHATSAPP_FROM: ${{ secrets.TWILIO_WHATSAPP_FROM }}
      run: python attendance_tracker.py
    
    - name: Commit attendance data
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/
        git diff --quiet && git diff --staged --quiet || git commit -m "Update attendance data - $(date +'%Y-%m-%d %H:%M:%S')"
        git push
```

## Step 3: Commit the File

1. Scroll down and click "Commit new file"
2. The workflow is now active!

## Next: Configure Secrets

After adding the workflow file, follow the README.md instructions to:
1. Add GitHub Secrets (Settings → Secrets and variables → Actions)
2. Set up Twilio WhatsApp
3. Update scraping selectors in attendance_tracker.py
4. Test manually in Actions tab
