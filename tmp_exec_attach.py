# Extract attach_mcp function from mcp_bridge.py and execute in restricted context
import ast, inspect, importlib.util, textwrap

src = open('deploy/docker/mcp_bridge.py','r',encoding='utf-8').read()
mod = ast.parse(src)
for node in mod.body:
    if isinstance(node, ast.FunctionDef) and node.name in ('attach_mcp', '_make_http_proxy'):
        # Collect both nodes; we'll exec helper first then attach_mcp
        pass

fn_nodes = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in ('_make_http_proxy', 'attach_mcp')]
if not fn_nodes:
    raise SystemExit('required functions not found')
else:
    raise SystemExit('attach_mcp not found')

fn_src = '\n\n'.join(ast.get_source_segment(src, n) for n in fn_nodes)
# Prepare safe globals with minimal symbols
safe_globals = {
    '__builtins__': __builtins__,
    're': __import__('re'),
    'inspect': __import__('inspect'),
    'json': __import__('json'),
    'logging': __import__('logging'),
}
# Provide minimal stubs for types used inside attach_mcp
class DummyBaseModel:
    def model_json_schema(self):
        return {'type':'object'}

class DummyTool:
    def __init__(self, name=None, description=None, inputSchema=None):
        pass

# Create dummy mcp and related decorators used inside function
class DummyMCP:
    def list_tools(self):
        def deco(f):
            return f
        return deco
    def call_tool(self):
        def deco(f):
            return f
        return deco
    def list_resources(self):
        def deco(f):
            return f
        return deco
    def read_resource(self):
        def deco(f):
            return f
        return deco
    def list_resource_templates(self):
        def deco(f):
            return f
        return deco
    def get_capabilities(self, **kw):
        return {}

# Minimal NotificationOptions and InitializationOptions
class NotificationOptions: pass
class InitializationOptions:
    def __init__(self, **kwargs):
        pass

# Dummy Server that exposes decorators used
class DummyServer:
    def __init__(self, name):
        self.name = name
    def list_tools(self):
        return DummyMCP().list_tools()
    def call_tool(self):
        return DummyMCP().call_tool()
    def list_resources(self):
        return DummyMCP().list_resources()
    def read_resource(self):
        return DummyMCP().read_resource()
    def list_resource_templates(self):
        return DummyMCP().list_resource_templates()
    def get_capabilities(self, **kw):
        return {}

# Insert stubs
safe_globals.update({
    'BaseModel': DummyBaseModel,
    't': type('T', (), {'Tool': DummyTool, 'TextContent': lambda **kw: None, 'Resource': lambda **kw: None, 'ResourceTemplate': lambda **kw: None}),
    'Server': DummyServer,
    'NotificationOptions': NotificationOptions,
    'InitializationOptions': InitializationOptions,
})

# Dummy FastAPI for type annotations and minimal route API used
class FastAPI:
    pass
safe_globals['FastAPI'] = FastAPI

# Execute function definition in safe globals
exec(fn_src, safe_globals)
attach_mcp = safe_globals['attach_mcp']

# Build fake app and routes
class FakeRoute:
    def __init__(self, path, endpoint, methods=None):
        self.path = path
        self.endpoint = endpoint
        self.methods = set(methods or {'GET'})

async def stream_handler():
    pass
stream_handler.__mcp_kind__ = 'tool'
stream_handler.__mcp_name__ = 'crawl_stream'

async def regular_handler():
    pass
regular_handler.__mcp_kind__ = 'tool'
regular_handler.__mcp_name__ = 'crawl'

class FakeApp:
    def __init__(self):
        self.routes = [
            FakeRoute('/crawl/stream', stream_handler, methods={'POST'}),
            FakeRoute('/crawl', regular_handler, methods={'POST'})
        ]
        self.title = 'FakeApp'
        self.param_convertors = {}
    def mount(self, path, app=None):
        print('mounted', path)
    def websocket_route(self, path):
        def deco(fn):
            print('ws route', path)
            return fn
        return deco
    def get(self, path):
        def deco(fn):
            print('get route', path)
            return fn
        return deco

app = FakeApp()
# Call attach_mcp
attach_mcp(app, base='/mcp', base_url='http://localhost:8000')
print('attach_mcp executed in stubbed environment')
