from dataclasses import dataclass
from typing import Any
import date_tools


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


import json

def run_batch(invokations={}):
    batch_output = []

    for invokation in invokations:
        name = invokation["name"]
        args = json.loads(invokation["arguments"])

        tool_output = run_tool(name, args)

        batch_output.append({"tool_name": name, "output": tool_output})

    return batch_output


def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return date_tools.get_current_datetime(**tool_input)
    elif tool_name == "add_duration_to_datetime":
        return date_tools.add_duration_to_datetime(**tool_input)
    elif tool_name == "set_reminder":
        return date_tools.set_reminder(**tool_input)
    elif tool_name == "batch_tool":
        return run_batch(**tool_input)


def run_tools(message):
    tool_requests = [block for block in message.content if block.type == "tool_use"]
    tool_result_blocks = []

    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(tool_output),
                "is_error": False,
            }
        except Exception as e:
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": f"Error: {e}",
                "is_error": True,
            }

        tool_result_blocks.append(tool_result_block)

    return tool_result_blocks