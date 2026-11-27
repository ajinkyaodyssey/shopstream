"""List every endpoint described in an OpenAPI spec.

Usage:
    python3 tools/list_endpoints.py <URL of openapi.json>
Example:
    python3 tools/list_endpoints.py https://petstore3.swagger.io/api/v3/openapi.json
"""
import json
import sys
import urllib.request

# The HTTP methods an OpenAPI "path item" can contain.
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def load_spec(url):
    """Download the spec and turn the JSON text into a Python dict."""
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.load(response)


def list_endpoints(spec):
    """Return a sorted list of (path, METHOD, summary) tuples."""
    rows = []
    # spec["paths"] looks like: {"/products": {"get": {...}, "post": {...}}}
    for path, path_item in spec.get("paths", {}).items():
        for method, details in path_item.items():
            # Skip keys such as "parameters" that are not HTTP methods.
            if method.lower() in HTTP_METHODS:
                rows.append((path, method.upper(), details.get("summary", "")))
    return sorted(rows)


def main():
    # sys.argv[0] is the script name, sys.argv[1] is the URL you typed.
    if len(sys.argv) != 2:
        print("Usage: python3 tools/list_endpoints.py <openapi.json URL>")
        sys.exit(1)  # a non-zero exit code means "something went wrong"

    spec = load_spec(sys.argv[1])
    print("API:", spec.get("info", {}).get("title", "unknown"))
    for path, method, summary in list_endpoints(spec):
        print(f"{method:7} {path:35} {summary}")


# Run main() only when this file is run directly, not when it is imported.
if __name__ == "__main__":
    main()
