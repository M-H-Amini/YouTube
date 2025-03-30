from agents import Agent, set_default_openai_key, Runner, trace
import asyncio
from dataclasses import dataclass

set_default_openai_key(open('api.txt').read().strip())

writer = Agent(
    name = "writer",
    instructions = (
        "You are a writer agent. You will be given a topic and you will write about it. "
        "You will receive feedback from a critic agent and you will revise your writing accordingly. "
    ),
    model = "o3-mini",
)

@dataclass
class Feedback:
    grammar_todo: str 
    content_todo: str
    style_todo: str
    grammar_score: int
    content_score: int
    style_score: int

critic = Agent(
    name = "critic",
    instructions = (
        "You are a critic agent. You will receive writing from the writer agent and you will provide feedback. "
        "Your feedback should be on the content, the grammar and the style of the writing. For each "
        "aspect, you should provide a brief todo list and an integer score from 0 to 10."
    ),
    model = "o3-mini",
    output_type = Feedback,
)

async def main():
    prompt = "Write an email to my professor, John, and ask him for a time so that I can see my exam paper."

    input_list = [{'role': 'user', 'content': prompt}]
    
    with trace('YouTube Writer'):
        while True:
            w_result = await Runner.run(
                writer,
                input_list,
            )
            print('Writer Output', w_result.final_output)
            input_list = w_result.to_input_list()

            c_result = await Runner.run(
                critic,
                input_list,
            )
            print('Critic Output', feedback:=c_result.final_output)
            input_list = c_result.to_input_list()

            thresh = 10
            if feedback.grammar_score >= thresh and feedback.content_score >= thresh and feedback.style_score >= thresh:
                print("Feedback is good enough, stopping...")
                break

            input('Press enter to continue...')

if __name__ == "__main__":
    asyncio.run(main())