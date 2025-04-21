import streamlit as st
from data import teamConfig, orchestrate
import os 
import asyncio
import re

def showMessage(container, msg):
    with container:
        if msg.startswith('Developer'):
            with st.chat_message("ai"):
                st.markdown(msg)
            if filename:=getFileName(msg):
                st.image(os.path.join("temp", filename), caption=filename)
        elif msg.startswith('CodeExecutor'):
            with st.chat_message("Executor", avatar="🤖"):
                st.markdown(msg)
        elif msg.startswith('Stop reason'):
            with st.chat_message("user"):
                st.markdown(msg)
        

def getFileName(msg):
    match = re.search(r'GENERATED:([^\s]+\.png)', msg)
    if match:
        return match.group(1)
    return None

st.markdown("<h1 style='text-align: center;'>Talk with your Dataset! 🕵️📊</h1>", unsafe_allow_html=True)

file = st.file_uploader("Upload your CSV file", type=["csv"])

if file:
    with open(os.path.join("temp", 'data.csv'), "wb") as f:
        f.write(file.getbuffer())
    st.success("File uploaded successfully!")

if 'messages' not in st.session_state:
    st.session_state.messages = []

chat_container = st.container()

prompt = st.chat_input("Ask a question about your dataset!")

for msg in st.session_state.messages:
    showMessage(chat_container, msg)

if prompt:
    async def query():
        team, docker = await teamConfig()
        if 'team_state' in st.session_state:
            await team.load_state(st.session_state['team_state'])
        with st.spinner("Generating response..."):
            async for msg in orchestrate(team, docker, prompt):
                st.session_state.messages.append(msg)
                showMessage(chat_container, msg)
        st.session_state['team_state'] = await team.save_state()
                
    asyncio.run(query())
            
    