from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench, mcp_server_tools
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import FunctionCallTermination
import asyncio 

def terminate():
    """Tool to terminate the chat."""
    pass

async def config():
    params = StdioServerParams(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-google-maps"],
        env={
            "GOOGLE_MAPS_API_KEY": open("api_maps.txt").read().strip(),
        }
    )

    model = OpenAIChatCompletionClient(
        model="o4-mini",
        api_key=open("api_openai.txt").read().strip(),
    )

    mcp_tools = await mcp_server_tools(server_params=params)
    
    agent = AssistantAgent(
        name="agent",
        system_message=open("agent.txt").read().strip(),
        model_client=model,
        reflect_on_tool_use=True,
        tools=(mcp_tools + [terminate])
    )

    team = RoundRobinGroupChat(
        participants=[agent],
        max_turns=10,
        termination_condition=FunctionCallTermination(function_name="terminate"),
    )
    return team

async def orchestrate(team, task):
    async for msg in team.run_stream(task=task):
        yield msg

async def main():
    team = await config()
    task = "Find a nice cafe near Downtown Ottawa."
    async for msg in orchestrate(team, task):
        print('---'* 20)
        print(msg)
    

if __name__ == "__main__":
    asyncio.run(main())