# Quick Fix Required

## Issue: GitHub Actions Permission Error (403)

The workflow needs write permissions to commit attendance data.

## Fix (30 seconds):

### Option 1: Enable in Repository Settings (Recommended)

1. Go to: [Settings → Actions → General](https://github.com/Crazyvishnu/attendance-tracker/settings/actions)
2. Scroll down to **"Workflow permissions"**
3. Select **"Read and write permissions"**
4. Click **"Save"**

### Option 2: Update Workflow File

1. Edit: [.github/workflows/attendance.yml](https://github.com/Crazyvishnu/attendance-tracker/edit/main/.github/workflows/attendance.yml)
2. Add these lines after `on:` section (around line 9):

```yaml
# Add this section
permissions:
  contents: write
```

So it looks like:
```yaml
name: College Attendance Tracker

on:
  schedule:
    - cron: '30 2 * * *'
    - cron: '30 10 * * *'
  workflow_dispatch:

permissions:
  contents: write  # <-- ADD THIS

jobs:
  track-attendance:
    ...
```

3. Commit changes

---

## ✅ After Fixing:

Run the workflow again from [Actions Tab](https://github.com/Crazyvishnu/attendance-tracker/actions)

The script is now fixed and will:
- ✅ Use correct Chrome driver for GitHub Actions
- ✅ Auto-detect login form elements
- ✅ Save screenshots for debugging
- ✅ Save HTML source for analysis
- ✅ Send WhatsApp notifications
- ✅ Commit data to repository
