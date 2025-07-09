import streamlit as st
import asyncio
from agent import config, orchestrate
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("Google Maps Agent")

container = st.container()

def show(container):
    for msg in st.session_state.messages:
        if msg.source == "user":
            with container:
                with st.chat_message("user"):
                    st.markdown(msg.content)
        elif msg.source == "agent":
            if isinstance(msg, TextMessage):
                with container:
                    with st.chat_message("assistant"):
                        st.markdown(msg.content)
            else:
                with container:
                    with st.expander("Tool Call"):
                        st.json(msg.content)

show(container)

task = st.chat_input("Enter your task here (e.g., 'Find a nice cafe near Downtown Ottawa.')")

if task:
    team = asyncio.run(config())

    async def run_agent(team, task):
        if 'team_state' in st.session_state:
            await team.load_state(st.session_state.team_state)

        async for msg in orchestrate(team, task):
            if not isinstance(msg, TaskResult):
                st.session_state.messages.append(msg)

                if msg.source == "user":
                    with container:
                        with st.chat_message("user"):
                            st.markdown(msg.content)
                elif msg.source == "agent":
                    if isinstance(msg, TextMessage):
                        with container:
                            with st.chat_message("assistant"):
                                st.markdown(msg.content)
                    else:
                        with container:
                            with st.expander("Tool Call"):
                                st.json(msg.content)
        st.session_state.team_state = await team.save_state()

    with st.spinner("Running agent..."):
        asyncio.run(run_agent(team, task))
    st.success("Task completed!")

            