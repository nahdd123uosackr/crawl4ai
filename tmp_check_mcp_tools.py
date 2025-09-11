# temp script to import server and inspect MCP tools registration
import importlib, sys, asyncio, inspect

# ensure deploy/docker is on path
sys.path.insert(0, 'deploy')
sys.path.insert(0, 'deploy/docker')

import importlib

# Import server module under package path
mod = importlib.import_module('docker.server')
print('server module imported:', mod)
