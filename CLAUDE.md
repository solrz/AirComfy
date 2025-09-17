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

3. **CORS Proxy Options**
   - proxy.py: Python aiohttp proxy with WebSocket support
   - worker.js: Cloudflare Worker for global deployment
   - CORSHandler.swift: iOS native proxy via custom URL scheme

## Development Commands

### PWA Development
```bash
# Local development server
python -m http.server 8000  # Serve PWA files from PWA/ directory

# CORS proxy (required for ComfyUI API access from browser)
python proxy.py --port 8080 --comfyui http://192.168.11.132:8188

# Testing
python test_aircomfy.py  # Full Selenium test suite
```

### iOS Development
```bash
# Build for simulator
xcodebuild -project iOS/AirComfy.xcodeproj -scheme AirComfy -sdk iphonesimulator -derivedDataPath build

# Build for device (requires proper signing)
xcodebuild -project iOS/AirComfy.xcodeproj -scheme AirComfy -sdk iphoneos

# Open in Xcode for debugging
open iOS/AirComfy.xcodeproj
```

### Testing Requirements
- Chrome/Chromium browser (for Selenium tests)
- Python 3.7+ with selenium, webdriver-manager packages
- Optional: webdriver-manager for automatic ChromeDriver management

## ComfyUI API Integration

### Core Endpoints
- `POST /prompt` - Submit workflow (requires prompt object and client_id)
- `GET /history/{prompt_id}` - Fetch execution results
- `GET /view` - Download generated images (params: filename, subfolder, type)
- `WS /ws?clientId={id}` - Real-time progress updates

### Workflow Format
```json
{
  "nodes": {
    "1": {
      "class_type": "LoadImage",
      "inputs": {}
    }
  }
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

### Core Functionality
- **Connection Management**: Server endpoint selection and WebSocket communication
- **Workflow Processing**: JSON upload, clipboard paste, validation, execution
- **Endpoint Management**: CRUD operations for server endpoints with localStorage persistence
- **Results Display**: Reactive image gallery from ComfyUI execution results
- **Error Handling**: Reactive status messages with type-based styling

### CORS Solutions
1. **Cloudflare Worker**: Deploy via worker.js, serves PWA and proxies API
2. **Python Proxy**: proxy.py provides local CORS proxy with WebSocket support
3. **iOS Native**: CORSHandler.swift converts comfyproxy:// to http:// with CORS headers

### iOS App Architecture (iOS/AirComfy/)
- **ContentView.swift**: Main SwiftUI view with WebView container
- **CORSHandler.swift**: URL scheme handler for bypassing CORS restrictions
- **AirComfyApp.swift**: App entry point
- PWA files are bundled directly in iOS app for offline access
- Uses WKWebView with custom URL scheme (comfyproxy://) for API requests

### PWA Requirements
- HTTPS required for service worker registration
- manifest.json defines app metadata and icons
- sw.js implements cache-first strategy for offline support
- petite-vue (4.1KB) loaded from CDN for minimal bundle size

## Testing

### Selenium Tests (test_aircomfy.py)
- Page load verification
- UI element presence
- Form interactions
- Workflow validation
- Connection handling
- Responsive design
- PWA features

Run with: `python test_aircomfy.py`

### Test Coverage
- Page load and title verification
- UI element presence and functionality
- Connection status and error handling
- Workflow upload (file and clipboard)
- Form validation and interaction
- Responsive design across viewport sizes
- PWA manifest and service worker registration

## Deployment

### Cloudflare Worker
1. Edit COMFYUI_SERVER in worker.js
2. Deploy via dashboard or wrangler CLI
3. Access at https://your-worker.workers.dev

### Local ComfyUI Integration
1. Copy PWA files to ComfyUI web directory
2. Access at http://localhost:8188

### iOS App Store
1. Update bundle identifier and signing in Xcode
2. Archive and upload via Xcode
3. Note: PWA files are bundled into iOS app, so updates require app resubmission

## Development Workflow

### Making Changes to PWA
1. Edit files in `PWA/` directory
2. Test locally with `python -m http.server 8000`
3. Run tests with `python test_aircomfy.py`
4. For iOS: Copy changes to `iOS/AirComfy/` and rebuild

### Vue Development Notes
- Uses petite-vue for minimal overhead (4.1KB vs 34KB for Vue 3)
- Reactive state eliminates manual DOM manipulation
- Template syntax provides declarative UI updates
- Computed properties auto-update when dependencies change
- Event handlers use `@click` instead of `addEventListener`

### iOS Development Notes
- PWA files are duplicated in iOS bundle for offline access
- Changes to PWA must be manually copied to iOS project
- CORSHandler enables direct ComfyUI API access without external proxy
- WebView loads from local bundle, not remote server