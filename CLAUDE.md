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
python -m http.server 8000  # Local dev server
python proxy.py --port 8080 --comfyui http://192.168.11.132:8188  # CORS proxy
python test_aircomfy.py  # Selenium tests
```

### iOS Development
```bash
xcodebuild -project iOS/AirComfy.xcodeproj -scheme AirComfy -sdk iphonesimulator
```

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

### AirComfy Class (PWA/index.html:62-368)
- Manages server connection, workflow validation, and execution
- WebSocket handling for real-time progress
- LocalStorage for settings persistence
- Client ID generation for session tracking

### CORS Solutions
1. **Cloudflare Worker**: Deploy via worker.js, serves PWA and proxies API
2. **Python Proxy**: proxy.py provides local CORS proxy with WebSocket support
3. **iOS Native**: CORSHandler converts comfyproxy:// to http:// with CORS headers

### PWA Requirements
- HTTPS required for service worker registration
- manifest.json defines app metadata and icons
- sw.js implements cache-first strategy for offline support

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

## Deployment

### Cloudflare Worker
1. Edit COMFYUI_SERVER in worker.js
2. Deploy via dashboard or wrangler CLI
3. Access at https://your-worker.workers.dev

### Local ComfyUI Integration
1. Copy PWA files to ComfyUI web directory
2. Access at http://localhost:8188

### iOS App Store
1. Update bundle identifier and signing
2. Archive and upload via Xcode