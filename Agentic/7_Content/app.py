import streamlit as st
import asyncio 
from writer import teamConfig, orchestrate

# --- New UI enhancements ---
st.set_page_config(
    page_title="Agentic Content Generation",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


# Sidebar for input controls
st.sidebar.title("⚙️ Controls")
min_thresh = st.sidebar.slider("Minimum score threshold", 0, 10, 9)

if 'messages' not in st.session_state:
    st.session_state.messages = []

def showMessages(chat):
    with chat:
        for message in st.session_state.messages:
            if message.startswith('**Writer**'):
                with st.chat_message("ai", avatar="images/writer.png"):
                    st.markdown(message)
            elif message.startswith('**Content Critic**'):
                with st.chat_message("ai", avatar="images/content.png"):
                    st.markdown(message)
            elif message.startswith('**SEO Critic**'):
                with st.chat_message("ai", avatar="images/seo.png"):
                    st.markdown(message)
            elif message.startswith('**User**'):
                with st.chat_message("user"):
                    st.markdown(message)
            elif message.startswith('**Termination**'):
                with st.chat_message("ai"):
                    st.markdown(message)   

# Main header
st.markdown("# 🚀 Agentic Content Generation Chatbot 🚀")
st.markdown("### Generate high-quality content with a team of expert agents 🤖🤖🤖")

# Styled chat wrapper
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
chat = st.container()
showMessages(chat)

# streamlined input prompt
prompt = st.chat_input(placeholder="Type your content request here…")
st.markdown('</div>', unsafe_allow_html=True)

if prompt:
    async def main():
        team = teamConfig(min_score_thresh=min_thresh)
        if 'team_state' in st.session_state:
            await team.load_state(st.session_state.team_state)

        with chat:
            async for message in orchestrate(team, prompt):
                st.session_state.messages.append(message)
                if message.startswith('**Writer**'):
                    with st.chat_message("ai", avatar="images/writer.png"):
                        st.markdown(message)
                elif message.startswith('**Content Critic**'):
                    with st.chat_message("ai", avatar="images/content.png"):
                        st.markdown(message)
                elif message.startswith('**SEO Critic**'):
                    with st.chat_message("ai", avatar="images/seo.png"):
                        st.markdown(message)
                elif message.startswith('**User**'):
                    with st.chat_message("user"):
                        st.markdown(message)
                elif message.startswith('**Termination**'):
                    with st.chat_message("ai"):
                        st.markdown(message)     
            
            st.session_state.team_state = await team.save_state()
    
    with st.spinner("Agents are heavily working..."):
        asyncio.run(main())
        st.success("Done!")
        st.balloons()

