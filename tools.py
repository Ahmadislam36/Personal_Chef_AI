"""
tools.py

Contains all tools used by the Personal Chef Agent.
"""

import os
from dotenv import load_dotenv

from tavily import TavilyClient
from langchain.tools import tool

# ----------------------------------------------------
# Load Environment Variables
# ----------------------------------------------------

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# ----------------------------------------------------
# Supported cuisines
# ----------------------------------------------------

SUPPORTED_CUISINES = [
    "Pakistani",
    "Indian",
    "Chinese",
    "Italian"
]

# ----------------------------------------------------
# Web Search Tool
# ----------------------------------------------------

@tool
def web_search(query: str) -> str:
    """
    Search the web for recipes and cooking information.
    """

    results = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
    )

    return str(results)


# ----------------------------------------------------
# Ingredient Validator
# ----------------------------------------------------

@tool
def validate_ingredients(ingredients: str) -> str:
    """
    Clean and validate ingredient list.
    """

    cleaned = [
        ingredient.strip().lower()
        for ingredient in ingredients.split(",")
        if ingredient.strip()
    ]

    return ", ".join(cleaned)


# ----------------------------------------------------
# Cuisine Validator
# ----------------------------------------------------

@tool
def validate_cuisine(cuisine: str) -> str:
    """
    Check whether the requested cuisine is supported.
    """

    cuisine = cuisine.strip().capitalize()

    if cuisine in SUPPORTED_CUISINES:
        return f"{cuisine} cuisine is supported."

    return (
        "Sorry, I only support "
        "Pakistani, Indian, Chinese and Italian cuisine."
    )


# ----------------------------------------------------
# Nutrition Tool
# ----------------------------------------------------

@tool
def nutrition_estimator(recipe_name: str) -> str:
    """
    Estimate nutrition values.
    """

    return f"""
Estimated Nutrition for {recipe_name}

Calories : 450-650 kcal

Protein : 18-25 g

Carbohydrates : 35-55 g

Fat : 15-30 g

Fiber : 5-8 g

Sugar : 4-10 g

(Sample estimation)
"""