# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AirComfy is a minimal Progressive Web App (PWA) and native iOS app for sending workflows to ComfyUI API. The project maintains a zero-dependency approach for maximum simplicity and reliability.

## Architecture

### Core Components

1. **PWA (PWA/ directory)**
   - Single page application with all logic in index.html
   - Service worker (sw.js) for offline support
   - Direct ComfyUI API integration via fetch/WebSocket
   - Cloudflare Worker deployment option (worker.js)

2. **iOS App (iOS/ directory)**
   - SwiftUI WebView wrapper loading PWA
   - CORSHandler.swift for proxying requests via comfyproxy:// scheme
   - ContentView.swift manages WebView lifecycle
   - NOTE: iOS app does NOT currently bundle PWA files - needs to load from remote or local server

3. **CORS Proxy Options**
   - proxy.py: Python aiohttp proxy with WebSocket support
   - worker.js: Cloudflare Worker for global deployment
   - CORSHandler.swift: iOS native proxy via custom URL scheme

## Development Commands

### PWA Development
```bash
# Local development server (run from project root)
cd PWA && python -m http.server 8000

# CORS proxy (required for ComfyUI API access from browser)
python proxy.py --port 8080 --comfyui http://192.168.11.132:8188

# Run all tests
python test_aircomfy.py

# Debug mode tests
python test_debug_mode.py

# Button functionality tests
python test_buttons.py
```

### iOS Development
```bash
# Build for simulator
cd iOS && xcodebuild -project AirComfy.xcodeproj -scheme AirComfy -sdk iphonesimulator -derivedDataPath build

# Build for device (requires proper signing)
cd iOS && xcodebuild -project AirComfy.xcodeproj -scheme AirComfy -sdk iphoneos

# Open in Xcode for debugging
open iOS/AirComfy.xcodeproj

# To bundle PWA files in iOS app (if needed in future):
# Copy PWA files to iOS/AirComfy/ and update ContentView.swift to load from bundle
```

### Testing Requirements
- Chrome/Chromium browser (for Selenium tests)
- Python 3.7+ with selenium, webdriver-manager packages
- webdriver-manager for automatic ChromeDriver management: `pip install webdriver-manager selenium`

## ComfyUI API Integration

### Core Endpoints
- `POST /prompt` - Submit workflow (requires prompt object and client_id)
- `GET /history/{prompt_id}` - Fetch execution results
- `GET /view` - Download generated images (params: filename, subfolder, type)
- `WS /ws?clientId={id}` - Real-time progress updates
- `GET /system_stats` - Get system resource usage (CPU, memory, GPU)

### Workflow Format
```json
{
  "prompt": {
    "1": {
      "class_type": "LoadImage",
      "inputs": {}
    }
  },
  "client_id": "unique-client-id"
}
```

## Key Implementation Details

### Vue Architecture (PWA/index.html)
**Framework**: Uses petite-vue (4.1KB) for reactive state management and DOM updates
- **AirComfyApp()**: Main Vue component function returning reactive state object
- **Reactive State**: All UI state (connections, workflows, endpoints) handled reactively
- **Computed Properties**: `canExecute`, `workflowPreview` automatically update based on state
- **Template Directives**: `v-model`, `v-show`, `v-for`, `@click` for declarative UI
- **Lifecycle**: `mounted()` hook initializes app state and service worker

### Core Features
- **Debug Mode**: Toggle with debug button for verbose logging and preset endpoints
- **System Stats**: View ComfyUI system resource usage (CPU, memory, GPU)
- **Endpoint Manager**: Add/edit/delete ComfyUI server endpoints with persistence
- **Connection Management**: Server endpoint selection and WebSocket communication
- **Workflow Processing**: JSON upload, clipboard paste, validation, execution
- **Results Display**: Reactive image gallery from ComfyUI execution results
- **Error Handling**: Reactive status messages with type-based styling

### CORS Solutions
1. **Cloudflare Worker**: Deploy via PWA/worker.js, serves PWA and proxies API
2. **Python Proxy**: proxy.py provides local CORS proxy with WebSocket support
3. **iOS Native**: CORSHandler.swift converts comfyproxy:// to http:// with CORS headers

### iOS App Architecture (iOS/AirComfy/)
- **ContentView.swift**: Main SwiftUI view with WebView container, currently loads from http://localhost:8000
- **CORSHandler.swift**: URL scheme handler for bypassing CORS restrictions
- **AirComfyApp.swift**: App entry point
- Uses WKWebView with custom URL scheme (comfyproxy://) for API requests
- Currently requires PWA to be served separately (not bundled)

### PWA Requirements
- HTTPS required for service worker registration
- manifest.json defines app metadata and icons
- sw.js implements cache-first strategy for offline support
- petite-vue (4.1KB) loaded from CDN for minimal bundle size
- style.css embedded directly in index.html for simplicity

## Testing

### Test Suites
1. **test_aircomfy.py**: Main test suite covering all functionality
2. **test_debug_mode.py**: Debug mode specific tests
3. **test_buttons.py**: Button interaction and visibility tests

### Test Coverage
- Page load and title verification
- UI element presence and functionality
- Connection status and error handling
- Workflow upload (file and clipboard)
- Form validation and interaction
- Responsive design across viewport sizes
- PWA manifest and service worker registration
- Debug mode toggle and presets
- System stats modal functionality

## Deployment

### Cloudflare Worker
1. Edit COMFYUI_SERVER in PWA/worker.js
2. Deploy via dashboard or wrangler CLI
3. Access at https://your-worker.workers.dev
4. See CLOUDFLARE_DEPLOY.md for detailed instructions

### Local ComfyUI Integration
1. Copy PWA files to ComfyUI web directory
2. Access at http://localhost:8188

### iOS App Store
1. Update ContentView.swift to load from bundled files or production URL
2. Update bundle identifier and signing in Xcode
3. Archive and upload via Xcode

## Development Workflow

### Making Changes to PWA
1. Edit files in `PWA/` directory
2. Test locally with `cd PWA && python -m http.server 8000`
3. Run tests with `python test_aircomfy.py`
4. For iOS: Ensure ContentView.swift points to correct PWA URL

### Vue Development Notes
- Uses petite-vue for minimal overhead (4.1KB vs 34KB for Vue 3)
- Reactive state eliminates manual DOM manipulation
- Template syntax provides declarative UI updates
- Computed properties auto-update when dependencies change
- Event handlers use `@click` instead of `addEventListener`

### iOS Development Notes
- Currently loads PWA from external URL (http://localhost:8000)
- CORSHandler enables direct ComfyUI API access without external proxy
- Test on simulator first before device deployment
- To bundle PWA files: copy to iOS/AirComfy/ and update ContentView.swift to use Bundle.main.url

## Sample Workflows

Example workflow files in repository:
- **SD15-basicT2I.json**: Stable Diffusion 1.5 text-to-image workflow
- **wan22-telltale-example.json**: Complex workflow example with multiple nodes