import os
import sys

# --- WINDOWS DLL FIX FOR pywin32 / pywintypes ---
# This resolves "ModuleNotFoundError: No module named 'pywintypes'" on some Windows setups.
if os.name == 'nt':
    # 1. Use the official bootstrap if available
    try:
        import pywin32_bootstrap
    except ImportError:
        pass

    # 2. Manual search paths as fallback
    _venv_root = os.path.dirname(os.path.dirname(__file__))
    _pywin32_dll_path = os.path.join(
        _venv_root, 'Lib', 'site-packages', 'pywin32_system32')
    _win32_path = os.path.join(_venv_root, 'Lib', 'site-packages', 'win32')

    if os.path.exists(_pywin32_dll_path):
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(_pywin32_dll_path)
        os.environ["PATH"] = _pywin32_dll_path + \
            os.pathsep + os.environ["PATH"]

    if os.path.exists(_win32_path):
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(_win32_path)
        os.environ["PATH"] = _win32_path + os.pathsep + os.environ["PATH"]

# Now we can safely import mcp
try:
    import pywintypes
except ImportError:
    try:
        from win32 import pywintypes
    except ImportError:
        pass

import asyncio
import subprocess
import threading
import time
from typing import Any, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class StitchMCPClient:
    """
    A standalone MCP client to talk directly to the Stitch MCP server.
    This enables the application to be independent of Antigravity's manual tools.
    """

    def _log(self, message: str):
        try:
            with open("mcp_debug.log", "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
            print(f"DEBUG: {message}")
        except:
            pass

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("STITCH_API_KEY")
        self.session: Optional[ClientSession] = None
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_event_loop, daemon=True)
        self._thread.start()
        self._log(
            f"StitchMCPClient initialized with API Key present: {'Yes' if self.api_key else 'No'}")

    def _get_server_params(self):
        # Determine the absolute path to the stitch-mcp binary
        _wealth_agent_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))  # wealth_agent

        # Check for Google Credentials
        _creds_path = os.path.join(
            _wealth_agent_root, "google_credentials.json")
        has_creds = os.path.exists(_creds_path)

        if not self.api_key and not has_creds:
            self._log(
                "ERROR: Attempted to get server params without API Key or Google Credentials.")
            raise RuntimeError(
                "STITCH_API_KEY or google_credentials.json is missing. Archi requires authentication.")

        # Check in local node_modules first (wealth_agent/node_modules)

        # Check in local node_modules first (wealth_agent/node_modules)
        _local_mcp_bin = os.path.join(
            _wealth_agent_root, 'node_modules', '@_davideast', 'stitch-mcp', 'bin', 'stitch-mcp.js')

        # Check in parent node_modules (nxstep_site/node_modules) - Fallback
        _project_root = os.path.dirname(_wealth_agent_root)  # nxstep_site
        _parent_mcp_bin = os.path.join(
            _project_root, 'node_modules', '@_davideast', 'stitch-mcp', 'bin', 'stitch-mcp.js')

        if os.path.exists(_local_mcp_bin):
            _mcp_bin = _local_mcp_bin
        else:
            _mcp_bin = _parent_mcp_bin

        if not os.path.exists(_mcp_bin):
            # Fallback to npx if binary not found in local node_modules
            mcp_cmd = "npx.cmd" if os.name == 'nt' else "npx"
            mcp_args = ["-y", "@_davideast/stitch-mcp", "proxy"]
            self._log(
                f"Binary not found at {_mcp_bin}. Falling back to {mcp_cmd}")
        else:
            mcp_cmd = "node"
            mcp_args = [_mcp_bin, "proxy"]
            self._log(
                f"Found local binary at {_mcp_bin}. Using direct node execution.")

        self._log(f"Launching Stitch MCP with: {mcp_cmd} {' '.join(mcp_args)}")

        env_vars = {**os.environ}

        # Check for Google Credentials
        if has_creds:
            self._log(f"Found Google Credentials at {_creds_path}")
            env_vars["GOOGLE_APPLICATION_CREDENTIALS"] = _creds_path
            # Explicitly remove STITCH_API_KEY if it exists in the environment to avoid conflict
            if "STITCH_API_KEY" in env_vars:
                self._log(
                    "Removing STITCH_API_KEY from env to prioritize Google Credentials")
                del env_vars["STITCH_API_KEY"]
        elif self.api_key:
            env_vars["STITCH_API_KEY"] = self.api_key

        return StdioServerParameters(
            command=mcp_cmd,
            args=mcp_args,
            env=env_vars
        )

    def _run_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _connect(self):
        if self.session:
            return

        try:
            params = self._get_server_params()
            self._log(
                f"Entering stdio_client context with command: {params.command} {' '.join(params.args)}")
            self.ctx = stdio_client(params)
            self.read, self.write = await self.ctx.__aenter__()
            self._log("stdio_client context entered. Creating session...")
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            self._log("Session created. Initializing...")
            # Set a timeout for the initialization
            await asyncio.wait_for(self.session.initialize(), timeout=120)
            self._log("✅ MCP Connection Initialized successfully!")
        except asyncio.TimeoutError:
            self._log("❌ Connection failed: Timeout during initialization")
            self.session = None
            raise RuntimeError(
                "Timeout lors de l'initialisation du serveur Stitch.")
        except Exception as e:
            import traceback
            self._log(
                f"❌ Connection failed: {str(e)}\n{traceback.format_exc()}")
            self.session = None
            raise

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Synchronous wrapper for calling an MCP tool."""
        self._log(f"call_tool called for: {tool_name}")
        future = asyncio.run_coroutine_threadsafe(
            self._async_call_tool(tool_name, arguments),
            self._loop
        )
        try:
            # Increase timeout for generation tools
            timeout = 600 if "generate" in tool_name else 120
            return future.result(timeout=timeout)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._log(f"❌ call_tool failed: {repr(e)}")
            raise e

    async def _async_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        await self._connect()
        self._log(f"Sending request for tool: {tool_name}")
        result = await self.session.call_tool(tool_name, arguments)
        self._log(f"Response received for tool: {tool_name}")
        # Log a snippet of the response content for debugging
        content_str = str(result.content)[:500]
        self._log(f"Tool Response Content (snippet): {content_str}")
        return result.content

    def list_tools(self):
        """Returns the list of available tools from the Stitch MCP server."""
        self._log("list_tools called")
        future = asyncio.run_coroutine_threadsafe(
            self._async_list_tools(), self._loop)
        try:
            return future.result(timeout=60)
        except Exception as e:
            self._log(f"❌ list_tools failed: {str(e)}")
            raise

    async def _async_list_tools(self):
        await self._connect()
        self._log("Fetching tool list from session...")
        return await self.session.list_tools()


# Singleton instance for the app
_client_instance = None


def get_stitch_client(api_key: Optional[str] = None):
    global _client_instance

    # If a new key is provided, we should update the existing client or create a new one
    active_key = api_key or os.environ.get("STITCH_API_KEY")

    if _client_instance is None:
        _client_instance = StitchMCPClient(api_key=active_key)
    elif active_key and _client_instance.api_key != active_key:
        # Restart/Update if key changed
        _client_instance.api_key = active_key
        # We might need to reset the session here if we were already connected
        _client_instance.session = None

    return _client_instance
