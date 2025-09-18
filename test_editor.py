#!/usr/bin/env python3
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_editor_filters_connected_fields():
    print("🧪 Testing editor field filtering...")

    # Setup Chrome options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Initialize driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Load the page
        driver.get("http://localhost:8000")
        time.sleep(3)  # Wait for Vue to initialize

        # Check if Vue app is loaded
        app_loaded = driver.execute_script("return window.$app !== undefined")
        if not app_loaded:
            print("⚠️ Vue app not initialized. Waiting longer...")
            time.sleep(2)

        # Create a test workflow with connected and unconnected fields
        test_workflow = {
            "1": {
                "class_type": "LoadImage",
                "inputs": {
                    "image": "test.png",
                    "upload": "image"
                }
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "a beautiful landscape",
                    "clip": ["3", 1]  # Connected to node 3
                }
            },
            "3": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "model.safetensors"
                }
            },
            "4": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["3", 0],  # Connected to node 3
                    "positive": ["2", 0],  # Connected to node 2
                    "negative": ["5", 0],  # Connected to node 5
                    "seed": 12345,  # Not connected
                    "steps": 20,  # Not connected
                    "cfg": 7.5,  # Not connected
                    "sampler_name": "euler",  # Not connected
                    "scheduler": "normal",  # Not connected
                    "denoise": 1.0  # Not connected
                }
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "",
                    "clip": ["3", 1]  # Connected to node 3
                }
            }
        }

        # Inject the workflow via JavaScript
        workflow_json = json.dumps(test_workflow)
        driver.execute_script(f"""
            window.$app.loadWorkflow('{workflow_json}', 'Test workflow');
            window.$app.switchToEditor();  // Use the Vue method instead of directly setting
        """)

        time.sleep(2)  # Give more time for rendering

        # Debug: Check if workflow was loaded and nodes extracted
        workflow_loaded = driver.execute_script("return window.$app.currentWorkflow !== null")
        nodes_extracted = driver.execute_script("return Object.keys(window.$app.workflowNodes).length")
        print(f"\n🔍 Debug: Workflow loaded: {workflow_loaded}, Nodes extracted: {nodes_extracted}")

        if nodes_extracted > 0:
            nodes_info = driver.execute_script("return JSON.stringify(window.$app.workflowNodes)")
            print(f"📊 Workflow nodes: {nodes_info[:200]}...")

        # Check that the editor is rendered
        editor_container = driver.find_element(By.ID, "workflow-editor-container")
        assert editor_container is not None, "Editor container not found"

        # Debug: print editor HTML content
        print("\n📄 Editor HTML content:")
        print(editor_container.get_attribute('innerHTML')[:500])

        # Check fields for each node
        print("\n📋 Checking visible fields for each node:")

        # Node 1 - LoadImage: should show all fields (none connected)
        node1_fields = driver.find_elements(By.CSS_SELECTOR, '[id^="node-1-"]')
        node1_field_names = [f.get_attribute('id').replace('node-1-', '') for f in node1_fields]
        print(f"  Node 1 (LoadImage): {node1_field_names}")
        assert 'image' in node1_field_names, "Node 1 should show 'image' field"
        assert 'upload' in node1_field_names, "Node 1 should show 'upload' field"

        # Node 2 - CLIPTextEncode: should show only 'text' (clip is connected)
        node2_fields = driver.find_elements(By.CSS_SELECTOR, '[id^="node-2-"]')
        node2_field_names = [f.get_attribute('id').replace('node-2-', '') for f in node2_fields]
        print(f"  Node 2 (CLIPTextEncode): {node2_field_names}")
        assert 'text' in node2_field_names, "Node 2 should show 'text' field"
        assert 'clip' not in node2_field_names, "Node 2 should NOT show 'clip' field (connected)"

        # Node 3 - CheckpointLoaderSimple: should show all fields (none connected)
        node3_fields = driver.find_elements(By.CSS_SELECTOR, '[id^="node-3-"]')
        node3_field_names = [f.get_attribute('id').replace('node-3-', '') for f in node3_fields]
        print(f"  Node 3 (CheckpointLoaderSimple): {node3_field_names}")
        assert 'ckpt_name' in node3_field_names, "Node 3 should show 'ckpt_name' field"

        # Node 4 - KSampler: should show only unconnected fields
        node4_fields = driver.find_elements(By.CSS_SELECTOR, '[id^="node-4-"]')
        node4_field_names = [f.get_attribute('id').replace('node-4-', '') for f in node4_fields]
        print(f"  Node 4 (KSampler): {node4_field_names}")

        # Should show unconnected fields
        unconnected = ['seed', 'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise']
        for field in unconnected:
            assert field in node4_field_names, f"Node 4 should show '{field}' field"

        # Should NOT show connected fields
        connected = ['model', 'positive', 'negative']
        for field in connected:
            assert field not in node4_field_names, f"Node 4 should NOT show '{field}' field (connected)"

        # Node 5 - CLIPTextEncode: should show only 'text' (clip is connected)
        node5_fields = driver.find_elements(By.CSS_SELECTOR, '[id^="node-5-"]')
        node5_field_names = [f.get_attribute('id').replace('node-5-', '') for f in node5_fields]
        print(f"  Node 5 (CLIPTextEncode): {node5_field_names}")
        assert 'text' in node5_field_names, "Node 5 should show 'text' field"
        assert 'clip' not in node5_field_names, "Node 5 should NOT show 'clip' field (connected)"

        print("\n✅ Editor correctly filters out connected fields!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_editor_filters_connected_fields()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Tests failed!")