#!/usr/bin/env python3
"""
College Attendance Tracker
Scrapes attendance from MGIT college website and sends WhatsApp notifications
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
    """Login to college website"""
    print(f"[{datetime.now()}] Navigating to college portal...")
    driver.get(COLLEGE_URL)
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        screenshot_path = SCREENSHOT_DIR / f"01_login_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"  📸 Screenshot: {screenshot_path}")
        
        time.sleep(3)
        
        print(f"[{datetime.now()}] Looking for login form...")
        
        username_selectors = [
            ("name", "username"), ("id", "username"), ("name", "user"),
            ("xpath", "//input[@type='text'][1]"),
        ]
        
        password_selectors = [
            ("name", "passwd"), ("name", "password"), ("id", "password"),
            ("xpath", "//input[@type='password']"),
        ]
        
        button_selectors = [
            ("name", "login"), ("id", "login"), ("xpath", "//input[@type='submit']"),
            ("xpath", "//button[@type='submit']"),
        ]
        
        username_field = try_find_element(driver, username_selectors, "username field")
        if not username_field:
            return False
        
        password_field = try_find_element(driver, password_selectors, "password field")
        if not password_field:
            return False
        
        login_button = try_find_element(driver, button_selectors, "login button")
        if not login_button:
            return False
        
        print(f"[{datetime.now()}] Entering credentials...")
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        login_button.click()
        
        print(f"[{datetime.now()}] Login submitted, waiting...")
        time.sleep(5)
        
        screenshot_path = SCREENSHOT_DIR / f"02_after_login_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"  📸 Screenshot: {screenshot_path}")
        print(f"  ✓ Login completed")
        
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] Login failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def navigate_to_attendance(driver):
    """Navigate to Student Info page to see attendance"""
    try:
        print(f"[{datetime.now()}] Navigating to Student Info...")
        
        # Try to find and click "Student Info" link
        student_info_selectors = [
            ("xpath", "//a[contains(text(), 'Student Info')]"),
            ("xpath", "//a[contains(text(), 'Student')]"),
            ("xpath", "//a[contains(@href, 'Student')]"),
            ("xpath", "//a[contains(@href, 'student')]"),
            ("xpath", "//a[contains(text(), 'Info')]"),
            ("css", "a[href*='student']"),
        ]
        
        student_info_link = try_find_element(driver, student_info_selectors, "Student Info link")
        
        if student_info_link:
            student_info_link.click()
            print(f"  ✓ Clicked Student Info link")
            time.sleep(4)  # Wait for page to load
            
            screenshot_path = SCREENSHOT_DIR / f"03_student_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(str(screenshot_path))
            print(f"  📸 Screenshot: {screenshot_path}")
            
            return True
        else:
            print(f"  ⚠️ Could not find Student Info link")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] Navigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def scrape_attendance(driver):
    """Scrape attendance data from Student Info page"""
    try:
        print(f"[{datetime.now()}] Scraping attendance from current page...")
        
        # Save screenshot
        screenshot_path = SCREENSHOT_DIR / f"04_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"  📸 Screenshot: {screenshot_path}")
        
        # Get page source
        page_source = driver.page_source
        current_url = driver.current_url
        
        print(f"  🌐 Current URL: {current_url}")
        print(f"  📄 Page source: {len(page_source)} characters")
        
        # Save HTML for analysis
        html_file = DATA_DIR / f"student_info_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"  💾 HTML saved: {html_file}")
        
        # Search for attendance percentage
        import re
        
        attendance_data = {
            "url": current_url,
            "timestamp": datetime.now().isoformat()
        }
        
        # Pattern 1: Look for 74.5 or decimal percentages
        decimals_with_percent = re.findall(r'(\d+\.\d+)\s*%', page_source)
        if decimals_with_percent:
            print(f"  Found decimal percentages: {decimals_with_percent}")
            attendance_data["decimal_percentages"] = decimals_with_percent
            
            # If 74.5 or similar is found, use it
            for val in decimals_with_percent:
                if float(val) > 50 and float(val) < 100:
                    attendance_data["likely_attendance"] = f"{val}%"
                    print(f"  ✓ Likely attendance value: {val}%")
        
        # Pattern 2: Look for ALL percentages
        all_percentages = re.findall(r'(\d+)\s*%', page_source)
        if all_percentages:
            print(f"  All percentages: {all_percentages[:15]}")
            attendance_data["all_percentages"] = all_percentages[:20]
        
        # Pattern 3: Look for text containing "attendance" nearby percentages
        attendance_context = re.findall(
            r'attendance[^<]{0,200}?(\d+\.?\d*)\s*%',
            page_source,
            re.IGNORECASE
        )
        if attendance_context:
            print(f"  Attendance context values: {attendance_context}")
            attendance_data["attendance_context"] = attendance_context
        
        # Pattern 4: Extract all text to find attendance
        visible_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for attendance in visible text
        text_lines = visible_text.split('\n')
        for i, line in enumerate(text_lines):
            if 'attendance' in line.lower():
                # Get surrounding lines
                context_lines = text_lines[max(0, i-2):min(len(text_lines), i+3)]
                print(f"  Attendance text context: {' | '.join(context_lines)}")
                
                # Look for percentage in these lines
                for ctx_line in context_lines:
                    percent_match = re.search(r'(\d+\.?\d*)\s*%', ctx_line)
                    if percent_match:
                        attendance_data["found_in_text"] = percent_match.group(1) + "%"
                        print(f"  ✓ Found in text: {percent_match.group(1)}%")
        
        # Pattern 5: Save full visible text
        text_file = DATA_DIR / f"visible_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(visible_text)
        print(f"  💾 Visible text saved: {text_file}")
        
        print(f"[{datetime.now()}] ✓ Data captured")
        return attendance_data
        
    except Exception as e:
        print(f"[{datetime.now()}] Error scraping: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_whatsapp_message(attendance_data):
    """Send WhatsApp notification (optional)"""
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_whatsapp = os.environ.get("TWILIO_WHATSAPP_FROM")
        to_whatsapp_number = os.environ.get("WHATSAPP_PHONE")
        
        if not all([account_sid, auth_token, from_whatsapp, to_whatsapp_number]):
            print(f"[{datetime.now()}] ⚠️ Twilio not configured, skipping WhatsApp")
            return False
        
        to_whatsapp = f"whatsapp:{to_whatsapp_number}"
        client = Client(account_sid, auth_token)
        
        # Get best attendance value
        attendance_val = (
            attendance_data.get("found_in_text") or
            attendance_data.get("likely_attendance") or
            "Check GitHub for captured data"
        )
        
        message_text = f"""🎓 Attendance Update
📅 {datetime.now().strftime('%d %B %Y, %I:%M %p')}

📊 Attendance: {attendance_val}

✅ Data saved to GitHub
🔗 github.com/Crazyvishnu/attendance-tracker
"""
        
        message = client.messages.create(
            from_=from_whatsapp,
            body=message_text,
            to=to_whatsapp
        )
        
        print(f"[{datetime.now()}] ✓ WhatsApp sent: {message.sid}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] ⚠️ WhatsApp failed (non-critical): {str(e)[:100]}")
        return False

def save_attendance_data(attendance_data):
    """Save attendance data to JSON file"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "data": attendance_data
        }
        all_data.append(entry)
        
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
    print(f"MGIT Attendance Tracker Started")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    driver = None
    
    try:
        username = os.environ.get("COLLEGE_USERNAME")
        password = os.environ.get("COLLEGE_PASSWORD")
        
        if not username or not password:
            print("❌ ERROR: Credentials not found in GitHub Secrets")
            return
        
        print(f"✓ Credentials loaded (Username: {username[:3]}***)")
        
        # Setup browser
        print(f"[{datetime.now()}] Setting up Chrome...")
        driver = setup_driver()
        print(f"  ✓ Chrome initialized")
        
        # Step 1: Login
        if not login_to_college_portal(driver, username, password):
            print("❌ ERROR: Login failed")
            return
        print(f"  ✓ Login successful")
        
        # Step 2: Navigate to Student Info
        if not navigate_to_attendance(driver):
            print("⚠️ WARNING: Could not navigate to Student Info")
            print("  Attempting to scrape current page anyway...")
        else:
            print(f"  ✓ Navigated to Student Info page")
        
        # Step 3: Scrape attendance
        attendance_data = scrape_attendance(driver)
        
        if not attendance_data:
            print("❌ ERROR: Failed to scrape")
            return
        
        print(f"  ✓ Attendance data captured")
        
        # Step 4: Save data
        save_attendance_data(attendance_data)
        print(f"  ✓ Data saved to repository")
        
        # Step 5: Send WhatsApp (optional)
        if send_whatsapp_message(attendance_data):
            print(f"  ✓ WhatsApp sent")
        else:
            print(f"  ⚠️ WhatsApp skipped")
        
        print(f"\n{'='*60}")
        print(f"✅ Tracker Completed Successfully!")
        print(f"{'='*60}\n")
        
        # Print summary
        print("\n📊 CAPTURED DATA:")
        if "found_in_text" in attendance_data:
            print(f"  🎯 Attendance found: {attendance_data['found_in_text']}")
        elif "likely_attendance" in attendance_data:
            print(f"  🎯 Likely attendance: {attendance_data['likely_attendance']}")
        elif "decimal_percentages" in attendance_data:
            print(f"  📊 Decimal percentages: {attendance_data['decimal_percentages']}")
        
        print(f"\n📁 Check these files in your repo:")
        print(f"  • data/attendance_log.json - All captured data")
        print(f"  • data/screenshots/ - Visual screenshots")
        print(f"  • data/*.html - Page HTML source")
        print(f"  • data/*.txt - Visible text content")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        if driver:
            try:
                SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                error_screenshot = SCREENSHOT_DIR / f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(str(error_screenshot))
                print(f"\n📸 Error screenshot: {error_screenshot}")
            except:
                pass
        
    finally:
        if driver:
            driver.quit()
            print(f"[{datetime.now()}] Browser closed")

if __name__ == "__main__":
    main()
