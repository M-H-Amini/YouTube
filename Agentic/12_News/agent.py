from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import mcp_server_tools, StdioServerParams
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import FunctionCallTermination
from autogen_core.model_context import UnboundedChatCompletionContext
from autogen_core._types import FunctionCall
from autogen_core.models._types import FunctionExecutionResult
import asyncio
from copy import deepcopy

class MHContext(UnboundedChatCompletionContext):
    async def get_messages(self):
        message = await super().get_messages()
        result = deepcopy(message)
        indices_func_call = [i for i, msg in enumerate(message) if isinstance(msg.content, list) and isinstance(msg.content[0], FunctionCall)]
        indices_func_result = [i for i, msg in enumerate(message) if isinstance(msg.content, list) and isinstance(msg.content[0], FunctionExecutionResult)]
        indices = sorted(indices_func_call[:-1] + indices_func_result[:-1])
        for i in reversed(indices):
            result.pop(i)
        return result

def terminate():
    """ Terminate the conversation (operation) by the agent """
    pass


async def config():
    params = StdioServerParams(
        command='npx',
        args=[
        "-y",
        "mcp-remote",
        f"https://mcp.tavily.com/mcp/?tavilyApiKey={open('api_tavily.txt').read().strip()}"
        ]
    )

    mcp_tools = await mcp_server_tools(server_params=params)

    model = OpenAIChatCompletionClient(
        model='gpt-4.1',
        api_key=open('api_openai.txt').read().strip(),
    )

    agent = AssistantAgent(
        name='agent',
        system_message=open('agent.txt').read().strip(),
        model_client=model,
        tools=(mcp_tools + [terminate]),
        reflect_on_tool_use=True,
        model_context=MHContext()
    )

    team = RoundRobinGroupChat(
        participants=[agent],
        max_turns=10,
        termination_condition=FunctionCallTermination(function_name='terminate')
    )

    return team

async def orchestrate(team, task):
    async for msg in team.run_stream(task=task):
        yield msg

async def main():
    team = await config()
    task = "Is Lionel Messi 25 years old on 2025?"
    async for msg in orchestrate(team, task):
        print('---' * 25)
        print(msg)

if __name__ == '__main__':
    asyncio.run(main())



