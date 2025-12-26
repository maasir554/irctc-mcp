from fastmcp import FastMCP

mcp = FastMCP("MY SERVER")


@mcp.tool
def greet(name: str) -> str:
    return "Hola Amigo, {name}!"

def main():
    mcp.run()


if __name__ == "__main__":
    main()
