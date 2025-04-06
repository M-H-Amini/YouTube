from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination
import asyncio

async def teamConfig(topic):
    model = OpenAIChatCompletionClient(
        model='gpt-4o',
        api_key=open('api.txt').read().strip(),
    )

    host = AssistantAgent(
        name='Jane',
        model_client=model,
        system_message=(
            'You are Jane, the host of a debate between John, a supporter agent, '
            'and Jack, a critic agent. You will moderate the debate.'
            f' The topic of the debate is {topic}. '
            'At the beginning of each round, announce the round number. '
            'At the beginning of the third round, declare that it will be '
            'the last round. After the last round, thank the audience and exactly '
            'say "TERMINATE".'
        )
    )

    supporter = AssistantAgent(
        name='John',
        system_message=(
        'You are John, a supporter agent in a debate for the'
        f' topic {topic}. You will be debating against Jack, a critic agent.'
        ),
        model_client=model,
    )

    critic = AssistantAgent(
        name='Jack',
        system_message=(
        'You are Jack, a critic agent in a debate for the'
        f' topic {topic}. You will be debating against John, a supporter agent.'
        ),
        model_client=model,
    )

    team = RoundRobinGroupChat(
        participants=[host, supporter, critic],
        max_turns=20,
        termination_condition=TextMentionTermination(text="TERMINATE"),
    )

    return team

async def debate(team):
    async for message in team.run_stream(task="Start the debate!"):
        if isinstance(message, TaskResult):
            message = f'Stopping reason: {message.stop_reason}'
            yield message
        else:
            message = f'{message.source}: {message.content}'
            yield message

async def main():
    topic = "Shall US government ban TikTok?"
    team = await teamConfig(topic)
    async for message in debate(team):
        print('-' * 20)
        print(message)
        
if __name__ == '__main__':
    asyncio.run(main())