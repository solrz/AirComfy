#!/usr/bin/env python3

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
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
    # Load the page
    driver.get("http://localhost:8000")
    time.sleep(2)

    # Debug the Vue app structure
    debug_result = driver.execute_script("""
        // Check app setup
        const app = window.$app;
        if (!app) {
            return { error: 'No app found' };
        }

        // Load test workflow
        const testWorkflow = {
            "3": {
                "inputs": {
                    "seed": 123456789,
                    "steps": 20
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "name": "test.safetensors"
                },
                "class_type": "CheckpointLoader"
            }
        };

        app.loadWorkflow(JSON.stringify(testWorkflow), 'Debug Test');

        // Get state after loading
        const afterLoad = {
            hasWorkflow: !!app.currentWorkflow,
            workflowNodes: app.workflowNodes,
            nodeCount: Object.keys(app.workflowNodes || {}).length,
            viewMode: app.workflowViewMode
        };

        // Switch to editor
        app.workflowViewMode = 'editor';

        // Force a tick
        setTimeout(() => {
            // Check DOM after switch
            const editorSection = document.querySelector('.workflow-editor');
            const editorDisplay = editorSection ? window.getComputedStyle(editorSection).display : 'none';

            // Try to manually check what should be rendered
            const shouldRender = [];
            for (const [nodeId, node] of Object.entries(app.workflowNodes || {})) {
                shouldRender.push({
                    nodeId,
                    classType: node.class_type,
                    inputCount: Object.keys(node.inputs || {}).length
                });
            }

            window.debugResult = {
                afterLoad,
                afterSwitch: {
                    viewMode: app.workflowViewMode,
                    editorFound: !!editorSection,
                    editorDisplay,
                    nodeGroups: document.querySelectorAll('.node-group').length,
                    shouldRender
                }
            };
        }, 500);

        return 'Check window.debugResult in 500ms';
    """)

    print("Initial result:", debug_result)
    time.sleep(1)

    # Get the delayed result
    final_result = driver.execute_script("return window.debugResult;")
    print("\nFinal debug result:")
    print(json.dumps(final_result, indent=2))

    # Check HTML structure
    html_check = driver.execute_script("""
        const editor = document.querySelector('.workflow-editor');
        if (editor) {
            return {
                innerHTML: editor.innerHTML.substring(0, 500),
                childCount: editor.children.length,
                display: window.getComputedStyle(editor).display
            };
        }
        return null;
    """)

    print("\nEditor HTML check:")
    print(json.dumps(html_check, indent=2))

    # Take screenshot
    driver.save_screenshot("debug_state.png")
    print("\n📸 Screenshot saved as debug_state.png")

    time.sleep(3)

finally:
    driver.quit()