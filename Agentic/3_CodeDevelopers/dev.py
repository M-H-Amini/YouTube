from autogen_agentchat.agents import CodeExecutorAgent, AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import asyncio 

async def teamConfig():
    model = OpenAIChatCompletionClient(
        model='o3-mini',
        api_key=open('api.txt').read().strip(),
    )

    docker = DockerCommandLineCodeExecutor(
        work_dir='temp',
        timeout=120,
    )

    code_developer = AssistantAgent(
        name='CodeDeveloper',
        model_client=model,
        system_message=(
            'You are a code developer agent working with a code executor agent. ' 
            'You will be given a task and you should '
            'write code to solve the task. Your codes should only be in Python or Shell.'
            'At the beginning, you should specify your plan to solve the task. '
            'Then, you should write the codes to solve the task. You should always '
            'write your code in a code block with language (Python or Shell) specified. '
            'You should write one code block at a time and then pass it to the code '
            'executor agent. If the code executor agent returned an error due to a library '
            'not being installed, you should use shell script code block to pip install it. '
            'Once the code executor agent executes the code and you have '
            'the results and the code was executed successfully, '
            'you should explain the code execution result. If an image has been generated, '
            'you should then exactly say "GENERATED:<filename>", like "GENERATED:plot.png" '
            'and in the end, exactly say "TERMINATE".'
            'Never say "TERMINATE" before the code executor agent has returned the execution '
            'results of all your codes and you are sure there was no error while executing them.'
        )
    )


    code_executor = CodeExecutorAgent(
        name='CodeExecutor',
        code_executor=docker,
    )

    team = RoundRobinGroupChat(
        participants=[code_developer, code_executor],
        termination_condition=TextMentionTermination('TERMINATE'),
        max_turns=40,
    )

    return team, docker

async def run(team, docker, task):
    await docker.start()
    async for message in team.run_stream(task=task):
        if isinstance(message, TaskResult):
            print(msg:=f'Stopping reason: {message.stop_reason}')
            yield msg
        else:
            print(msg:=f'{message.source}: {message.content}')
            yield msg
    
    print('Task completed!')
    await docker.stop()

async def main():
    # task = 'What is the 17th prime number?'
    # task = 'Sum the numbers from 1 to 100 and print the result.'
    task = (
        'Toss a fair coin, respectively, from 10 times to 1000 times, with steps of 10. ' 
        'Generate a beautiful plot of the ratio of heads in each experiment. '
        'Save the plot as "plot.png".'
    )
    team, docker = await teamConfig()
    async for message in run(team, docker, task):
        pass

if __name__ == '__main__':
    asyncio.run(main())


