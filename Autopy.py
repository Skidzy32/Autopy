from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time
from datetime import datetime

# ===== CONFIGURATION - CHANGE THIS! =====
GROUP_NAME = "Team Tarzan"  # Exact name of your WhatsApp group
# ========================================

# Session schedule
SESSIONS = {
    "Monday": {"day": "Tuesday", "time": "6:00 AM"},
    "Tuesday": {"day": "Wednesday", "time": "5:00 PM"},
    "Wednesday": {"day": "Thursday", "time": "6:00 AM"},
    "Friday": {"day": "Saturday", "time": "5:00 PM"}
}

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
    
    def start_browser(self):
        print("Starting browser...")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("https://web.whatsapp.com")
        print("\n📱 SCAN THE QR CODE WITH YOUR PHONE NOW!")
        
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            self.is_logged_in = True
            print("Logged in successfully!")
        except:
            print("Login timeout. Restart and scan QR code faster.")
            self.driver.quit()
    
    def send_message(self, group_name, message):
        if not self.is_logged_in:
            print("Not logged in!")
            return False
        
        try:
            print(f"Searching for group: {group_name}")
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            search_box.click()
            search_box.clear()
            search_box.send_keys(group_name)
            time.sleep(2)
            
            group_title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//span[@title="{group_name}"]'))
            )
            group_title.click()
            time.sleep(1)
            
            message_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10" or @data-tab="6"]'))
            )
            message_box.click()
            time.sleep(0.5)
            
            actions = ActionChains(self.driver)
            lines = message.split('\n')
            for i, line in enumerate(lines):
                actions.send_keys(line)
                if i < len(lines) - 1:
                    actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT)
            actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
            actions.perform()
            
            time.sleep(2)
            print(f"Message sent at {datetime.now().strftime('%H:%M:%S')}")
            
            with open("message_log.txt", "a") as f:
                f.write(f"{datetime.now()} - Sent to {group_name}\n")
            
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()

bot = WhatsAppBot()

def send_session_reminder(day_name):
    session_info = SESSIONS[day_name]
    message = f"""🗓️ Session Reminder

Tomorrow's session: {session_info['day']} at {session_info['time']}

Please reply with:
✅ - I'm coming
❌ - Can't make it

See you there! 💪"""
    
    print(f"\nSending {day_name} reminder...")
    bot.send_message(GROUP_NAME, message)

def monday_reminder():
    send_session_reminder("Monday")

def tuesday_reminder():
    send_session_reminder("Tuesday")

def wednesday_reminder():
    send_session_reminder("Wednesday")

def friday_reminder():
    send_session_reminder("Friday")

if __name__ == "__main__":
    print("=" * 50)
    print("WhatsApp Session Reminder Bot")
    print("=" * 50)
    
    bot.start_browser()
    
    if not bot.is_logged_in:
        exit()
    
    print("\nSending confirmation message to group...")
    confirmation_msg = "🤖 WhatsApp Auto Schedule Bot is now active!\n\nYou'll receive session reminders at 6 PM on:\n• Monday (for Tuesday 6 AM)\n• Tuesday (for Wednesday 5 PM)\n• Wednesday (for Thursday 6 AM)\n• Friday (for Saturday 5 PM)"
    bot.send_message(GROUP_NAME, confirmation_msg)
    time.sleep(2)
    
    schedule.every().monday.at("18:00").do(monday_reminder)
    schedule.every().tuesday.at("18:00").do(tuesday_reminder)
    schedule.every().wednesday.at("18:00").do(wednesday_reminder)
    schedule.every().friday.at("18:00").do(friday_reminder)
    
    print("\nBot is now running! Keep this window open.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping bot...")
        bot.close()
        print("Bot stopped. Goodbye!")
