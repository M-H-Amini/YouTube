from autogen import ConversableAgent

api_key = open('api.txt').read().strip()

llm_config = {'config_list': [
    {'model': 'gpt-4o', 'api_key': api_key}
]}

john = ConversableAgent(
    'John',
    system_message="You are John, a writer agent. You prepare a piece of text and pass it to Jack, a critic agent. You'll receive feedback from Jack. Once you have the feedback, you should revise and regenerate the text.",
    llm_config = llm_config,
    is_termination_msg = lambda msg: True if 'terminate' in msg['content'].lower() else False,
    human_input_mode = "NEVER",
)

jack = ConversableAgent(
    'Jack',
    system_message="You are Jack, a critic agent. You receive a piece of text from John, a writer agent. You should provide feedback to John for grammar, content and style. For each of these, briefly provide an explanation and a score from 0 to 10 and then suggest improvements. Be strict on your scores. Once all of these items are above 9, generate exactly 'terminate' at the end.",
    llm_config = llm_config,
)

initial_text = "hi prof. i don't like my score. i want to see my paper. Alex."

john.initiate_chat(jack, message=f"Here's my draft: {initial_text}", max_turns=5)

