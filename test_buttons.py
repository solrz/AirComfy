#!/usr/bin/env python3
"""Test the delete and edit buttons in endpoint management"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

def test_buttons():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        # Load the page
        print("Loading page...")
        driver.get("http://localhost:8000/index.html")

        # Wait for page to load
        time.sleep(2)

        # Click on Manage Endpoints
        print("Looking for Manage Endpoints button...")
        try:
            manage_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Manage Endpoints')]")
            driver.execute_script("arguments[0].scrollIntoView();", manage_btn)
            driver.execute_script("arguments[0].click();", manage_btn)
            print("Clicked Manage Endpoints button")
            time.sleep(2)
        except Exception as e:
            print(f"Could not find Manage Endpoints button: {e}")
            # Try alternative selector
            manage_btn = driver.find_element(By.CLASS_NAME, "secondary-btn")
            driver.execute_script("arguments[0].click();", manage_btn)
            time.sleep(2)

        # Add a test endpoint
        print("Adding test endpoint...")
        name_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Local Server']")
        url_input = driver.find_element(By.XPATH, "//input[@placeholder='http://localhost:8188']")

        name_input.send_keys("Test Server")
        url_input.send_keys("http://test.example.com:8188")

        add_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Endpoint')]")
        add_btn.click()
        time.sleep(1)

        # Check if endpoint was added
        endpoints = driver.find_elements(By.CLASS_NAME, "endpoint-item")
        print(f"Number of endpoints: {len(endpoints)}")

        # Try to click the edit button
        print("Testing edit button...")
        try:
            edit_btn = driver.find_element(By.CLASS_NAME, "edit-btn")
            driver.execute_script("arguments[0].scrollIntoView();", edit_btn)
            print(f"Edit button found. Is displayed: {edit_btn.is_displayed()}, Is enabled: {edit_btn.is_enabled()}")

            # Try clicking with JavaScript
            driver.execute_script("arguments[0].click();", edit_btn)
            time.sleep(1)

            # Check for prompt dialog (handled automatically by Selenium)
            alert = driver.switch_to.alert
            print(f"Edit prompt appeared: {alert.text}")
            alert.dismiss()
        except Exception as e:
            print(f"Edit button error: {e}")

        # Try to click the delete button
        print("Testing delete button...")
        try:
            delete_btn = driver.find_element(By.CLASS_NAME, "delete-btn")
            driver.execute_script("arguments[0].scrollIntoView();", delete_btn)
            print(f"Delete button found. Is displayed: {delete_btn.is_displayed()}, Is enabled: {delete_btn.is_enabled()}")

            # Try clicking with JavaScript
            driver.execute_script("arguments[0].click();", delete_btn)
            time.sleep(1)

            # Check for confirm dialog
            alert = driver.switch_to.alert
            print(f"Delete confirm appeared: {alert.text}")
            alert.accept()  # Click OK to delete

            time.sleep(1)
            endpoints_after = driver.find_elements(By.CLASS_NAME, "endpoint-item")
            print(f"Endpoints after delete: {len(endpoints_after)}")

        except Exception as e:
            print(f"Delete button error: {e}")

        # Get console logs
        logs = driver.get_log('browser')
        if logs:
            print("\nBrowser console logs:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")

    except Exception as e:
        print(f"Test failed: {e}")
        # Take a screenshot for debugging
        driver.save_screenshot("test_failure.png")
        print("Screenshot saved as test_failure.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_buttons()