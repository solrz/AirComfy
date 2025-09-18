#!/usr/bin/env python3

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup Chrome in non-headless mode for debugging
chrome_options = Options()
# Remove headless mode to see what's happening
# chrome_options.add_argument("--headless")
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
    # Load the page
    driver.get("http://localhost:8000")
    time.sleep(2)

    # Load test workflow via JavaScript
    test_workflow = {
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
        }
    }

    # Execute JavaScript to load workflow
    result = driver.execute_script("""
        const testWorkflow = arguments[0];
        const app = window.$app;

        if (!app) {
            return { error: 'App not found' };
        }

        // Load workflow
        app.loadWorkflow(JSON.stringify(testWorkflow), 'Test Workflow');

        // Get initial state
        const state1 = {
            hasWorkflow: !!app.currentWorkflow,
            viewMode: app.workflowViewMode,
            nodeCount: Object.keys(app.workflowNodes || {}).length
        };

        // Switch to editor
        app.workflowViewMode = 'editor';

        // Get state after switch
        const state2 = {
            viewMode: app.workflowViewMode,
            nodeGroups: document.querySelectorAll('.node-group').length,
            editorVisible: !!document.querySelector('.workflow-editor'),
            tabButtons: document.querySelectorAll('.tab-btn').length,
            workflowPreviewSection: !!document.querySelector('.workflow-preview')
        };

        return { state1, state2 };
    """, test_workflow)

    print("JavaScript execution result:")
    print(json.dumps(result, indent=2))

    # Take a screenshot
    driver.save_screenshot("workflow_editor_state.png")
    print("\n📸 Screenshot saved as workflow_editor_state.png")

    # Check visible elements
    print("\n🔍 Checking visible elements:")
    elements_to_check = [
        ('.workflow-preview', 'Workflow preview section'),
        ('.workflow-tabs', 'Workflow tabs'),
        ('.tab-btn', 'Tab buttons'),
        ('.workflow-editor', 'Editor container'),
        ('.node-group', 'Node groups'),
        ('.field-group', 'Field groups')
    ]

    for selector, name in elements_to_check:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            visible = [e for e in elements if e.is_displayed()]
            print(f"✅ {name}: {len(elements)} found, {len(visible)} visible")
        else:
            print(f"❌ {name}: Not found")

    # Keep browser open for 3 seconds to see the result
    time.sleep(3)

finally:
    driver.quit()