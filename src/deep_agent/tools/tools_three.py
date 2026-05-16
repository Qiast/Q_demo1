# from langchain_core.tools import BaseTool
# from pydantic.v1 import BaseModel, Field
# from typing import Type
#
# # 继承BaseTool创建tool
#
# class AssetArgs(BaseModel):
#     date: str = Field(description = "The date the user wants to query.")
#
# class GetAssetTool(BaseTool):
#     name: str = "get_asset",
#     description: str = "Get the user's assets on the specified date.",
#     return_direct: bool = False,
#     args_schema: Type[BaseModel] = AssetArgs,
#     def _run(self, date: str) -> int:
#         try:
#             result = 1000000
#         except Exception as e:
#             print(e)
#             return 'No valid content'
#
# get_asset = GetAssetTool()