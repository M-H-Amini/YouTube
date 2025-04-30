from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage, ToolCallRequestEvent, ToolCallExecutionEvent
from autogen_core import CancellationToken
from autogen_agentchat.base._chat_agent import Response
import asyncio

async def getVideoTranscript(url: str) -> str:
    """Gets the url of a video and returns the title, description, and transcript."""
    yt = YouTube(url)
    title = yt.title
    description = yt.description
    video_id = url.split('v=')[1].split('&')[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ' '.join([item['text'] for item in transcript])
    res = f'Title: {title}\n\nDescription: {description}\n\nTranscript: {transcript_text}'
    return res

async def getVideoTranscriptWithTimeStamps(url: str) -> str:
    """Gets the url of a video and returns the title, description, and transcript with timestamps."""
    yt = YouTube(url)
    title = yt.title
    description = yt.description
    video_id = url.split('v=')[1].split('&')[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    res = f'Title: {title}\n\nDescription: {description}\n\nTranscript with timestamps:\n\n{transcript}'
    return res

def configAgent():
    model = OpenAIChatCompletionClient(
        model='o3-mini',
        api_key=open('api.txt').read().strip()
    )

    agent = AssistantAgent(
        name='YouTube_Video_Proxy',
        system_message=(
            "You are a helpful assistant. You will get the url of a YouTube video and "
            "the user will ask questions about that video. You can use the tools to answer "
            "the user's questions. If the answer to that question is not in the video, "
            "you should say that you don't know the answer. "
            "If the question is asking when a particular event is happening, you should use the `getVideoTranscriptWithTimeStamps` tool. "
            "Otherwise, you should use the `getVideoTranscript` tool. "
            "When you are reporting a time in the video, you should use the format 'at 1:23' or 'at 1:23:45'. "
        ),
        tools=[getVideoTranscript, getVideoTranscriptWithTimeStamps],
        reflect_on_tool_use=True,
        model_client=model,
    )
    return agent

async def askAgent(agent, url, query):
    task = f'This is the url of the video: {url}. {query}'
    async for msg in agent.on_messages_stream([TextMessage(source='user', content=task)], cancellation_token=CancellationToken()):
        print('--' * 20)
        if isinstance(msg, Response):
            print(message:=msg.chat_message.content)
            yield message
        else:
            print(message:=msg.to_text())
            yield msg

async def main(url, query):
    agent = configAgent()
    await askAgent(agent, url, query)
        

if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=9_PepvnqIfU&t=461s'
    query = 'Summarize the video in two sentences.'
    # query = 'Tell me all the times that he talks about Andy.'
    # query = 'Does he mention Lionel Messi?'
    res = asyncio.run(main(url, query))
