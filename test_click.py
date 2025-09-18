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

    # Load workflow via JavaScript
    print("📦 Loading test workflow...")
    driver.execute_script("""
        const testWorkflow = {
            "3": {
                "inputs": {
                    "seed": 123456789,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler"
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "model.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "6": {
                "inputs": {
                    "text": "beautiful scenery",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            }
        };

        const app = window.$app;
        if (app) {
            app.loadWorkflow(JSON.stringify(testWorkflow), 'Test Workflow');
        }
    """)

    time.sleep(0.5)

    # Check if workflow preview is visible
    try:
        workflow_preview = driver.find_element(By.CLASS_NAME, "workflow-preview")
        if workflow_preview.is_displayed():
            print("✅ Workflow preview is visible")
    except:
        print("❌ Workflow preview not found")

    # Find and click the Editor tab button
    print("🔍 Looking for Editor tab button...")
    try:
        # Find all tab buttons
        tab_buttons = driver.find_elements(By.CLASS_NAME, "tab-btn")
        print(f"Found {len(tab_buttons)} tab buttons")

        # Find the Editor button specifically
        editor_button = None
        for button in tab_buttons:
            if "Editor" in button.text:
                editor_button = button
                break

        if editor_button:
            print("🖱️ Clicking Editor tab...")
            editor_button.click()
            time.sleep(1)

            # Check if editor is now visible
            editor_check = driver.execute_script("""
                const app = window.$app;
                const editor = document.querySelector('.workflow-editor');
                const nodeGroups = document.querySelectorAll('.node-group');

                return {
                    viewMode: app ? app.workflowViewMode : null,
                    editorFound: !!editor,
                    editorVisible: editor ? (editor.offsetParent !== null) : false,
                    nodeGroupsCount: nodeGroups.length,
                    workflowNodes: app ? Object.keys(app.workflowNodes || {}) : []
                };
            """)

            print("\n📊 Editor state after clicking tab:")
            print(json.dumps(editor_check, indent=2))

            # Take screenshot
            driver.save_screenshot("editor_after_click.png")
            print("\n📸 Screenshot saved as editor_after_click.png")

            # Check for node groups
            node_groups = driver.find_elements(By.CLASS_NAME, "node-group")
            if node_groups:
                print(f"\n✅ Success! Found {len(node_groups)} node groups in editor")
                for i, group in enumerate(node_groups):
                    header = group.find_element(By.CLASS_NAME, "node-header")
                    print(f"  Node {i+1}: {header.text}")
            else:
                print("\n❌ No node groups found in editor")

        else:
            print("❌ Editor tab button not found")

    except Exception as e:
        print(f"❌ Error: {e}")
        driver.save_screenshot("error_state.png")

    print("\n⏳ Keeping browser open for 5 seconds...")
    time.sleep(5)

finally:
    driver.quit()
    print("✅ Test complete")