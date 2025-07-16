import streamlit as st
from agent import orchestrate, config
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.messages import ToolCallExecutionEvent, ToolCallRequestEvent
import asyncio

st.title("📰 News Fact-Checking Agent 🤖✅")

chat = st.container()

task = st.chat_input("Enter your question about news or facts:")

if task:
    team = asyncio.run(config())
    async def run_agent(team, task):
        with chat:
            async for msg in orchestrate(team, task):
                print('---' * 20)
                print(type(msg))
                print(msg)
                if not isinstance(msg, TaskResult):
                    if msg.source == "user":
                        with st.chat_message("user"):
                            st.markdown(msg.content)
                    elif msg.source == "agent":
                        if isinstance(msg, ToolCallRequestEvent) or isinstance(msg, ToolCallExecutionEvent):
                            with st.expander("Tool Call"):
                                st.markdown(msg.content)
                        else:
                            with st.chat_message("assistant"):
                                st.markdown(msg.content)
    with st.spinner("Processing..."):
        asyncio.run(run_agent(team, task))
    st.success("Task completed successfully!")
                        
            