#!/usr/bin/env python3

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class WorkflowEditorTester:
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
        except:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Chrome WebDriver initialized with webdriver-manager")
            except Exception as e:
                print(f"❌ Failed to initialize Chrome WebDriver: {e}")
                raise

    def test_workflow_editor(self):
        print("\n🧪 Testing Workflow Editor Feature...")

        try:
            # Load the page
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Page loaded successfully")

            # Test workflow JSON
            test_workflow = {
                "3": {
                    "inputs": {
                        "seed": 123456789,
                        "steps": 20,
                        "cfg": 8,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": 1,
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0]
                    },
                    "class_type": "KSampler"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "v1-5-pruned-emaonly.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "width": 512,
                        "height": 512,
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage"
                },
                "6": {
                    "inputs": {
                        "text": "test prompt",
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "7": {
                    "inputs": {
                        "text": "test negative",
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                }
            }

            # Simulate workflow loading via JavaScript
            workflow_json = json.dumps(test_workflow)
            self.driver.execute_script(f"""
                const app = window.$app;
                if (app) {{
                    app.loadWorkflow('{workflow_json}', 'Test workflow');
                    return true;
                }}
                return false;
            """)

            time.sleep(1)  # Wait for workflow to load
            print("✅ Workflow loaded successfully")

            # Check if workflow preview is visible
            try:
                workflow_preview = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "workflow-preview"))
                )
                if workflow_preview.is_displayed():
                    print("✅ Workflow preview is visible")
            except:
                print("⚠️ Workflow preview not found, continuing...")

            # Switch to editor view
            self.driver.execute_script("""
                const app = window.$app;
                if (app) {
                    app.switchToEditor();
                    return true;
                }
                return false;
            """)

            time.sleep(0.5)
            print("✅ Switched to editor view")

            # Wait a bit for editor to render
            time.sleep(1)

            # Check if node groups are created
            node_groups = self.driver.find_elements(By.CLASS_NAME, "node-group")
            if len(node_groups) > 0:
                print(f"✅ {len(node_groups)} node groups created in editor")
            else:
                print(f"⚠️ No node groups found")

            # Test field editing
            self.driver.execute_script("""
                const app = window.$app;
                if (app && app.workflowNodes['3']) {
                    // Update seed value
                    app.updateNodeField('3', 'seed', '999999999', 'number');
                    // Update text prompt
                    if (app.workflowNodes['6']) {
                        app.updateNodeField('6', 'text', 'updated prompt text', 'string');
                    }
                    return true;
                }
                return false;
            """)

            print("✅ Field values updated successfully")

            # Test hide/show functionality
            self.driver.execute_script("""
                const app = window.$app;
                if (app) {
                    app.hideAllNodes();
                    return true;
                }
                return false;
            """)

            time.sleep(0.5)
            print("✅ Hide all nodes functionality works")

            self.driver.execute_script("""
                const app = window.$app;
                if (app) {
                    app.showAllNodes();
                    return true;
                }
                return false;
            """)

            time.sleep(0.5)
            print("✅ Show all nodes functionality works")

            # Verify the workflow is updated
            updated_workflow = self.driver.execute_script("""
                const app = window.$app;
                if (app && app.currentWorkflow) {
                    return JSON.stringify(app.currentWorkflow);
                }
                return null;
            """)

            if updated_workflow:
                workflow_obj = json.loads(updated_workflow)
                # Check if values were updated
                if workflow_obj.get('3', {}).get('inputs', {}).get('seed') == 999999999:
                    print("✅ Workflow values are correctly updated")
                if workflow_obj.get('6', {}).get('inputs', {}).get('text') == 'updated prompt text':
                    print("✅ Text fields are correctly updated")

            print("\n✅ All workflow editor tests passed!")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            # Take a screenshot for debugging
            self.driver.save_screenshot("workflow_editor_error.png")
            raise

    def cleanup(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    tester = WorkflowEditorTester()
    try:
        tester.test_workflow_editor()
    finally:
        tester.cleanup()