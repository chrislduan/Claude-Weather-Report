from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    "Base Class for Agent Tools"

    name: str
    description: str
    input_schema: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        "convert tool to Claude API format"
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
    
    async def excecute (self, **kwargs) -> str:
        """Execute Tool with paramaters"""
        raise NotImplementedError(
            "Tool subclasses must implement execute method"
        )
    


batch_tool_schema = {
    "name": "batch_tool",
    "description": "Invoke multiple other tool calls simultaneously",
    "input_schema": {
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "description": "The tool calls to invoke",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the tool to invoke",
                        },
                        "arguments": {
                            "type": "string",
                            "description": "The arguments to the tool, encoded as a JSON string",
                        },
                    },
                    "required": ["name", "arguments"],
                },
            }
        },
        "required": ["invocations"],
    },
}
