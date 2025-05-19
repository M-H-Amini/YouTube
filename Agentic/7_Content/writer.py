from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.base import TerminatedException, TerminationCondition
from autogen_agentchat.messages import StopMessage
from autogen_agentchat.base import TaskResult
from autogen_core import Component
from pydantic import BaseModel
import asyncio
from pydantic import BaseModel

class ContentFeedback(BaseModel):
    grammar_score: int
    clarity_score: int
    style_score: int
    to_do: str

class SEOFeedback(BaseModel):
    seo_score: int
    to_do: str

class ScoreTerminationConfig(BaseModel):
    min_score_thresh : int

class ScoreTerminationCondition(TerminationCondition, Component[ScoreTerminationConfig]):
    def __init__(self, min_score_thresh: int = 8):
        self.min_score_thresh = min_score_thresh
        self._terminated = False
        self.min_content_score = 0
        self.seo_score = 0

    @property
    def terminated(self) -> bool:
        return self._terminated
    
    async def __call__(self, messages) -> StopMessage | None:
        if self._terminated:
            raise TerminatedException("Termination condition has already been reached")
        for message in messages:
            if message.source == "content_critic_agent":
                self.min_content_score = min(
                    message.content.grammar_score,
                    message.content.clarity_score,
                    message.content.style_score
                )
            
            elif message.source == "seo_critic_agent":
                    self.seo_score = message.content.seo_score
            
        if self.min_content_score >= self.min_score_thresh and self.seo_score >= self.min_score_thresh:
            self._terminated = True
            return StopMessage(
                content=f"The minimum scores are greater than or equal to the threshold {self.min_score_thresh}!",
                source="ScoreTermination",
            )
        return None

    async def reset(self) -> None:
        self._terminated = False

    def _to_config(self) -> ScoreTerminationConfig:
        return ScoreTerminationConfig(min_score_thresh=self.min_score_thresh)

    @classmethod
    def _from_config(cls, config: ScoreTerminationConfig):
        return cls(
            min_score_thresh=config.min_score_thresh,
        )
    
def teamConfig(min_score_thresh: int = 8):
    model = OpenAIChatCompletionClient(
        model='o3-mini',
        api_key=open('api.txt').read().strip(),
    )

    writer_agent = AssistantAgent(
        name="writer_agent",
        description="A writer agent that writes content based on a given topic.",
        system_message=(
            "You are a writer agent. You will be given a topic and you need to write some content in markdown format about it. "
            "You will be collaborating with a content-critic agent and an SEO-critic agent. These agents "
            "will provide feedbacks and scores on your content. You should address their feedbacks and improve your content. "
            f"If both of the critic agents give you a minimum score of {min_score_thresh} in all of the scores, you should regenerate the content and "
            "then you should exactly say 'TERMINATE'"
        ),
        model_client=model
    )

    content_critic_agent = AssistantAgent(
        name="content_critic_agent",
        description="A content-critic agent that provides feedback on the content written by the writer agent.",
        system_message=(
            "You are a content-critic agent. You will be given a piece of text and you need to provide scores from 0 to 10 on "
            "the grammar, clarity, and style of the text. You should also provide a to-do list of improvements for the writer agent, "
            "to improve the text. You should never write the text yourself. Be as specific as possible. "
            f"If the minimum score of the text is {min_score_thresh} or above {min_score_thresh}, leave the to-do list empty. "
        ),
        model_client=model,
        output_content_type=ContentFeedback
    )

    seo_critic_agent = AssistantAgent(
        name="seo_critic_agent",
        description="An SEO-critic agent that provides feedback on the SEO of the content written by the writer agent.",
        system_message=(
            "You are an SEO-critic agent. You will be given a piece of text and you need to provide a single score from 0 to 10 "
            "on the SEO of the text. You should also provide a to-do list of improvements for the writer agent. "
            "You should never write the text yourself. Be as specific as possible. "
            f"If the score of the text is {min_score_thresh} or above {min_score_thresh}, leave the to-do list empty. "
        ),
        model_client=model,
        output_content_type=SEOFeedback
    )

    selector_prompt = """You are in a team of content generation agents. The following roles are available:
{roles}.
Read the following conversation. Then select the next role from {participants} to speak. Only return the role.

{history}

If a critic agent has some to-do list for the writer agent, the writer agent should address it in the next message and that same critic agent should review the writer agent's message afterwards.
Read the above conversation. Then select the next role from {participants} to speak. Only return the role.
"""
    termination = ScoreTerminationCondition(min_score_thresh) | MaxMessageTermination(15)

    team = SelectorGroupChat(
        participants=[writer_agent, content_critic_agent, seo_critic_agent],
        model_client=model,
        selector_prompt=selector_prompt,
        termination_condition=termination
    )
    return team

async def orchestrate(team, task):
    async for message in team.run_stream(task=task):
        if isinstance(message, TaskResult):
            print(msg:=f'**Termination**: {message.stop_reason}')
            yield msg
        else:
            print('--'*20)
            if message.source == "writer_agent":
                print(msg:=f'**Writer**: {message.content}')
                yield msg
            elif message.source == "content_critic_agent":
                print(msg:=f'**Content Critic**:\n\n **Grammar Score**: {message.content.grammar_score},\n\n**Clarity Score**: {message.content.clarity_score},\n\n **Style Score**: {message.content.style_score},\n\n **To Do**: {message.content.to_do}')
                yield msg
            elif message.source == "seo_critic_agent":
                print(msg:=f'**SEO Critic**:\n\n **SEO Score**: {message.content.seo_score},\n\n **To Do**: {message.content.to_do}')
                yield msg
            elif message.source == "user":
                print(msg:=f'**User**:\n\n{message.content}')
                yield msg
        

async def main():
    task = "Write a short paragraph about the importance of AI in modern technology. "
    team = teamConfig(min_score_thresh=8)
    async for message in orchestrate(team, task):
        pass
    

if __name__ == "__main__":
    asyncio.run(main())

