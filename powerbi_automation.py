import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
import requests

# Configuration
POWER_BI_URL = "https://app.powerbi.com/view?r=your-dashboard-link"
SCREENSHOT_PATH = f"/tmp/powerbi_screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/your/slack/webhook"
CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'

# Slack message function
def send_slack_message(file_path, message):
    with open(file_path, "rb") as file_content:
        response = requests.post(
            "https://slack.com/api/files.upload",
            headers={
                "Authorization": "Bearer your-slack-bot-token"
            },
            data={
                "channels": "#your-channel-name",
                "initial_comment": message,
            },
            files={
                "file": file_content,
            },
        )
    if response.status_code == 200:
        print("Message sent to Slack successfully.")
    else:
        print(f"Failed to send message. Response: {response.text}")

# Take screenshot of the Power BI page
def take_screenshot(url, save_path):
    print("Taking screenshot of the Power BI page...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(5)  # Let the page load completely
    driver.save_screenshot(save_path)
    driver.quit()

# Analyze the screenshot for red/green indicators
def analyze_image(file_path):
    print("Analyzing screenshot for red/green status...")
    image = Image.open(file_path)
    
    # Adjust the cropping based on the actual location of the red/green percentage on your Power BI dashboard
    cropped_image = image.crop((500, 500, 600, 550))  # Adjust coordinates accordingly
    colors = cropped_image.getcolors()

    if colors:
        for count, color in colors:
            # If red color found
            if color[0] > 150 and color[1] < 100 and color[2] < 100:  
                return "red"
            # If green color found
            if color[1] > 150 and color[0] < 100 and color[2] < 100:
                return "green"
    return "none"

# Main execution
if __name__ == "__main__":
    take_screenshot(POWER_BI_URL, SCREENSHOT_PATH)
    
    status = analyze_image(SCREENSHOT_PATH)

    # Prepare message based on the status
    if status == "red":
        message = ":warning: Dear team, we are observing rejection in transactions. Please check the Power BI dashboard."
    elif status == "green":
        message = ":white_check_mark: Dear team, all systems are operational for the last 15 minutes."
    else:
        message = ":information_source: Dashboard data available. Please review manually."

    # Send the screenshot and message to Slack
    send_slack_message(SCREENSHOT_PATH, message)

    print("Script execution complete.")
