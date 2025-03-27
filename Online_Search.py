from Config import qwen
from scrape_data import web_base_scraper
from langchain_core.prompts import ChatPromptTemplate
from tools import tavily_search_tool
from langchain.agents import create_tool_calling_agent , AgentExecutor 
from langchain_core.runnables.history import RunnableWithMessageHistory
from utils import get_postgres_history

prompt = ChatPromptTemplate.from_messages([
  ("system", "You are a helpful assistant , you always answer using the search tool"
   "always respond like you are in a conservation , REMEBER DO NOT USE YOUR OWN KNOWLWDGE"
   "Do not make the user feel like that you are getting the answer from a context or Documents"),
  ("placeholder", "{chat_history}"),
  ("human", "{input}"),
  ("placeholder", "{agent_scratchpad}"),
])


tools = [tavily_search_tool]

agent = create_tool_calling_agent(qwen , tools , prompt)

search_agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True , return_intermediate_steps=True)

search_agent_with_message_history = RunnableWithMessageHistory(
    search_agent_executor,
    get_postgres_history , 
    input_messages_key="input",
    history_messages_key="chat_history"
)





# def online_search_agent(query : str):
#     search_prompt = PromptTemplate(
#     template="""You are a highly skilled Turtles Researcher assistant. You will be provided with multiple excerpts from trusted sources. Your task is to extract and infer the most relevant and precise answer to the given question using only the provided context. 

#     ### Important Instructions:
#     - The context contains partial readings from webpages and may not always state the answer explicitly. Your job is to synthesize the most relevant information available.
#     - If the answer is indirectly mentioned or requires minor inference (such as recognizing numerical ranges or summarizing scattered details), provide a well-formed answer based on the data.
#     - Do NOT make up any information. If the exact answer cannot be determined with high confidence, say: "The context does not provide a definitive answer."
#     - If multiple sources provide conflicting data, summarize the range of information accurately.

#     ### CONTEXT:
#     {context}

#     ### QUESTION:
#     {question}

#     ### ANSWER:
#     """,
#     input_variables=["context", "question"]  
#     )

#     search_results = tavily_tool.invoke(query)
#     print(search_results)

#     urls = [dic["url"] for dic in search_results]
    
#     answer_collections = [dic["content"] for dic in search_results]

#     context = f"""Source 1 : \n {answer_collections[0]} \n Source 2 : \n {answer_collections[1]} \n Source 3 : \n {answer_collections[2]} \n Source 4 : \n {answer_collections[3]} \n Source 5 : \n {answer_collections[4]}"""


#     print(f"Context is : {context}")
#     online_search_agent = search_prompt | qwen

#     print(online_search_agent.invoke({"context" : context , "question" : query}).content)
#     # scrape_thread = threading.Thread(target =web_base_scraper  , args =(urls,))

# online_search_agent("what is the hearing range of the flatback sea turtle?")