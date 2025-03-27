import random
import json
import requests
from Config import REDIS_URL
from langchain.tools import tool
import threading
from langchain_community.chat_message_histories import RedisChatMessageHistory
from Config import tavily_tool
from duckduckgo_search import DDGS
from scrape_data import web_base_scraper
from pydantic import BaseModel , Field
from typing import Literal
from langchain.memory import ConversationBufferWindowMemory
# from langchain_community.chat_message_histories import (
#     PostgresChatMessageHistory,
# )
from PostgresLimited import LimitedPostgresChatMessageHistory


def prepare_content(output):
    if isinstance(output, dict):
        # Serialize dictionary into JSON format
        return json.dumps(output, indent=2)
    return str(output)


def get_taxa_id(query):
    base_url = "https://api.inaturalist.org/v1/taxa"

    params = {"q": query}
    
    response = requests.get(base_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json() 
    
    results = data["results"]
    if results :
        return results[0]["id"]

    return {"error": "Please provide a valid query"}


# @tool
# def search_photos(query , number_of_photos = 3 , page = 2):
#     """
#     Any query related to photos you must use this tool

#     Args:

#     query : the species name.
#     number_of_photos :  number of photos to search and return.
#     """
    
#     taxon_id = get_taxa_id(query)

#     base_url = "https://api.inaturalist.org/v1/observations"
    
#     params = {
#             "taxon_id": taxon_id,
#             "per_page": number_of_photos,
#             "page": page,
#         }
#     response = requests.get(base_url, params=params)
#     if response.status_code != 200:
#         print("Please Provide a valid query or species")
#         # print(f"Failed to fetch data for page {page}: {response.status_code}")

#     data = response.json()
    
#     results = data.get("results", [])
    
#     if not results:
#         print(f"No more results found on page {page}.")

#     photos2 = []
#     for obs in results:
#         photos = obs.get("photos", [])
#         for photo in photos:
#             image_url = photo.get("url")
#             if image_url:
#                 photos2.append(image_url.replace("square" , "original"))

#     if photos2:
#         sample_size = min(len(photos2), int(number_of_photos))
#         final_photos = random.sample(photos2 , sample_size)
#         return prepare_content({"photos":final_photos})
    

#     return {"error": "Please provide a valid query"}


# def get_taxa_id(query):
#     """
#     Retrieves the taxon ID for a given species name using the iNaturalist API.

#     This function queries the iNaturalist taxa API to find the taxon ID for a species.
#     The taxon ID is required to search for observations (e.g., photos) of the species.

#     Parameters:
#         query (str): The name of the species to search for (e.g., "Panthera tigris").

#     Returns:
#         int: The taxon ID of the species.

#     Raises:
#         HTTPError: If the API request fails (e.g., due to an invalid query or network issue).

#     Example:
#         >>> get_taxa_id("green turtle")
#         12345
#     """
#     base_url = "https://api.inaturalist.org/v1/taxa"

#     params = {"q": query}
    
#     response = requests.get(base_url, params=params, timeout=10)
#     response.raise_for_status()
#     data = response.json() 
    
#     results = data["results"]
#     if results :
#         return results[0]["id"]

#     return {"error": "Please provide a valid query"}


# @tool
# def search_photos(query: str, number_of_photos: int = 3, page: int = 2) -> dict:
#     """
#     Searches for photos of a given species using the iNaturalist API.

#     This tool retrieves photos of a species by first finding its taxon ID and then querying
#     the iNaturalist observations API for photos. It returns a list of image URLs.

#     Parameters:
#         query (str): The name of the species to search for (e.g., "Panthera tigris").
#         number_of_photos (int, optional): The number of photos to retrieve. Defaults to 3.
#         page (int, optional): The page number of results to fetch. Defaults to 2.

#     Returns:
#         dict: A dictionary containing a list of photo URLs under the key "photos".
#               Example: {"photos": ["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"]}

#     Raises:
#         HTTPError: If the API request fails (e.g., due to an invalid query or network issue).

#     Example:
#         >>> search_photos("green turtle", number_of_photos=2)
#         {"photos": ["https://inaturalist.org/photos/123.jpg", "https://inaturalist.org/photos/456.jpg"]}
#     """
#     taxon_id = get_taxa_id(query)

#     base_url = "https://api.inaturalist.org/v1/observations"
    
#     params = {
#         "taxon_id": taxon_id,
#         "per_page": number_of_photos,
#         "page": page,
#     }
#     response = requests.get(base_url, params=params)
#     if response.status_code != 200:
#         print("Please provide a valid query or species.")
#         return {"error": "Failed to fetch data from iNaturalist API."}

#     data = response.json()
#     results = data.get("results", [])
    
#     if not results:
#         print(f"No more results found on page {page}.")
#         return {"error": "No photos found for the given query."}

#     photos2 = []
#     for obs in results:
#         photos = obs.get("photos", [])
#         for photo in photos:
#             image_url = photo.get("url")
#             if image_url:
#                 photos2.append(image_url.replace("square", "original"))

#     if photos2:
#         sample_size = min(len(photos2), int(number_of_photos))
#         final_photos = random.sample(photos2, sample_size)
#         return prepare_content({"photos": final_photos})
    
#     return {"error": "No photos found for the given query."}


from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import OutputFixingParser

# Define structured output schema
class GraderOutput(BaseModel):
    verdict: Literal["Fully Relevant" , "Partially Relevant" , "Irrelevant"] = Field(..., description="How much does the answer relates to the question")
    needs_search: bool = Field(..., description="True if the answer is insufficient, otherwise False")
    justification: str = Field(..., description="Explanation of why the answer was graded this way")



@tool
def search_photos(query : str) -> list:
    """
        Any query related to photos you must use this tool

        Args:
        query : the species name.
    """

    max_img = random.randint(1, 9)  
    print(f"Searching for '{query}'")
    with DDGS() as ddgs:
        search_results = ddgs.images(keywords=query)
        image_data = list(search_results)
        image_urls = [item.get("image") for item in image_data[:max_img]]
        return prepare_content({"photos":image_urls})


def get_message_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(session_id, url=REDIS_URL)

def get_session_history(session_id: str, k=4):
    history = RedisChatMessageHistory(session_id, url=REDIS_URL)
    messages = history.messages
    if len(messages) > k:  # k pairs (human + AI)
        history.clear()
        for msg in messages[-k:]:  # Keep last k pairs
            history.add_message(msg)
    return history

def get_postgres_history(session_id: str):
    history = LimitedPostgresChatMessageHistory(
    connection_string="postgresql://postgres:mypassword@localhost/chat_history",
    session_id=session_id,
)   
    return history


def custom_tavily_search(query : str):
    search_results = tavily_tool.invoke(query)
    
    urls = [dic["url"] for dic in search_results]

    scrape_thread = threading.Thread(target=web_base_scraper, args=(urls,))

    scrape_thread.start()

    return "\n\n".join([f"Source: {dic['url']}\n{dic['content']}" for dic in search_results])


class BinaryGrade(BaseModel):
    binary_score : Literal["yes","no"] = Field(... , description="The binary score either the answer is relevant or not , the binary is a string yes or no")



# print(custom_tavily_search("what is the habitat of the green turtle"))