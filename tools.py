from utils import search_photos , custom_tavily_search
from langchain.tools import Tool
from langchain.tools.retriever import create_retriever_tool
from Config import all_retrievers , qwen
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor , LLMChainFilter


search_photos_tool = Tool(
    name="Photos_tool",
    func=search_photos,
    description="Tool used for photos , any photos queries you must use this tool"
)



compressor = LLMChainExtractor.from_llm(qwen)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=all_retrievers
)

retriever_tool = create_retriever_tool(retriever=compression_retriever , name="Turtles_Researcher" ,
                                        description="Answers information about the turtles , for any questions regarding the turtles you should use this tool! ")

# print(retriever_tool.invoke("What is the taxa classification of the green turtle?"))

tavily_search_tool = Tool(
    name="Tavily_Search",
    func= custom_tavily_search,
    description="Search the web using Tavily to find the relevant information"
)
