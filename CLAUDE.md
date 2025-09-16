# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AirComfy is a minimal static Progressive Web App (PWA) designed to send workflows directly to a ComfyUI API. This project focuses on simplicity, offline functionality, and direct API integration without unnecessary complexity.

## Architecture

**Core Philosophy**: Minimal complexity, maximum functionality
- **Single Page Application**: All functionality consolidated in index.html
- **No Framework Dependencies**: Pure HTML/CSS/JavaScript implementation
- **Direct API Integration**: Uses native fetch API to communicate with ComfyUI endpoints
- **PWA Features**: Service Worker caching and offline capability

## File Structure

```
AirComfy/
├── index.html          # Main application interface and logic
├── manifest.json       # PWA configuration and metadata
├── sw.js              # Service Worker for caching and offline support
├── style.css          # Minimal responsive styling
└── icon-192.png       # PWA icon (192x192px minimum)
```

## Development Commands

Since this is a static PWA with no build process:

- **Development**: Open `index.html` in browser or use `python -m http.server 8000`
- **Testing**: Use browser developer tools to test PWA features
- **Deployment**: Copy all files to any web server or CDN

## ComfyUI API Integration

**Primary Endpoint**: `POST /prompt`
- Accepts JSON workflow data
- Returns prompt_id for tracking execution
- Requires client_id for WebSocket connection

**Additional Endpoints**:
- `GET /history/{prompt_id}` - Retrieve execution results
- `GET /view?filename={name}&subfolder={path}&type={type}` - Download generated images
- WebSocket connection for real-time progress updates

## Key Implementation Details

**Error Handling**: Unified try-catch wrapper for all network operations
**Offline Support**: Service Worker caches critical files for offline usage
**Mobile-First**: Responsive design optimized for mobile devices
**Validation**: JSON workflow validation before API submission
**CORS Handling**: ComfyUI doesn't support CORS headers - use proxy or serve PWA from same origin

## Code Conventions

- **No Comments**: Code should be self-documenting
- **Minimal Indentation**: Maximum 3 levels of nesting
- **Direct DOM Manipulation**: No jQuery or similar libraries
- **ES6+ Features**: Use modern JavaScript where supported
- **Security**: Never log or expose API keys or sensitive data

## Testing Strategy

- **Manual Testing**: Browser-based testing of core functionality
- **PWA Testing**: Use Chrome DevTools Lighthouse for PWA compliance
- **API Testing**: Test against local ComfyUI instance
- **Offline Testing**: Verify service worker caching behavior

## Deployment Notes

- **Static Hosting**: Can be deployed to GitHub Pages, Netlify, or any static host
- **HTTPS Required**: PWA features require secure connection
- **CORS Workarounds**: Since ComfyUI doesn't support CORS:
  - **Option 1**: Cloudflare Worker (recommended) - Free, global, zero-config
  - **Option 2**: Copy PWA files to ComfyUI's web directory
  - **Option 3**: Run simple proxy server (see proxy.py)
  - **Option 4**: Use nginx/apache proxy with CORS headers