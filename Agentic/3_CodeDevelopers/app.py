import streamlit as st 
import asyncio
import os
from dev import teamConfig, run

st.title('My Developer Agents! 🕵️🤖')

default_task = 'What is the 17th prime number?'
task = st.text_area('Task: ', default_task)
clicked = st.button('Run!')

chat = st.container()

if clicked:
    chat.empty()

    async def run_task(task):
        with st.spinner('Running...'):
            team, docker = await teamConfig()
            with chat:
                async for msg in run(team, docker, task):
                    if msg.startswith('CodeDeveloper'):
                        with st.chat_message('ai'):
                            st.markdown(msg)
                    elif msg.startswith('CodeExecutor'):
                        with st.chat_message('user'):
                            st.markdown(msg)
                    if 'GENERATED' in msg:
                        filename = msg.split('GENERATED:')[1].split()[0]
                        filepath = os.path.join('temp', filename)
                        if os.path.exists(filepath):
                            st.image(filepath)
                        else:
                            st.write(f'File {filename} not found.')
    asyncio.run(run_task(task))


    
        
