#!/usr/bin/env python3

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AirComfyTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("Trying with webdriver-manager...")
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Chrome WebDriver initialized with webdriver-manager")
            except Exception as e2:
                print(f"❌ Failed with webdriver-manager: {e2}")
                raise

    def test_page_load(self):
        print("\n🧪 Testing page load...")
        try:
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            title = self.driver.title
            assert title == "AirComfy", f"Expected 'AirComfy', got '{title}'"
            print("✅ Page loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Page load failed: {e}")
            return False

    def test_ui_elements(self):
        print("\n🧪 Testing UI elements...")
        tests_passed = 0
        total_tests = 0

        # Test header elements
        elements_to_test = [
            ("h1", "AirComfy header"),
            ("#connectionStatus", "Connection status"),
            ("#serverUrl", "Server URL input"),
            ("#connectBtn", "Connect button"),
            ("#workflowInput", "Workflow textarea"),
            ("#validateBtn", "Validate button"),
            ("#executeBtn", "Execute button"),
            ("#status", "Status display"),
            ("#progress", "Progress display"),
            ("#results", "Results display")
        ]

        for selector, description in elements_to_test:
            total_tests += 1
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ {description} found")
                tests_passed += 1
            except NoSuchElementException:
                print(f"❌ {description} not found")

        print(f"UI Elements: {tests_passed}/{total_tests} tests passed")
        return tests_passed == total_tests

    def test_form_interactions(self):
        print("\n🧪 Testing form interactions...")
        try:
            # Test server URL input
            server_input = self.driver.find_element(By.ID, "serverUrl")
            original_value = server_input.get_attribute("value")
            server_input.clear()
            server_input.send_keys("http://test.example.com:8188")
            assert server_input.get_attribute("value") == "http://test.example.com:8188"
            print("✅ Server URL input working")

            # Reset to original value
            server_input.clear()
            server_input.send_keys(original_value)

            # Test workflow textarea
            workflow_input = self.driver.find_element(By.ID, "workflowInput")
            test_json = '{"test": "workflow"}'
            workflow_input.send_keys(test_json)
            assert test_json in workflow_input.get_attribute("value")
            print("✅ Workflow textarea working")

            # Clear workflow
            workflow_input.clear()

            return True
        except Exception as e:
            print(f"❌ Form interaction failed: {e}")
            return False

    def test_validation_functionality(self):
        print("\n🧪 Testing workflow validation...")
        try:
            workflow_input = self.driver.find_element(By.ID, "workflowInput")
            validate_btn = self.driver.find_element(By.ID, "validateBtn")
            status_display = self.driver.find_element(By.ID, "status")

            # Test empty workflow validation
            workflow_input.clear()
            validate_btn.click()
            time.sleep(1)
            status_text = status_display.text
            assert "Please enter a workflow" in status_text
            print("✅ Empty workflow validation working")

            # Test invalid JSON validation
            workflow_input.send_keys('{"invalid": json}')
            validate_btn.click()
            time.sleep(1)
            status_text = status_display.text
            assert "validation failed" in status_text.lower()
            print("✅ Invalid JSON validation working")

            # Test valid JSON validation
            workflow_input.clear()
            valid_workflow = '{"nodes": {"1": {"class_type": "LoadImage", "inputs": {}}}}'
            workflow_input.send_keys(valid_workflow)
            validate_btn.click()
            time.sleep(1)
            status_text = status_display.text
            assert "validation passed" in status_text.lower()
            print("✅ Valid JSON validation working")

            return True
        except Exception as e:
            print(f"❌ Validation test failed: {e}")
            return False

    def test_connection_status(self):
        print("\n🧪 Testing connection status...")
        try:
            connection_status = self.driver.find_element(By.ID, "connectionStatus")
            initial_status = connection_status.text
            assert initial_status == "Disconnected"
            print("✅ Initial connection status correct")

            # Test connection attempt (will fail but should update UI)
            connect_btn = self.driver.find_element(By.ID, "connectBtn")
            connect_btn.click()

            # Wait a moment for the connection attempt
            time.sleep(3)

            # Check if status display shows connection error
            status_display = self.driver.find_element(By.ID, "status")
            status_text = status_display.text.lower()
            assert any(word in status_text for word in ["failed", "error", "connection"])
            print("✅ Connection error handling working")

            return True
        except Exception as e:
            print(f"❌ Connection status test failed: {e}")
            return False

    def test_responsive_design(self):
        print("\n🧪 Testing responsive design...")
        try:
            # Test desktop view
            self.driver.set_window_size(1920, 1080)
            time.sleep(1)

            main_element = self.driver.find_element(By.TAG_NAME, "main")
            desktop_width = main_element.size['width']

            # Test mobile view
            self.driver.set_window_size(375, 667)
            time.sleep(1)

            mobile_width = main_element.size['width']

            # Mobile should be narrower than desktop
            assert mobile_width < desktop_width
            print("✅ Responsive design working")

            # Reset to desktop
            self.driver.set_window_size(1920, 1080)

            return True
        except Exception as e:
            print(f"❌ Responsive design test failed: {e}")
            return False

    def test_pwa_features(self):
        print("\n🧪 Testing PWA features...")
        try:
            # Check if service worker is registered
            sw_registered = self.driver.execute_script("""
                return navigator.serviceWorker.getRegistrations().then(registrations => {
                    return registrations.length > 0;
                });
            """)

            # Wait a moment for service worker registration
            time.sleep(2)

            # Check manifest
            manifest_link = self.driver.find_element(By.CSS_SELECTOR, 'link[rel="manifest"]')
            manifest_href = manifest_link.get_attribute("href")
            assert "manifest.json" in manifest_href
            print("✅ Manifest link found")

            # Check theme color
            theme_color = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="theme-color"]')
            assert theme_color.get_attribute("content") == "#2196F3"
            print("✅ Theme color set correctly")

            return True
        except Exception as e:
            print(f"❌ PWA features test failed: {e}")
            return False

    def run_all_tests(self):
        print("🚀 Starting AirComfy PWA Tests")
        print("=" * 50)

        tests = [
            ("Page Load", self.test_page_load),
            ("UI Elements", self.test_ui_elements),
            ("Form Interactions", self.test_form_interactions),
            ("Validation Functionality", self.test_validation_functionality),
            ("Connection Status", self.test_connection_status),
            ("Responsive Design", self.test_responsive_design),
            ("PWA Features", self.test_pwa_features)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! AirComfy PWA is working correctly.")
        else:
            print(f"⚠️  {total - passed} tests failed. Review the issues above.")

        return passed == total

    def cleanup(self):
        if self.driver:
            self.driver.quit()
            print("🧹 WebDriver cleaned up")

if __name__ == "__main__":
    tester = AirComfyTester()
    try:
        success = tester.run_all_tests()
        exit(0 if success else 1)
    finally:
        tester.cleanup()