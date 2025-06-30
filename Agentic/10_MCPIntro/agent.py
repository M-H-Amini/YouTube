from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
import time 
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

async def main():

    params = StdioServerParams(
        command="uvx",
        args=["mcp-server-time", "--local-timezone=America/New_York"]
    )

    model = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=open('api.txt').read().strip(),
    )

    async with McpWorkbench(server_params=params) as workbench:
        agent = AssistantAgent(
            name="Agent",
            system_message="You are a helpful assistant.",
            model_client=model,
            workbench=workbench,
        )

        task = "What time is it now in Tehran?"

        async for msg in agent.run_stream(task=task):
            print('--' * 20)
            print(msg)

if __name__ == "__main__":
    asyncio.run(main())