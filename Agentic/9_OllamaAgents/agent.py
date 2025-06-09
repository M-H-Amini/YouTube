from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from pypdf import PdfReader
import asyncio 

def count_pdf_pages(pdf_file_path: str) -> int:
    """Counts the number of pages in a PDF file."""
    reader = PdfReader(pdf_file_path)
    return len(reader.pages)

def read_pdf_file(pdf_file_path: str) -> str:
    """Reads the content of a PDF file."""
    reader = PdfReader(pdf_file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

async def main():
    model = OllamaChatCompletionClient(model="qwen3:1.7b")
    # model = OpenAIChatCompletionClient(api_key=open('api.txt').read().strip(), model="gpt-4o")
    agent = AssistantAgent(
        name="summarizer",
        system_message="""You are a summarizer agent.
You will receive a pdf file and summarize its content in a concise manner.
Here's what you need to do:
1. Check the number of pages in the PDF file using the appropriate tool.
2. Call the appropriate tool to read the content of the PDF file.
3. After you have called the two tools and got their outputs, summarize the content of the PDF file in a concise manner. At the beginning of your summarization, include the number of pages in the PDF file.
4. Once you have the summary, exactly say "TERMINATE".
For example, if the user says "Summarize `a.pdf`, you should call `count_pdf_pages` and `read_pdf_file` tools to get the number of pages and the content of the PDF file respectively.
Then, use the outputs of these tools to create a summary like this:
"The PDF file has X pages. Here is the summary of its content: <summary> TERMINATE".
""",
    model_client=model,
    tools=[count_pdf_pages, read_pdf_file],
    reflect_on_tool_use=True,
    )

    team = RoundRobinGroupChat(
        participants=[agent],
        max_turns=3,
        termination_condition=TextMentionTermination("TERMINATE")
    )

    await Console(team.run_stream(task="Summarize `test.pdf` file."))


if __name__ == "__main__":
    asyncio.run(main())
    