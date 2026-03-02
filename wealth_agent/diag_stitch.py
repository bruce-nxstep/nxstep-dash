import os
import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Diagnostic for Stitch MCP following the new direct-node path
async def main():
    api_key = os.environ.get("STITCH_API_KEY")
    if not api_key:
        print("❌ STITCH_API_KEY is missing from environment.")
        return

    print(f"Using API Key: {api_key[:8]}...")
    
    _src_root = os.path.dirname(os.path.abspath(__file__)) # wealth_agent
    _project_root = os.path.dirname(_src_root) # nxstep_site
    _mcp_bin = os.path.join(_project_root, 'node_modules', '@_davideast', 'stitch-mcp', 'bin', 'stitch-mcp.js')
    
    if not os.path.exists(_mcp_bin):
        print(f"❌ Binary NOT FOUND at: {_mcp_bin}")
        return

    print(f"✅ Found binary at: {_mcp_bin}")
    
    server_params = StdioServerParameters(
        command="node",
        args=[_mcp_bin],
        env={**os.environ, "STITCH_API_KEY": api_key}
    )
    
    print("\n--- Testing direct node execution ---")
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Connecting...")
                await asyncio.wait_for(session.initialize(), timeout=20)
                print("✅ Connection successful!")
                tools = await session.list_tools()
                print(f"Available tools: {[t.name for t in tools.tools]}")
                return True
    except asyncio.TimeoutError:
        print("⏳ Timeout: Server didn't respond to initialize.")
    except Exception as e:
        print(f"❌ Error during connection: {e}")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.environ["STITCH_API_KEY"] = sys.argv[1]
    asyncio.run(main())
