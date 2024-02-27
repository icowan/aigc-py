from typing import List, Literal

from fastapi import APIRouter, Depends
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.utils.function_calling import format_tool_to_openai_tool
from requests import Session
from langchain.agents import AgentExecutor, tool, ZeroShotAgent
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from typing_extensions import Annotated

from app.config.config import Config, get_config
from app.config.dependencies import get_token_header
from app.logger.logger import build_logger
from app.models.assistants import get_assistant_by_uuid, Tools
from app.models.base import get_db
from app.protocol.assistants_protocol import AssistantsChatCompletionsRequest, AssistantsChatCompletionsResponse

router = APIRouter(
    prefix="/assistants",
    tags=["assistants"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

logger = build_logger("assistants", "assistants.log")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant, but bad at calculating lengths of words. "
            "Talk with the user as normal. "
            "If they ask you to calculate the length of a word, use a tool",
        ),
        # Please note the ordering of the fields in the prompt!
        # The correct ordering is:
        # 1. user - the user's current input
        # 2. agent_scratchpad - the agent's working space for thinking and
        #    invoking tools to respond to the user's input.
        # If you change the ordering, the agent will not work correctly since
        # the messages will be shown to the underlying LLM in the wrong order.
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


@tool
def word_length(word: str) -> int:
    """Returns a counter word"""
    return len(word)


@tool
def favorite_animal(name: str) -> str:
    """Get the favorite animal of the person with the given name"""
    if name.lower().strip() == "eugene":
        return "cat"
    return "dog"


TOOL_MAPPING = {
    "word_length": word_length,
    "favorite_animal": favorite_animal,
}
KnownTool = Literal["word_length", "favorite_animal"]


def _create_agent_with_tools(llm: ChatOpenAI, requested_tools: List[Tools]) -> AgentExecutor:
    """Create an agent with custom tools."""
    tools = []

    for requested_tool in requested_tools:
        if requested_tool not in TOOL_MAPPING:
            raise ValueError(f"Unknown tool: {requested_tool}")
        tools.append(TOOL_MAPPING[requested_tool])

    if tools:
        llm_with_tools = llm.bind(
            tools=[format_tool_to_openai_tool(tool) for tool in tools]
        )
    else:
        llm_with_tools = llm

    agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True).with_config(
        {"run_name": "agent"}
    )
    return agent_executor


@router.post("/{assistantId}/chat/completions", tags=["assistants"])
async def chat_completions(assistantId: str, request: AssistantsChatCompletionsRequest, db: Session = Depends(get_db),
                           config: Config = Depends(get_config)):
    assistant = get_assistant_by_uuid(db, assistantId, tools=True)
    if not assistant:
        logger.warning(f"Assistant not found: {assistantId}", f"opanai_base_url: {config.openai_base_url}")
        return

    logger.info(
        f"Assistant found: {assistantId}, Assistant model name: {assistant.model_name}, config.openai_base_url: {config.openai_base_url}")

    for tool in assistant.tools:
        logger.info(f"Tool: {tool.name}")

    llm = ChatOpenAI(model=assistant.model_name, openai_api_base=config.openai_base_url,
                     openai_api_key=config.openai_api_key,
                     temperature=0, streaming=True)

    # TODO: 将tools组装成动态tools

    prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
    suffix = """Begin!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )


    agent_executor = _create_agent_with_tools(llm, assistant.tools)
    # response = agent_executor.run(request.messages)

    return AssistantsChatCompletionsResponse()
