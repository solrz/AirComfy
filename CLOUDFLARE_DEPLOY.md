# Cloudflare Worker Deployment Guide

Deploy AirComfy PWA using Cloudflare Workers for free, global CORS proxy.

## Quick Setup

1. **Edit worker.js**:
   ```javascript
   const COMFYUI_SERVER = 'http://your-comfyui-server:8188'; // Change to your ComfyUI URL

   // Optional: Whitelist specific domains (empty array = allow all)
   const ALLOWED_ORIGINS = [
     'https://yourdomain.com',
     'https://www.yourdomain.com',
     'http://localhost:3000',  // For local development
   ];
   ```

2. **Deploy via Cloudflare Dashboard**:
   - Go to [dash.cloudflare.com](https://dash.cloudflare.com)
   - Workers & Pages → Create Application → Create Worker
   - Replace default code with `worker.js` content
   - Deploy

3. **Access your PWA**:
   - Visit your worker URL: `https://your-worker.your-subdomain.workers.dev`
   - Leave "Server URL" empty to use proxy automatically
   - If using domain whitelist, ensure your domain is in `ALLOWED_ORIGINS`

## CLI Deployment (Alternative)

1. **Install Wrangler**:
   ```bash
   npm install -g wrangler
   wrangler auth
   ```

2. **Create wrangler.toml**:
   ```toml
   name = "aircomfy-proxy"
   compatibility_date = "2023-12-01"
   main = "worker.js"
   ```

3. **Deploy**:
   ```bash
   wrangler deploy
   ```

## Features

- ✅ **Free**: Cloudflare Workers free tier (100k requests/day)
- ✅ **Global CDN**: Fast worldwide access
- ✅ **CORS Handling**: Automatic CORS headers for all requests
- ✅ **WebSocket Proxy**: Real-time progress updates work
- ✅ **Static Hosting**: Serves PWA files directly from Worker
- ✅ **Zero Config**: Users just visit the Worker URL

## How It Works

The Worker acts as a smart proxy:
- **Static files** (`/`, `/style.css`, etc.) → Serves PWA from Worker
- **API calls** (`/prompt`, `/history`, etc.) → Proxies to your ComfyUI server
- **WebSocket** (`/ws`) → Proxies WebSocket connection with CORS
- **Everything else** → Serves index.html (SPA routing)

## Security Notes

- **ComfyUI server URL** is hardcoded in Worker (not exposed to clients)
- **Domain Whitelisting**: Set `ALLOWED_ORIGINS` to restrict which domains can use the proxy
- **API Endpoint Filtering**: Only specific endpoints (`/prompt`, `/history`, etc.) are proxied
- **CORS headers** added automatically with origin validation
- **Static Files**: Always served regardless of origin (PWA hosting)
- **403 Forbidden**: API requests from non-whitelisted origins are blocked

## Limitations

- **Request Size**: 100MB limit per request
- **Execution Time**: 10 seconds per request (sufficient for ComfyUI API)
- **WebSocket**: 10 second connection limit on free tier
- **Private Networks**: Worker can't access local IPs directly

## For Local ComfyUI Access

If your ComfyUI is on a local network, you need a tunnel:

```bash
# Option 1: Cloudflare Tunnel
cloudflared tunnel --hello-world

# Option 2: ngrok
ngrok http 8188

# Then update COMFYUI_SERVER in worker.js to the tunnel URL
```