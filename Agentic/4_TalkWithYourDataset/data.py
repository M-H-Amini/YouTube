from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
import asyncio 

async def teamConfig():
    model = OpenAIChatCompletionClient(
        model='o3-mini',
        api_key=open('api.txt').read().strip(),
    )

    developer = AssistantAgent(
        name='Developer',
        model_client=model,
        system_message=(
            "You are a code developer agent. You will be given a csv file named 'data.csv' in your working directory and "
            "a question about it. You can develope python code to answer the question. "
            "You should always begin with your plan to answer the question. Then you "
            "should write the code to answer the question. "
            "You should always write the code in a code block with language(python) specified. "
            "If you need several code blocks, make sure to write down one at a time. "
            "You will be working with a code executor agent. Once you have a code block, "
            "you must wait for the code executor agent to execute the code. If the code "
            "is executed successfully, you can continue. "
            "Use pandas to answer the question if possible. If a library is not installed, "
            "use pip in a shell code block (with shell specified) to install it. "
            "If the user asks you to provide a plot, you should use matplotlib to plot it and "
            'you should save it as a png file and you should exactly say "GENERATED:<filename>" (like "GENERATED:plot.png") in your message (not in your code). '
            'in a new line after you are sure that the code executor has executed the code and generated the plot successfully.'
            "Once you have the code execution results, you should provide the final answer and "
            'after that, you should exactly say "TERMINATE" to terminate the conversation. '
            ""
        ),
    )

    docker = DockerCommandLineCodeExecutor(
        work_dir='temp',
        image='amancevice/pandas:2.2.2'
    )

    executor = CodeExecutorAgent(
        name='CodeExecutor',
        code_executor=docker
    )

    team = RoundRobinGroupChat(
        participants=[developer, executor],
        termination_condition=TextMentionTermination('TERMINATE'),
        max_turns=20,
    )
    return team, docker

async def orchestrate(team, docker, task):
    await docker.start()
    async for msg in team.run_stream(task=task):
        if isinstance(msg, TextMessage):
            print(message:=f'{msg.source}: {msg.content}')
            yield message
        elif isinstance(msg, TaskResult):
            print(message:=f'Stop reason: {msg.stop_reason}')
            yield message

    await docker.stop()

async def main():
    task = 'My dataset is "data.csv". What are the columns of the dataset.'
    team, docker = await teamConfig()
    async for msg in orchestrate(team, docker, task):
        pass

if __name__ == '__main__':
    asyncio.run(main())

