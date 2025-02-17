import inspect
from llama_index.core.tools import FunctionTool
from api.services.ticketmaster_service import TicketmasterService
from typing import List, Optional


def create_ticketmaster_tools() -> List[FunctionTool]:
    """Create Ticketmaster-specific LlamaIndex tools automatically from TicketmasterService methods."""
    tools = []

    for name, method in inspect.getmembers(
        TicketmasterService, predicate=inspect.isfunction
    ):
        if not name.startswith("_"):  # Skip private methods
            # Add fields parameter to method signature
            def wrapped_method(*args, fields: Optional[List[str]] = None, **kwargs):
                return method(*args, fields=fields, **kwargs)

            wrapped_method.__doc__ = method.__doc__

            tool = FunctionTool.from_defaults(
                fn=wrapped_method,
                name=name,
                description=getattr(
                    method, "yaml_doc", f"Call {name} on Ticketmaster API"
                ),
            )
            tools.append(tool)

    return tools


# Create tools once at module level
ticketmaster_tools = create_ticketmaster_tools()
