from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",	  },
)

from langchain.agents import AgentType, initialize_agent
from langchain_ollama import ChatOllama
import asyncio
from playwright.async_api import async_playwright


import asyncio
from playwright.async_api import async_playwright
from langchain.agents import AgentType, initialize_agent
from langchain_ollama import ChatOllama

async def main():
    # Initialize the language model
    llm = ChatOllama(model="qwen2.5", temperature=0)

    # Manually create the async Playwright browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create the toolkit with the browser
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        tools = toolkit.get_tools()

        # Organize tools by name (optional, if you need specific tools later)
        tools_by_name = {tool.name: tool for tool in tools}

        # Initialize the agent
        agent_chain = initialize_agent(
            tools,
            llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

        # Run the agent asynchronously
        result = await agent_chain.arun("What kind of data does hycom.org provides , is it about turtles?")
        print(result)

        # Clean up: close the browser
        await browser.close()

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())