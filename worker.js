/**
 * Cloudflare Worker for AirComfy PWA
 * Proxies ComfyUI API requests with CORS headers and serves PWA files
 */

const COMFYUI_SERVER = 'http://192.168.11.132:8188'; // Change this to your ComfyUI server

// Whitelisted domains that can use this proxy (empty array = allow all)
const ALLOWED_ORIGINS = [
  // 'https://yourdomain.com',
  // 'https://www.yourdomain.com',
  // 'http://localhost:3000',  // For local development
];

// PWA static files - base64 encoded or raw text
const STATIC_FILES = {
  '/': 'index.html',
  '/index.html': 'index.html',
  '/style.css': 'style.css',
  '/manifest.json': 'manifest.json',
  '/sw.js': 'sw.js',
  '/icon-192.png': 'icon-192.png'
};

// File contents will be served from these
const PWA_FILES = {
  'index.html': `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AirComfy</title>
    <link rel="stylesheet" href="style.css">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#2196F3">
    <meta name="description" content="Minimal PWA for ComfyUI workflow execution">
</head>
<body>
    <header>
        <h1>AirComfy</h1>
        <div class="connection-status" id="connectionStatus">Disconnected</div>
    </header>

    <main>
        <section class="config-section">
            <h2>ComfyUI Configuration</h2>
            <div class="input-group">
                <label for="serverUrl">Server URL:</label>
                <input type="url" id="serverUrl" placeholder="Leave empty to use proxy" value="">
            </div>
            <button id="connectBtn" class="primary-btn">Connect</button>
        </section>

        <section class="workflow-section">
            <h2>Workflow</h2>
            <div class="input-group">
                <label for="workflowInput">JSON Workflow:</label>
                <textarea id="workflowInput" placeholder="Paste your ComfyUI workflow JSON here..." rows="10"></textarea>
            </div>
            <div class="workflow-actions">
                <button id="validateBtn" class="secondary-btn">Validate</button>
                <button id="executeBtn" class="primary-btn" disabled>Execute</button>
            </div>
        </section>

        <section class="results-section">
            <h2>Results</h2>
            <div id="status" class="status-display"></div>
            <div id="progress" class="progress-display"></div>
            <div id="results" class="results-display"></div>
        </section>
    </main>

    <script>
        class AirComfy {
            constructor() {
                this.serverUrl = '';
                this.clientId = this.generateClientId();
                this.websocket = null;
                this.currentPromptId = null;
                this.init();
            }

            init() {
                this.bindEvents();
                this.loadSettings();
                this.registerServiceWorker();
            }

            bindEvents() {
                document.getElementById('connectBtn').addEventListener('click', () => this.connect());
                document.getElementById('validateBtn').addEventListener('click', () => this.validateWorkflow());
                document.getElementById('executeBtn').addEventListener('click', () => this.executeWorkflow());
                document.getElementById('serverUrl').addEventListener('input', (e) => this.saveSettings());
            }

            generateClientId() {
                return Math.random().toString(36).substring(2) + Date.now().toString(36);
            }

            loadSettings() {
                const saved = localStorage.getItem('aircomfy-settings');
                if (saved) {
                    const settings = JSON.parse(saved);
                    document.getElementById('serverUrl').value = settings.serverUrl || '';
                }
            }

            saveSettings() {
                const settings = {
                    serverUrl: document.getElementById('serverUrl').value
                };
                localStorage.setItem('aircomfy-settings', JSON.stringify(settings));
            }

            async connect() {
                const serverUrl = document.getElementById('serverUrl').value.trim();

                // Use proxy if no server URL specified
                this.serverUrl = serverUrl || window.location.origin;
                this.saveSettings();

                try {
                    const response = await fetch(\`\${this.serverUrl}/system_stats\`);
                    if (response.ok) {
                        this.updateConnectionStatus('Connected');
                        this.connectWebSocket();
                        document.getElementById('executeBtn').disabled = false;
                        this.updateStatus('Connected to ComfyUI server', 'success');
                    } else {
                        throw new Error(\`Server responded with \${response.status}\`);
                    }
                } catch (error) {
                    this.updateConnectionStatus('Disconnected');
                    document.getElementById('executeBtn').disabled = true;
                    this.updateStatus(\`Connection failed: \${error.message}\`, 'error');
                }
            }

            connectWebSocket() {
                const wsUrl = this.serverUrl.replace('http', 'ws') + \`/ws?clientId=\${this.clientId}\`;

                if (this.websocket) {
                    this.websocket.close();
                }

                this.websocket = new WebSocket(wsUrl);

                this.websocket.onopen = () => {
                    this.updateStatus('WebSocket connected', 'success');
                };

                this.websocket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                };

                this.websocket.onclose = () => {
                    this.updateStatus('WebSocket disconnected', 'warning');
                };

                this.websocket.onerror = (error) => {
                    this.updateStatus('WebSocket error occurred', 'error');
                };
            }

            handleWebSocketMessage(data) {
                if (data.type === 'status') {
                    this.updateProgress(\`Queue: \${data.data.status.exec_info.queue_remaining}\`);
                } else if (data.type === 'progress') {
                    const progress = Math.round((data.data.value / data.data.max) * 100);
                    this.updateProgress(\`Progress: \${progress}% (\${data.data.node})\`);
                } else if (data.type === 'executed') {
                    this.handleExecutionComplete(data.data);
                }
            }

            validateWorkflow() {
                const workflowText = document.getElementById('workflowInput').value.trim();

                if (!workflowText) {
                    this.updateStatus('Please enter a workflow', 'error');
                    return false;
                }

                try {
                    const workflow = JSON.parse(workflowText);
                    if (typeof workflow !== 'object' || !workflow) {
                        throw new Error('Invalid workflow format');
                    }
                    this.updateStatus('Workflow validation passed', 'success');
                    return true;
                } catch (error) {
                    this.updateStatus(\`Workflow validation failed: \${error.message}\`, 'error');
                    return false;
                }
            }

            async executeWorkflow() {
                if (!this.validateWorkflow()) return;
                if (!this.serverUrl) {
                    this.updateStatus('Please connect to server first', 'error');
                    return;
                }

                const workflowText = document.getElementById('workflowInput').value.trim();
                const workflow = JSON.parse(workflowText);

                const promptData = {
                    prompt: workflow,
                    client_id: this.clientId
                };

                try {
                    this.updateStatus('Submitting workflow...', 'info');
                    const response = await fetch(\`\${this.serverUrl}/prompt\`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(promptData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        this.currentPromptId = result.prompt_id;
                        this.updateStatus(\`Workflow submitted. Prompt ID: \${this.currentPromptId}\`, 'success');
                    } else {
                        throw new Error(\`Server error: \${response.status}\`);
                    }
                } catch (error) {
                    this.updateStatus(\`Execution failed: \${error.message}\`, 'error');
                }
            }

            async handleExecutionComplete(data) {
                if (data.prompt_id === this.currentPromptId) {
                    this.updateStatus('Workflow execution completed', 'success');
                    this.updateProgress('Complete');

                    try {
                        const historyResponse = await fetch(\`\${this.serverUrl}/history/\${this.currentPromptId}\`);
                        if (historyResponse.ok) {
                            const history = await historyResponse.json();
                            this.displayResults(history);
                        }
                    } catch (error) {
                        this.updateStatus(\`Failed to fetch results: \${error.message}\`, 'error');
                    }
                }
            }

            displayResults(history) {
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '';

                for (const [promptId, promptData] of Object.entries(history)) {
                    if (promptData.outputs) {
                        for (const [nodeId, nodeOutput] of Object.entries(promptData.outputs)) {
                            if (nodeOutput.images) {
                                nodeOutput.images.forEach(image => {
                                    const img = document.createElement('img');
                                    img.src = \`\${this.serverUrl}/view?filename=\${image.filename}&subfolder=\${image.subfolder}&type=\${image.type}\`;
                                    img.alt = \`Generated image from node \${nodeId}\`;
                                    img.className = 'result-image';
                                    resultsDiv.appendChild(img);
                                });
                            }
                        }
                    }
                }

                if (resultsDiv.innerHTML === '') {
                    resultsDiv.innerHTML = '<p>No images generated</p>';
                }
            }

            updateConnectionStatus(status) {
                const element = document.getElementById('connectionStatus');
                element.textContent = status;
                element.className = \`connection-status \${status.toLowerCase()}\`;
            }

            updateStatus(message, type = 'info') {
                const element = document.getElementById('status');
                element.textContent = message;
                element.className = \`status-display \${type}\`;
            }

            updateProgress(message) {
                document.getElementById('progress').textContent = message;
            }

            async registerServiceWorker() {
                if ('serviceWorker' in navigator) {
                    try {
                        await navigator.serviceWorker.register('./sw.js');
                    } catch (error) {
                        console.warn('Service Worker registration failed');
                    }
                }
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            new AirComfy();
        });
    </script>
</body>
</html>`,

  'style.css': `/* CSS content from original style.css */`,
  'manifest.json': `{
    "name": "AirComfy",
    "short_name": "AirComfy",
    "description": "Minimal PWA for ComfyUI workflow execution",
    "start_url": "./",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#2196F3",
    "orientation": "portrait-primary",
    "scope": "./",
    "lang": "en",
    "categories": ["productivity", "utilities"],
    "icons": [
        {
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable any"
        }
    ]
}`,
  'sw.js': `/* Service worker content */`
};

function isOriginAllowed(origin, request) {
  // If no whitelist is set, allow all origins
  if (ALLOWED_ORIGINS.length === 0) {
    return true;
  }

  // Always allow requests from the Worker's own domain (for PWA hosting)
  const workerOrigin = new URL(request.url).origin;
  if (origin === workerOrigin) {
    return true;
  }

  // Check if origin is in whitelist
  return ALLOWED_ORIGINS.includes(origin);
}

function addCorsHeaders(response, origin, request) {
  if (isOriginAllowed(origin, request)) {
    response.headers.set('Access-Control-Allow-Origin', origin || '*');
  } else {
    response.headers.set('Access-Control-Allow-Origin', 'null');
  }
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  response.headers.set('Access-Control-Allow-Credentials', 'false');
  return response;
}

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  const origin = request.headers.get('Origin');

  // Check if origin is allowed (for API endpoints only, not static files)
  const isApiRequest = path.startsWith('/system_stats') ||
                      path.startsWith('/prompt') ||
                      path.startsWith('/history') ||
                      path.startsWith('/view') ||
                      path.startsWith('/ws');

  if (isApiRequest && !isOriginAllowed(origin, request)) {
    return new Response('Origin not allowed', {
      status: 403,
      headers: { 'Content-Type': 'text/plain' }
    });
  }

  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return addCorsHeaders(new Response(null, { status: 204 }), origin, request);
  }

  // Serve static PWA files
  if (STATIC_FILES[path]) {
    const filename = STATIC_FILES[path];
    if (PWA_FILES[filename]) {
      const contentType = getContentType(filename);
      const response = new Response(PWA_FILES[filename], {
        headers: { 'Content-Type': contentType }
      });
      return addCorsHeaders(response, origin, request);
    }
  }

  // Proxy to ComfyUI API
  if (path.startsWith('/system_stats') ||
      path.startsWith('/prompt') ||
      path.startsWith('/history') ||
      path.startsWith('/view') ||
      path.startsWith('/ws')) {

    // WebSocket upgrade
    if (request.headers.get('Upgrade') === 'websocket') {
      return handleWebSocket(request);
    }

    // Regular HTTP proxy
    const targetUrl = COMFYUI_SERVER + path + url.search;

    const proxyRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body
    });

    try {
      const response = await fetch(proxyRequest);
      const newResponse = new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
      });
      return addCorsHeaders(newResponse, origin, request);
    } catch (error) {
      return addCorsHeaders(new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }), origin, request);
    }
  }

  // Default: serve index.html
  const response = new Response(PWA_FILES['index.html'], {
    headers: { 'Content-Type': 'text/html' }
  });
  return addCorsHeaders(response, origin, request);
}

async function handleWebSocket(request) {
  const url = new URL(request.url);
  const wsUrl = COMFYUI_SERVER.replace('http', 'ws') + '/ws' + url.search;

  // Create WebSocket pair
  const [client, server] = Object.values(new WebSocketPair());

  // Connect to ComfyUI WebSocket
  const upstream = new WebSocket(wsUrl);

  // Forward messages both ways
  upstream.addEventListener('message', event => {
    client.send(event.data);
  });

  server.addEventListener('message', event => {
    upstream.send(event.data);
  });

  upstream.addEventListener('close', () => client.close());
  server.addEventListener('close', () => upstream.close());

  return new Response(null, { status: 101, webSocket: client });
}

function getContentType(filename) {
  if (filename.endsWith('.html')) return 'text/html';
  if (filename.endsWith('.css')) return 'text/css';
  if (filename.endsWith('.js')) return 'application/javascript';
  if (filename.endsWith('.json')) return 'application/json';
  if (filename.endsWith('.png')) return 'image/png';
  return 'text/plain';
}

// Cloudflare Worker event listener
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});