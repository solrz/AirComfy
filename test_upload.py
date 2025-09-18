#!/usr/bin/env python3

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

try:
    driver = webdriver.Chrome(options=chrome_options)
except:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("🌐 Loading PWA...")
    driver.get("http://localhost:8000")
    wait = WebDriverWait(driver, 10)

    # Wait for page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    print("🔍 Testing Upload JSON button...")

    # Test if clicking Upload JSON triggers file input
    upload_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload JSON')]"))
    )

    # Check if file input exists
    file_input_check = driver.execute_script("""
        const fileInput = document.getElementById('workflow-file-input');
        return {
            exists: !!fileInput,
            type: fileInput ? fileInput.type : null,
            accept: fileInput ? fileInput.accept : null,
            hidden: fileInput ? (fileInput.style.display === 'none') : null
        };
    """)

    print("📁 File input check:", json.dumps(file_input_check, indent=2))

    # Test clicking the upload button
    print("🖱️ Clicking Upload JSON button...")
    upload_button.click()

    # The file dialog should open, but we can't interact with it in Selenium
    # So we'll test the functionality directly

    print("\n🧪 Testing file upload handler directly...")

    # Create a test workflow file
    test_workflow = {
        "1": {
            "class_type": "TestNode",
            "inputs": {
                "test_field": "test_value"
            }
        }
    }

    # Simulate file upload via JavaScript
    result = driver.execute_script("""
        const app = window.$app;
        if (!app) {
            return { error: 'App not found' };
        }

        // Simulate loading a workflow
        const testWorkflow = arguments[0];
        app.loadWorkflow(JSON.stringify(testWorkflow), 'Test Upload');

        return {
            success: true,
            hasWorkflow: !!app.currentWorkflow,
            nodeCount: Object.keys(app.workflowNodes || {}).length,
            workflowStatus: app.workflowStatus
        };
    """, test_workflow)

    print("📤 Upload simulation result:", json.dumps(result, indent=2))

    # Check if workflow preview appears
    time.sleep(1)
    workflow_preview = driver.find_elements(By.CLASS_NAME, "workflow-preview")
    if workflow_preview and workflow_preview[0].is_displayed():
        print("✅ Workflow preview is visible after upload")

    # Check if tabs are visible
    tabs = driver.find_elements(By.CLASS_NAME, "tab-btn")
    if tabs:
        print(f"✅ Found {len(tabs)} tab buttons (Preview/Editor)")

    # Test paste from clipboard button
    print("\n🔍 Testing Paste from Clipboard button...")
    paste_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Paste from Clipboard')]")
    if paste_button:
        print("✅ Paste from Clipboard button found")

    # Test clear button
    clear_button = driver.find_element(By.XPATH, "//button[text()='Clear']")
    if clear_button:
        print("✅ Clear button found")
        clear_button.click()
        time.sleep(0.5)

        # Check if workflow was cleared
        cleared = driver.execute_script("""
            const app = window.$app;
            return {
                hasWorkflow: !!app.currentWorkflow,
                workflowStatus: app.workflowStatus
            };
        """)
        print("🗑️ After clear:", json.dumps(cleared, indent=2))

    print("\n✅ Upload functionality test complete!")

    # Take screenshot
    driver.save_screenshot("upload_test.png")
    print("📸 Screenshot saved as upload_test.png")

    time.sleep(3)

finally:
    driver.quit()