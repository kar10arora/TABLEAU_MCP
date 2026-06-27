from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

# Collect everything from fastmcp and its deep dependencies
datas, binaries, hiddenimports = collect_all('fastmcp')

# Collect all submodules that fastmcp.server needs
hiddenimports += collect_submodules('fastmcp.server')
hiddenimports += collect_submodules('mcp')
hiddenimports += collect_submodules('mcp.server')
hiddenimports += collect_submodules('starlette')
hiddenimports += collect_submodules('anyio')
hiddenimports += collect_submodules('httpx')
hiddenimports += collect_submodules('key_value')
hiddenimports += collect_submodules('key_value.aio')

# Copy metadata so package presence checks pass at runtime
datas += copy_metadata('fastmcp')
datas += copy_metadata('mcp')
datas += copy_metadata('starlette')
datas += copy_metadata('anyio')
datas += copy_metadata('httpx')
