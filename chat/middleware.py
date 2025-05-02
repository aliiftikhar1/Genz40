from channels.middleware import BaseMiddleware

class WebSocketCORSMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Allow all origins for WebSocket connections
        scope['cors_headers'] = [
            (b'Access-Control-Allow-Origin', b'*'),
            (b'Access-Control-Allow-Methods', b'GET,POST,OPTIONS'),
            (b'Access-Control-Allow-Headers', b'authorization,content-type'),
        ]
        return await super().__call__(scope, receive, send)