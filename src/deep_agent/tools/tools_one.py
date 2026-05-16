from langchain_core.tools import tool
from pydantic import BaseModel
from pydantic import Field

class GetUserRelativeArgs(BaseModel):
    relation: str = Field(description = "The relation of the user's relative.")

@tool(args_schema = GetUserRelativeArgs)
def get_user_relative(relation: str) -> str:
    # method2: relaton: Annotated[str, "The relation of the user's relative."]

    """Get the name of user's relative.

    Args:
        relation: The relation of the user's relative.

    Returns:
        The name of the user's relative.
    """
    result = ""
    match relation:
        case "son":
            result = "Elon Musk"
        case "maid":
            result = "Donald Trump"

    return result