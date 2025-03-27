from langchain_core.prompts import ChatPromptTemplate
from Config import qwen , REDIS_URL
from tools import search_photos_tool , retriever_tool , tavily_search_tool
from langchain.agents import create_tool_calling_agent , AgentExecutor , create_react_agent
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub
from utils import get_message_history , get_session_history , get_postgres_history



# prompt = ChatPromptTemplate.from_messages([
#   ("system", "You are a helpful assistant  , DO NOT ANSWER FROM YOUR OWN KNOWLEDGE"
#    "always respond like you are in a conservation , REMEBER DO NOT USE YOUR OWN KNOWLWDGE" "Always use the tools you have"),
#   ("placeholder", "{chat_history}"),
#   ("human", "{input}"),
#   ("placeholder", "{agent_scratchpad}"),
# ])

prompt = ChatPromptTemplate.from_messages([
  ("system", """You are an AI assistant with access to two specialized tools:  

1. **Turtles_Researcher** – Provides information about turtles.  
2. **Photos_tool** – Handles queries related to images.  
3. **Tavily_Search** - Searches for the information online


### STRICT RULES:  
- **You are NOT ALLOWED to answer queries directly.**  
- **You MUST use one of the tools for every query.**  
- If a query is about turtles (including habitats, species, or conservation organizations)  except photos, use Turtles_Researcher.  
- If a query involves photos, use Photos_tool.  
- If a query is not related to turtles, respond with: "I do not have access to that information."  
- If the Turtles_Researcher didn't return any information , then say "I don't know ", don't try to answer yourself.
- Always fallback to the Tavily_Search tool if there is no answer provided from the Turtles_Researcher tool

### Examples:  
- *"Tell me about sea turtles."* → Use Turtles_Researcher  
- *"Show me a photo of a turtle."* → Use Photos_tool  
- *"Describe the habitat of leatherback turtles."* → Use Turtles_Researcher  

Strictly follow these rules and never generate answers yourself.
"""),
  ("placeholder", "{chat_history}"),
  ("human", "{input}"),
  ("placeholder", "{agent_scratchpad}"),
])



tools = [search_photos_tool , retriever_tool , tavily_search_tool]

agent = create_tool_calling_agent(qwen , tools , prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True , return_intermediate_steps=True , handle_parsing_errors=True)


agent_with_message_history = RunnableWithMessageHistory(
    agent_executor,
    # get_session_history,
    # get_message_history,
    get_postgres_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# answer = agent_with_message_history.invoke({"input": "can you show me one photo for it please?"} , config={"configurable" : {"session_id":"3awady"}})

# print(anwer["content"])
# print(answer["output"])


# AI agents ==> langchain , langgraph , Llamaindex , phidata
# [(ToolAgentAction(tool='Photos_tool', tool_input='turtle', log='\nInvoking: `Photos_tool` with `turtle`\n\n\n', 
#                   message_log=[AIMessageChunk(content='', additional_kwargs={}, 
#                                               response_metadata={'model': 'qwen2.5', 'created_at': '2025-03-05T13:54:18.2027675Z', 'done': True, 'done_reason': 'stop', 'total_duration': 627653600, 'load_duration': 12501800, 'prompt_eval_count': 268, 'prompt_eval_duration': 58000000, 'eval_count': 22, 'eval_duration': 554000000, 'message': Message(role='assistant', content='', images=None, tool_calls=None)}
#                                               ,id='run-efeb3b46-68ec-4c69-a1de-1016c63bc453', tool_calls=[{'name': 'Photos_tool', 'args': {'__arg1': 'turtle'}, 'id': '6f0fca50-adcb-433a-89ef-489687a55cc3', 'type': 'tool_call'}], usage_metadata={'input_tokens': 268, 'output_tokens': 22, 'total_tokens': 290}, 
#                                               tool_call_chunks=[{'name': 'Photos_tool', 'args': '{"__arg1": "turtle"}', 'id': '6f0fca50-adcb-433a-89ef-489687a55cc3', 'index': None, 'type': 'tool_call_chunk'}])],
#                                               tool_call_id='6f0fca50-adcb-433a-89ef-489687a55cc3'), 
#                                             '{\n  "photos": [\n    "https://www.thoughtco.com/thmb/BzglVchKrX8Ef1oAwTQln0DveoI=/5500x3667/filters:fill(auto,1)/sea-turtle--hawaii-110896831-596153023df78cdc68ba309b.jpg",\n    "https://mauikayakadventures.com/wp-content/uploads/P8290054Sunomen-.jpg",\n    "https://cdn.creatureandcoagency.com/uploads/2016/11/Turtle-facts-FB.jpg",\n    "http://2.bp.blogspot.com/-b6qT1WwvlEg/UM1Vqg41pFI/AAAAAAAABw0/AEiwBJj7K8k/s1600/Hawksbill+Turtle+Red+Sea.jpg",\n    "https://cdn.britannica.com/02/157202-050-26FD69B6/tortoise-ground-species-Galapagos-Islands-home-archipelago.jpg"\n  ]\n}')]

