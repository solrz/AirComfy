#!/usr/bin/env python3
"""
Simple CORS proxy for ComfyUI API access.
Usage: python proxy.py [--port 8080] [--comfyui http://localhost:8188]
"""

import argparse
import asyncio
import json
import aiohttp
from aiohttp import web, ClientSession
from aiohttp.web_ws import WSMsgType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComfyUIProxy:
    def __init__(self, comfyui_url="http://localhost:8188"):
        self.comfyui_url = comfyui_url.rstrip('/')
        self.websocket_connections = {}

    def add_cors_headers(self, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    async def handle_preflight(self, request):
        response = web.Response()
        return self.add_cors_headers(response)

    async def proxy_request(self, request):
        path = request.path
        method = request.method

        # Build target URL
        target_url = f"{self.comfyui_url}{path}"
        if request.query_string:
            target_url += f"?{request.query_string}"

        try:
            async with ClientSession() as session:
                # Forward headers (except host)
                headers = {k: v for k, v in request.headers.items()
                          if k.lower() not in ['host', 'origin']}

                # Handle request body
                data = None
                if method in ['POST', 'PUT', 'PATCH']:
                    data = await request.read()

                async with session.request(method, target_url,
                                         headers=headers, data=data) as resp:
                    # Read response
                    body = await resp.read()

                    # Create response
                    response = web.Response(
                        body=body,
                        status=resp.status,
                        headers=dict(resp.headers)
                    )

                    return self.add_cors_headers(response)

        except Exception as e:
            logger.error(f"Proxy error: {e}")
            response = web.json_response(
                {'error': f'Proxy failed: {str(e)}'},
                status=500
            )
            return self.add_cors_headers(response)

    async def handle_websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        client_id = request.query.get('clientId', 'unknown')
        logger.info(f"WebSocket connection from client {client_id}")

        # Connect to ComfyUI WebSocket
        try:
            comfyui_ws_url = self.comfyui_url.replace('http', 'ws') + f"/ws?clientId={client_id}"

            async with ClientSession() as session:
                async with session.ws_connect(comfyui_ws_url) as comfyui_ws:
                    # Store connections
                    self.websocket_connections[client_id] = (ws, comfyui_ws)

                    # Forward messages both ways
                    async def forward_to_client():
                        async for msg in comfyui_ws:
                            if msg.type == WSMsgType.TEXT:
                                await ws.send_str(msg.data)
                            elif msg.type == WSMsgType.BINARY:
                                await ws.send_bytes(msg.data)
                            elif msg.type == WSMsgType.ERROR:
                                logger.error(f'ComfyUI WS error: {comfyui_ws.exception()}')
                                break

                    async def forward_to_comfyui():
                        async for msg in ws:
                            if msg.type == WSMsgType.TEXT:
                                await comfyui_ws.send_str(msg.data)
                            elif msg.type == WSMsgType.BINARY:
                                await comfyui_ws.send_bytes(msg.data)
                            elif msg.type == WSMsgType.ERROR:
                                logger.error(f'Client WS error: {ws.exception()}')
                                break

                    # Run both forwarding tasks concurrently
                    await asyncio.gather(
                        forward_to_client(),
                        forward_to_comfyui(),
                        return_exceptions=True
                    )

        except Exception as e:
            logger.error(f"WebSocket proxy error: {e}")
        finally:
            # Clean up
            if client_id in self.websocket_connections:
                del self.websocket_connections[client_id]
            logger.info(f"WebSocket connection closed for client {client_id}")

        return ws

    async def serve_static(self, request):
        """Serve static PWA files"""
        file_path = request.path.lstrip('/')
        if file_path == '' or file_path == '/':
            file_path = 'index.html'

        static_files = {
            'index.html': 'text/html',
            'style.css': 'text/css',
            'manifest.json': 'application/json',
            'sw.js': 'application/javascript',
            'icon-192.png': 'image/png'
        }

        if file_path in static_files:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                response = web.Response(
                    body=content,
                    content_type=static_files[file_path]
                )
                return self.add_cors_headers(response)
            except FileNotFoundError:
                pass

        # If not a static file, proxy to ComfyUI
        return await self.proxy_request(request)

def create_app(comfyui_url):
    proxy = ComfyUIProxy(comfyui_url)
    app = web.Application()

    # WebSocket route
    app.router.add_get('/ws', proxy.handle_websocket)

    # CORS preflight
    app.router.add_route('OPTIONS', '/{path:.*}', proxy.handle_preflight)

    # All other routes (static files + API proxy)
    app.router.add_route('*', '/{path:.*}', proxy.serve_static)

    return app

def main():
    parser = argparse.ArgumentParser(description='ComfyUI CORS Proxy')
    parser.add_argument('--port', type=int, default=8080,
                       help='Proxy server port (default: 8080)')
    parser.add_argument('--comfyui', default='http://localhost:8188',
                       help='ComfyUI server URL (default: http://localhost:8188)')

    args = parser.parse_args()

    app = create_app(args.comfyui)

    logger.info(f"Starting CORS proxy on port {args.port}")
    logger.info(f"Proxying to ComfyUI at {args.comfyui}")
    logger.info(f"Open http://localhost:{args.port} in your browser")

    web.run_app(app, host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    main()