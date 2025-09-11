# Unit-style test for attach_mcp route registration logic without importing server
from types import SimpleNamespace
import importlib, sys, importlib.machinery, importlib.util
mb_path = 'deploy/docker/mcp_bridge.py'
loader = importlib.machinery.SourceFileLoader('mcp_bridge_mod', mb_path)
spec = importlib.util.spec_from_loader(loader.name, loader)
mb = importlib.util.module_from_spec(spec)
loader.exec_module(mb)

# Create fake route objects
class FakeRoute:
    def __init__(self, path, endpoint, methods=None):
        self.path = path
        self.endpoint = endpoint
        self.methods = set(methods or {"GET"})

# Create fake endpoints with __mcp_kind__ when decorated
async def stream_handler():
    return 'stream'
stream_handler.__mcp_kind__ = 'tool'
stream_handler.__mcp_name__ = 'crawl_stream'

async def regular_handler():
    return 'ok'
regular_handler.__mcp_kind__ = 'tool'
regular_handler.__mcp_name__ = 'crawl'

# Fake app with routes
class FakeApp(SimpleNamespace):
    pass

app = FakeApp()
app.routes = [
    FakeRoute('/crawl/stream', stream_handler, methods={'POST'}),
    FakeRoute('/crawl', regular_handler, methods={'POST'})
]

# Call attach_mcp with base_url
try:
    mb.attach_mcp(app, base='/mcp', base_url='http://localhost:8000')
    print('attach_mcp completed')

    # We can't access the internal 'tools' closure directly, but we can test behavior by
    # creating a proxy via mb._make_http_proxy and ensure '/stream' check works.
    proxy = mb._make_http_proxy('http://localhost:8000', app.routes[0])
    print('proxy callable created for /crawl/stream')

    print('Done')
except Exception as e:
    import traceback
    print('attach_mcp raised:', e)
    traceback.print_exc()
