import requests
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(env_path)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def search_web(query: str) -> str:
    """
    Executes a search query using Tavily API (or fallback).
    Returns a formatted string with results.
    """
    if not query:
        return "No hay consulta para buscar."

    if not TAVILY_API_KEY:
        return "Error: TAVILY_API_KEY not found in environment variables. Cannot search web."

    try:
        print(f"DEBUG: Executing Web Search: {query}")
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "max_results": 3
            },
            timeout=10
        )
        response.raise_for_status()
        results = response.json()
        
        # Extract relevant info
        answer = results.get("answer", "")
        search_results = results.get("results", [])
        
        formatted_results = f"Respuesta directa: {answer}\n\nDetalles adicionales:\n"
        for res in search_results:
            formatted_results += f"- {res.get('title')}: {res.get('content')}\nURL: {res.get('url')}\n"
            
        return formatted_results.strip()
        
    except Exception as e:
        print(f"[ERROR] Web Search Failed: {e}")
        return f"Error al buscar en internet: {str(e)}"
