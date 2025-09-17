#!/usr/bin/env python3
"""
Test script for debug mode functionality in AirComfy PWA
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_debug_mode():
    """Test debug mode functionality"""

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')  # Comment this to see browser

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("Testing normal mode...")
        driver.get("http://localhost:8000")

        # Check that debug badge is not visible
        time.sleep(1)
        debug_badges = driver.find_elements(By.CLASS_NAME, "debug-badge")
        assert len(debug_badges) == 0 or not debug_badges[0].is_displayed(), "Debug badge should not be visible"
        print("✓ Debug badge not shown in normal mode")

        # Check for debug button
        debug_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Enable Debug Mode')]"))
        )
        assert debug_btn.is_displayed(), "Enable debug mode button should be visible"
        print("✓ Enable debug mode button found")

        print("\nTesting debug mode via URL parameter...")
        driver.get("http://localhost:8000?debug=true")
        time.sleep(2)

        # Check that debug badge is visible
        debug_badge = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "debug-badge"))
        )
        assert debug_badge.is_displayed(), "Debug badge should be visible"
        assert "DEBUG" in debug_badge.text, "Debug badge should say DEBUG"
        print("✓ Debug badge shown in debug mode")

        # Check for debug controls
        debug_controls = driver.find_element(By.CLASS_NAME, "debug-controls")
        assert debug_controls.is_displayed(), "Debug controls should be visible"
        print("✓ Debug controls visible")

        # Check if workflow is preloaded
        workflow_status = driver.find_element(By.CLASS_NAME, "workflow-status")
        if "Debug preset workflow loaded" in workflow_status.text:
            print("✓ Debug workflow preloaded")
        else:
            print("ℹ No debug workflow preset found (expected on first run)")

        # Check endpoint selection
        endpoint_dropdown = driver.find_element(By.CLASS_NAME, "endpoint-dropdown")
        selected_option = endpoint_dropdown.find_element(By.CSS_SELECTOR, "option:checked")
        if selected_option.get_attribute("value"):
            print(f"✓ Endpoint preselected: {selected_option.text}")
        else:
            print("ℹ No endpoint preselected (expected on first run)")

        # Test toggling debug mode off
        print("\nTesting debug mode toggle...")
        debug_toggle = driver.find_element(By.CLASS_NAME, "debug-btn")
        debug_toggle.click()
        time.sleep(1)

        # Check that debug badge is hidden after toggle
        debug_badges = driver.find_elements(By.CLASS_NAME, "debug-badge")
        assert len(debug_badges) == 0 or not debug_badges[0].is_displayed(), "Debug badge should be hidden after toggle"
        print("✓ Debug mode toggled off successfully")

        print("\n✅ All debug mode tests passed!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False
    finally:
        driver.quit()

    return True

if __name__ == "__main__":
    print("Starting AirComfy Debug Mode Tests")
    print("=" * 50)
    success = test_debug_mode()
    exit(0 if success else 1)