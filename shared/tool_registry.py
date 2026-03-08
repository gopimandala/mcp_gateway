# tool_registry.py
class ToolRegistryService:
    """Base class for MCP services to expose available tools dynamically."""
    OPERATIONS = {}

    @classmethod
    def get_tools_list(cls):
        """Return all tools with name, description, method, and path."""
        return [
            {
                "name": k,
                "description": v.get("description", ""),
                "method": v.get("method", ""),
                "path": v.get("path", ""), # actual jira path
                "wrapper_path": v.get("wrapper_path", "")  # MCP wrapper endpoint
            }
            for k, v in cls.OPERATIONS.items()
        ]