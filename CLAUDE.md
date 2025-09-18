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
   - **BUILD ISSUE**: iOS project has duplicate file references (PWA files and iOS/AirComfy files) causing build conflicts
   - NOTE: iOS app bundles PWA files but ContentView.swift loads from http://localhost:8000

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
python proxy.py --port 8080 --comfyui http://localhost:8188

# Run all tests
python test_aircomfy.py

# Debug mode tests
python test_debug_mode.py

# Button functionality tests
python test_buttons.py
```

### iOS Development
```bash
# Build for simulator (from project root)
xcodebuild -project iOS/AirComfy.xcodeproj -scheme AirComfy -sdk iphonesimulator -derivedDataPath iOS/build

# Build for device (requires proper signing)
xcodebuild -project iOS/AirComfy.xcodeproj -scheme AirComfy -sdk iphoneos -derivedDataPath iOS/build

# Clean build folder if encountering duplicate file errors
rm -rf iOS/build

# Open in Xcode for debugging
open iOS/AirComfy.xcodeproj

# Fix duplicate file references:
# Remove duplicate PWA file references from iOS/AirComfy/ in Xcode project navigator
```

### Testing
```bash
# Install test dependencies
pip install selenium webdriver-manager

# Run main test suite
python test_aircomfy.py

# Run specific test suites
python test_debug_mode.py  # Debug mode functionality
python test_buttons.py     # Button interactions
python test_workflow_editor.py  # Workflow editor
python test_upload.py      # File upload functionality
```

**Requirements:**
- Chrome/Chromium browser
- Python 3.7+ with selenium, webdriver-manager packages

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
- **ContentView.swift**: Main SwiftUI view with WebView container, loads from http://localhost:8000
- **CORSHandler.swift**: URL scheme handler converting comfyproxy:// to http:// with CORS headers
- **AirComfyApp.swift**: App entry point with SwiftUI lifecycle
- Uses WKWebView with custom URL scheme handler for API proxying
- PWA files are bundled but need to update ContentView.swift to use Bundle.main.url for production
- **IMPORTANT**: Do NOT copy PWA files into iOS/AirComfy/ folder - they should only exist in PWA/ folder and be referenced from there in Copy Bundle Resources

### PWA Requirements
- HTTPS required for service worker registration
- manifest.json defines app metadata and icons
- sw.js implements cache-first strategy for offline support
- petite-vue (4.1KB) loaded from CDN for minimal bundle size
- style.css embedded directly in index.html for simplicity

## High-Level Architecture

### Data Flow
1. **User Input** → Vue reactive state (petite-vue) → ComfyUI API request
2. **API Response** → WebSocket updates → Vue state updates → DOM updates
3. **CORS Handling**: Browser → CORS Proxy (Python/Cloudflare/iOS) → ComfyUI Server

### State Management
- All state in single Vue component (`AirComfyApp`)
- LocalStorage for persistent endpoint configuration
- WebSocket for real-time execution progress
- No external state management libraries (zero-dependency principle)

### Security Considerations
- CORS proxy required for browser-to-ComfyUI communication
- iOS app uses custom URL scheme to bypass CORS
- No authentication/authorization (assumes trusted local network)

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
- Currently loads PWA from http://localhost:8000 (change for production)
- CORSHandler enables direct ComfyUI API access without external proxy
- Test on simulator first before device deployment
- **Build Issues Fixed:**
  - DO NOT copy PWA files into iOS/AirComfy/ folder - causes duplicate file errors
  - PWA files should only exist in ../PWA/ folder and be referenced in Copy Bundle Resources
  - If you see "Multiple commands produce" errors, check for duplicate files in iOS/AirComfy/
  - ContentView.swift needs update to load bundled files: `Bundle.main.url(forResource: "index", withExtension: "html")`

## Sample Workflows

Example workflow files in repository:
- **SD15-basicT2I.json**: Stable Diffusion 1.5 text-to-image workflow
- **wan22-telltale-example.json**: Complex workflow example with multiple nodes