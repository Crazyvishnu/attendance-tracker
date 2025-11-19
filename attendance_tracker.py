#!/usr/bin/env python3
"""
College Attendance Tracker
Scrapes attendance from college website and sends WhatsApp notifications
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from twilio.rest import Client

# Configuration
COLLEGE_URL = "https://mgit.winnou.net/index.php"
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "attendance_log.json"

def setup_driver():
    """Setup headless Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_college_portal(driver, username, password):
    """Login to college website"""
    print(f"[{datetime.now()}] Navigating to college portal...")
    driver.get(COLLEGE_URL)
    
    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # TODO: YOU NEED TO INSPECT YOUR COLLEGE WEBSITE AND UPDATE THESE SELECTORS
        # These are placeholder selectors - replace with actual ones from your site
        print(f"[{datetime.now()}] Looking for login form...")
        
        # Example selectors (REPLACE THESE):
        username_field = driver.find_element(By.ID, "username")  # Update selector
        password_field = driver.find_element(By.ID, "password")  # Update selector
        login_button = driver.find_element(By.ID, "login")  # Update selector
        
        # Enter credentials
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
        print(f"[{datetime.now()}] Login submitted, waiting for dashboard...")
        time.sleep(3)  # Wait for redirect
        
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] Login failed: {e}")
        return False

def scrape_attendance(driver):
    """Scrape attendance data from the portal"""
    try:
        print(f"[{datetime.now()}] Scraping attendance data...")
        
        # TODO: YOU NEED TO INSPECT YOUR COLLEGE WEBSITE AND UPDATE THESE SELECTORS
        # Navigate to attendance page if needed
        # driver.find_element(By.LINK_TEXT, "Attendance").click()  # Update as needed
        
        time.sleep(2)  # Wait for page to load
        
        # Example: Scrape attendance percentage
        # REPLACE THIS WITH YOUR ACTUAL SELECTORS
        attendance_data = {}
        
        # Option 1: If attendance is in a table
        # table = driver.find_element(By.CLASS_NAME, "attendance-table")
        # rows = table.find_elements(By.TAG_NAME, "tr")
        # for row in rows[1:]:  # Skip header
        #     cols = row.find_elements(By.TAG_NAME, "td")
        #     subject = cols[0].text
        #     percentage = cols[1].text
        #     attendance_data[subject] = percentage
        
        # Option 2: If attendance is in specific elements
        # subjects = driver.find_elements(By.CLASS_NAME, "subject-name")
        # percentages = driver.find_elements(By.CLASS_NAME, "attendance-percentage")
        # for subject, percentage in zip(subjects, percentages):
        #     attendance_data[subject.text] = percentage.text
        
        # Placeholder - YOU NEED TO REPLACE THIS
        attendance_data = {
            "overall_percentage": "85%",  # Replace with actual scraping
            "subjects": {
                "Math": "90%",
                "Physics": "85%",
                "Chemistry": "80%"
            }
        }
        
        print(f"[{datetime.now()}] Attendance scraped: {attendance_data}")
        return attendance_data
        
    except Exception as e:
        print(f"[{datetime.now()}] Error scraping attendance: {e}")
        return None

def send_whatsapp_message(attendance_data):
    """Send WhatsApp notification using Twilio"""
    try:
        # Get credentials from environment
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_whatsapp = os.environ.get("TWILIO_WHATSAPP_FROM")  # e.g., "whatsapp:+14155238886"
        to_whatsapp = f"whatsapp:{os.environ.get('WHATSAPP_PHONE')}"  # e.g., "whatsapp:+919440911008"
        
        if not all([account_sid, auth_token, from_whatsapp]):
            print(f"[{datetime.now()}] Missing Twilio credentials, skipping WhatsApp")
            return False
        
        client = Client(account_sid, auth_token)
        
        # Format message
        message_text = f"""🎓 *Attendance Update*
📅 {datetime.now().strftime('%d %B %Y, %I:%M %p')}

📊 Overall: {attendance_data.get('overall_percentage', 'N/A')}

📚 Subject-wise:
"""
        
        for subject, percentage in attendance_data.get('subjects', {}).items():
            message_text += f"  • {subject}: {percentage}\n"
        
        message_text += "\n✅ Updated in GitHub repo"
        
        # Send message
        message = client.messages.create(
            from_=from_whatsapp,
            body=message_text,
            to=to_whatsapp
        )
        
        print(f"[{datetime.now()}] WhatsApp sent: {message.sid}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] Error sending WhatsApp: {e}")
        return False

def save_attendance_data(attendance_data):
    """Save attendance data to JSON file"""
    try:
        # Create data directory if it doesn't exist
        DATA_DIR.mkdir(exist_ok=True)
        
        # Load existing data
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = []
        
        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "attendance": attendance_data
        }
        all_data.append(entry)
        
        # Save back to file
        with open(DATA_FILE, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"[{datetime.now()}] Data saved to {DATA_FILE}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] Error saving data: {e}")
        return False

def main():
    """Main execution function"""
    print(f"\n{'='*60}")
    print(f"College Attendance Tracker Started")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    driver = None
    
    try:
        # Get credentials
        username = os.environ.get("COLLEGE_USERNAME")
        password = os.environ.get("COLLEGE_PASSWORD")
        
        if not username or not password:
            print("ERROR: College credentials not found in environment variables")
            return
        
        # Setup browser
        driver = setup_driver()
        
        # Login
        if not login_to_college_portal(driver, username, password):
            print("ERROR: Login failed")
            return
        
        # Scrape attendance
        attendance_data = scrape_attendance(driver)
        
        if not attendance_data:
            print("ERROR: Failed to scrape attendance")
            return
        
        # Save data
        save_attendance_data(attendance_data)
        
        # Send WhatsApp notification
        send_whatsapp_message(attendance_data)
        
        print(f"\n{'='*60}")
        print(f"Attendance Tracker Completed Successfully!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"ERROR in main execution: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print(f"[{datetime.now()}] Browser closed")

if __name__ == "__main__":
    main()
