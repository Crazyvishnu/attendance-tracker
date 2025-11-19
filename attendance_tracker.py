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
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
COLLEGE_URL = "https://mgit.winnou.net/index.php"
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "attendance_log.json"
SCREENSHOT_DIR = DATA_DIR / "screenshots"

def setup_driver():
    """Setup headless Chrome driver for GitHub Actions"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # For GitHub Actions, use chromium-chromedriver
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    # Service pointing to chromedriver
    service = Service("/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def try_find_element(driver, selectors_list, element_name):
    """Try multiple selectors to find an element"""
    for selector_type, selector_value in selectors_list:
        try:
            if selector_type == "id":
                element = driver.find_element(By.ID, selector_value)
            elif selector_type == "name":
                element = driver.find_element(By.NAME, selector_value)
            elif selector_type == "class":
                element = driver.find_element(By.CLASS_NAME, selector_value)
            elif selector_type == "xpath":
                element = driver.find_element(By.XPATH, selector_value)
            elif selector_type == "css":
                element = driver.find_element(By.CSS_SELECTOR, selector_value)
            
            print(f"  ✓ Found {element_name} using {selector_type}: {selector_value}")
            return element
        except NoSuchElementException:
            continue
    
    print(f"  ✗ Could not find {element_name} with any selector")
    return None

def login_to_college_portal(driver, username, password):
    """Login to college website with multiple selector attempts"""
    print(f"[{datetime.now()}] Navigating to college portal...")
    driver.get(COLLEGE_URL)
    
    try:
        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Save screenshot for debugging
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        screenshot_path = SCREENSHOT_DIR / f"login_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"  📸 Screenshot saved: {screenshot_path}")
        
        time.sleep(3)  # Wait for any JavaScript to load
        
        print(f"[{datetime.now()}] Looking for login form elements...")
        
        # Try multiple common selectors for username field
        username_selectors = [
            ("name", "username"),
            ("id", "username"),
            ("id", "user"),
            ("name", "user"),
            ("name", "login"),
            ("id", "email"),
            ("name", "email"),
            ("name", "userid"),
            ("id", "userid"),
            ("xpath", "//input[@type='text'][1]"),
            ("xpath", "//input[@type='email']"),
            ("css", "input[placeholder*='username' i]"),
            ("css", "input[placeholder*='user' i]"),
        ]
        
        # Try multiple common selectors for password field
        password_selectors = [
            ("name", "password"),
            ("id", "password"),
            ("name", "passwd"),
            ("id", "passwd"),
            ("name", "pwd"),
            ("id", "pwd"),
            ("xpath", "//input[@type='password']"),
            ("css", "input[type='password']"),
        ]
        
        # Try multiple common selectors for login button
        button_selectors = [
            ("id", "login"),
            ("id", "submit"),
            ("name", "login"),
            ("name", "submit"),
            ("name", "Submit"),
            ("xpath", "//button[@type='submit']"),
            ("xpath", "//input[@type='submit']"),
            ("xpath", "//button[contains(text(), 'Sign in')]"),
            ("xpath", "//button[contains(text(), 'Login')]"),
            ("xpath", "//input[@value='Login']"),
            ("xpath", "//input[@value='Sign in']"),
            ("xpath", "//button[contains(@class, 'login')]"),
            ("xpath", "//button[contains(@class, 'submit')]"),
            ("css", "button[type='submit']"),
            ("css", "input[type='submit']"),
        ]
        
        # Find username field
        username_field = try_find_element(driver, username_selectors, "username field")
        if not username_field:
            print("❌ ERROR: Could not find username field")
            return False
        
        # Find password field
        password_field = try_find_element(driver, password_selectors, "password field")
        if not password_field:
            print("❌ ERROR: Could not find password field")
            return False
        
        # Find login button
        login_button = try_find_element(driver, button_selectors, "login button")
        if not login_button:
            print("❌ ERROR: Could not find login button")
            return False
        
        # Enter credentials
        print(f"[{datetime.now()}] Entering credentials...")
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Take screenshot before clicking login
        screenshot_path = SCREENSHOT_DIR / f"before_login_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"  📸 Screenshot saved: {screenshot_path}")
        
        login_button.click()
        
        print(f"[{datetime.now()}] Login submitted, waiting for dashboard...")
        time.sleep(5)  # Wait for redirect
        
        # Take screenshot after login
        screenshot_path = SCREENSHOT_DIR / f"after_login_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"  📸 Screenshot saved: {screenshot_path}")
        
        print(f"  ✓ Login completed")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] Login failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def scrape_attendance(driver):
    """Scrape attendance data from the portal"""
    try:
        print(f"[{datetime.now()}] Scraping attendance data...")
        
        # Save current page screenshot
        screenshot_path = SCREENSHOT_DIR / f"attendance_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"  📸 Screenshot saved: {screenshot_path}")
        
        # Get page source for analysis
        page_source = driver.page_source
        print(f"  📄 Page source length: {len(page_source)} characters")
        
        # Save page source to file for debugging
        html_file = DATA_DIR / f"page_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"  💾 Page source saved: {html_file}")
        
        # Get current URL to understand where we are
        current_url = driver.current_url
        print(f"  🌐 Current URL: {current_url}")
        
        # Try to find attendance data using multiple patterns
        attendance_data = {
            "url_after_login": current_url,
            "timestamp": datetime.now().isoformat()
        }
        
        # Pattern 1: Look for ALL percentages in text
        import re
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', page_source)
        if percentages:
            print(f"  Found {len(percentages)} percentages: {percentages}")
            attendance_data["all_percentages_found"] = percentages
            
            # Instead of guessing, save all for user to review
            print(f"  ⚠️ Multiple percentages found - check HTML to identify correct one")
        
        # Pattern 2: Look for text containing "attendance"
        attendance_text = re.findall(r'attendance[^<]{0,100}(\d+(?:\.\d+)?)\s*%', page_source, re.IGNORECASE)
        if attendance_text:
            print(f"  Found attendance-related percentages: {attendance_text}")
            attendance_data["attendance_percentages"] = attendance_text
        
        # Pattern 3: Try to find tables and extract ALL data
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"  Found {len(tables)} tables on page")
            
            all_table_data = []
            for i, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"    Table {i+1}: {len(rows)} rows")
                
                table_content = []
                for row_idx, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        cells = row.find_elements(By.TAG_NAME, "th")
                    
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        if any(row_data):  # Only add non-empty rows
                            table_content.append(row_data)
                            print(f"      Row {row_idx}: {row_data}")
                
                if table_content:
                    all_table_data.append({
                        "table_index": i + 1,
                        "rows": table_content
                    })
            
            if all_table_data:
                attendance_data["tables"] = all_table_data
                
        except Exception as e:
            print(f"  Could not analyze tables: {e}")
        
        print(f"[{datetime.now()}] ✓ Page data captured")
        print(f"  📁 Check data/page_source_*.html to see the full page")
        print(f"  📸 Check data/screenshots/ to see visual representation")
        
        return attendance_data
        
    except Exception as e:
        print(f"[{datetime.now()}] Error scraping attendance: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_whatsapp_message(attendance_data):
    """Send WhatsApp notification using Twilio (optional)"""
    try:
        # Get credentials from environment
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_whatsapp = os.environ.get("TWILIO_WHATSAPP_FROM")
        to_whatsapp_number = os.environ.get("WHATSAPP_PHONE")
        
        if not all([account_sid, auth_token, from_whatsapp, to_whatsapp_number]):
            print(f"[{datetime.now()}] ⚠️ Twilio credentials not configured, skipping WhatsApp")
            return False
        
        # Import Twilio (optional dependency)
        try:
            from twilio.rest import Client
        except ImportError:
            print(f"[{datetime.now()}] ⚠️ Twilio not installed, skipping WhatsApp")
            return False
        
        to_whatsapp = f"whatsapp:{to_whatsapp_number}"
        
        client = Client(account_sid, auth_token)
        
        # Format message with all data for review
        message_text = f"""🎓 Attendance Tracker Update
📅 {datetime.now().strftime('%d %B %Y, %I:%M %p')}

✅ Tracker is running!

📄 Data captured from college portal.
Check your GitHub repo for:
• All percentages found: {attendance_data.get('all_percentages_found', [][:5])}
• Screenshots in data/screenshots/
• HTML in data/ folder

🔗 github.com/Crazyvishnu/attendance-tracker
"""
        
        # Send message
        message = client.messages.create(
            from_=from_whatsapp,
            body=message_text,
            to=to_whatsapp
        )
        
        print(f"[{datetime.now()}] ✓ WhatsApp sent: {message.sid}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] ⚠️ WhatsApp failed (non-critical): {e}")
        print(f"  Continuing without WhatsApp notification...")
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
            "data_captured": attendance_data
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
            print("❌ ERROR: College credentials not found in environment variables")
            print("   Make sure COLLEGE_USERNAME and COLLEGE_PASSWORD are set in GitHub Secrets")
            return
        
        print(f"✓ Credentials loaded (Username: {username[:3]}***)")
        
        # Setup browser
        print(f"[{datetime.now()}] Setting up Chrome browser...")
        driver = setup_driver()
        print(f"  ✓ Chrome driver initialized")
        
        # Login
        if not login_to_college_portal(driver, username, password):
            print("❌ ERROR: Login failed")
            print("   Check the screenshots in data/screenshots/ to see what happened")
            return
        
        print(f"  ✓ Login successful")
        
        # Scrape attendance
        attendance_data = scrape_attendance(driver)
        
        if not attendance_data:
            print("❌ ERROR: Failed to scrape attendance")
            return
        
        print(f"  ✓ Attendance data retrieved")
        
        # Save data (this is the main goal)
        save_attendance_data(attendance_data)
        print(f"  ✓ Data saved to repository")
        
        # Try to send WhatsApp notification (optional)
        whatsapp_sent = send_whatsapp_message(attendance_data)
        if whatsapp_sent:
            print(f"  ✓ WhatsApp notification sent")
        else:
            print(f"  ⚠️ WhatsApp skipped (check Twilio setup if needed)")
        
        print(f"\n{'='*60}")
        print(f"✅ Attendance Tracker Completed Successfully!")
        print(f"{'='*60}\n")
        print(f"\n📊 ATTENDANCE DATA SUMMARY:")
        print(f"  - All percentages found: {attendance_data.get('all_percentages_found', [])}")
        print(f"  - Tables captured: {len(attendance_data.get('tables', []))}")
        print(f"  - Full data saved to: {DATA_FILE}")
        print(f"  - Screenshots saved to: {SCREENSHOT_DIR}")
        print(f"\n🔍 TO FIND YOUR CORRECT ATTENDANCE:")
        print(f"  1. Check the screenshots in data/screenshots/")
        print(f"  2. Check the HTML file in data/")
        print(f"  3. Look at data/attendance_log.json for all captured data")
        print(f"  4. Identify which percentage is your actual attendance")
        print(f"  5. Update the script to extract that specific value")
        
    except Exception as e:
        print(f"\n❌ ERROR in main execution: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to save screenshot even on error
        if driver:
            try:
                SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                error_screenshot = SCREENSHOT_DIR / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(str(error_screenshot))
                print(f"\n📸 Error screenshot saved: {error_screenshot}")
            except:
                pass
        
    finally:
        if driver:
            driver.quit()
            print(f"[{datetime.now()}] Browser closed")

if __name__ == "__main__":
    main()
