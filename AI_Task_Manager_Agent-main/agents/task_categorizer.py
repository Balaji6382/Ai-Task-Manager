from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from core.models import CategorizedTask
from core.config import OLLAMA_BASE_URL, LLM_MODEL

llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1)


def categorize_and_prioritize(task_input: str) -> CategorizedTask:
    parser = PydanticOutputParser(pydantic_object=CategorizedTask)

    system_prompt = (
        "You are an expert Task Analyzer.\n"
        "Extract category, priority, summary, tags (3-5), and estimated_duration.\n"
        "{format_instructions}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "Task: {task_input}")]
    ).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | llm | parser

    return chain.invoke({"task_input": task_input})
