import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

# Configure MCP server for web fetching
mcp_fetch_server = MCPServerStdio(
    command="python",
    args=["-m", "mcp_server_fetch"]
)

# Configure Groq API
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

class ItineraryRequest(BaseModel):
    location: str
    category: str
    days: int = 3
    interests: Optional[List[str]] = None
    budget: Optional[str] = None

class Source(BaseModel):
    url: str
    trustworthiness_score: float
    relevance_score: float
    content_snippet: str

class ProcessedData(BaseModel):
    sources: List[Source]
    combined_context: str

class ItineraryGenerator:
    def __init__(self):
        self.agent = Agent(
            model="groq:llama-3.3-70b-versatile",
            mcp_servers=[mcp_fetch_server]
        )
    
    async def gather_data(self, request: ItineraryRequest) -> ProcessedData:
        """Gather and process data from the web based on the itinerary request."""
        # Create search queries based on the request
        search_queries = [
            f"best places to visit in {request.location} for {request.category} tourism",
            f"top attractions in {request.location} {request.category}",
            f"travel guide {request.location} {request.category}",
            f"{request.location} itinerary {request.days} days",
            f"{request.location} tourist spots {request.category}"
        ]
        
        if request.interests:
            for interest in request.interests:
                search_queries.append(f"{request.location} {interest} attractions")
        
        # Additional query for budget considerations if provided
        if request.budget:
            search_queries.append(f"{request.location} travel on {request.budget} budget")
        
        # Join queries for the MCP request
        queries_str = " AND ".join([f"({q})" for q in search_queries])
        
        async with self.agent.run_mcp_servers():
            # Use MCP to search and fetch relevant information
            prompt = f"""
            I need comprehensive travel information about {request.location} with a focus on {request.category} attractions.

            Please search the web for:
            {queries_str}

            For each source you find:
            1. Evaluate its trustworthiness (consider if it's from a reputable travel site, tourism board, etc.)
            2. Assess its relevance to the search query
            3. Extract key information about attractions, activities, logistics, and practical tips
            
            Return the information as a structured JSON with:
            - sources: array of objects with url, trustworthiness_score (0-1), relevance_score (0-1), and content_snippet
            - The content snippets should focus on practical information useful for creating a {request.days}-day itinerary
            """
            
            result = await self.agent.run(prompt)
            
            # Process the result to extract structured data
            try:
                # Try to parse as JSON first
                data = json.loads(result.output)
                sources = []
                for source in data.get("sources", []):
                    sources.append(Source(
                        url=source.get("url", ""),
                        trustworthiness_score=source.get("trustworthiness_score", 0.0),
                        relevance_score=source.get("relevance_score", 0.0),
                        content_snippet=source.get("content_snippet", "")
                    ))
            except json.JSONDecodeError:
                # If not valid JSON, use regex or string manipulation to extract urls and content
                # This is a simplified fallback
                sources = [
                    Source(
                        url="[Extracted from unstructured response]",
                        trustworthiness_score=0.7,
                        relevance_score=0.7,
                        content_snippet=result.output[:10000]  # Take first part of output as snippet
                    )
                ]
            
            # Sort sources by combined score of trustworthiness and relevance
            sources.sort(key=lambda x: (x.trustworthiness_score + x.relevance_score), reverse=True)
            
            # Create combined context from top sources
            top_sources = sources[:5]  # Limit to top 5 sources
            combined_context = f"# Travel Information for {request.location} - {request.category}\n\n"
            for idx, source in enumerate(top_sources, 1):
                combined_context += f"## Source {idx}: {source.url}\n"
                combined_context += f"Trustworthiness: {source.trustworthiness_score:.2f}, Relevance: {source.relevance_score:.2f}\n\n"
                combined_context += f"{source.content_snippet}\n\n---\n\n"
            
            return ProcessedData(sources=sources, combined_context=combined_context)
    
    async def generate_itinerary(self, 
                                request: ItineraryRequest, 
                                processed_data: ProcessedData) -> str:
        """Generate a detailed itinerary based on the processed data."""
        async with self.agent.run_mcp_servers():
            # Create prompt for itinerary generation
            interests_str = ", ".join(request.interests) if request.interests else "general tourism"
            budget_str = f" with a {request.budget} budget" if request.budget else ""
            
            prompt = f"""
            Based on the following travel research for {request.location} with a focus on {request.category} attractions, 
            create a detailed {request.days}-day itinerary for a traveler interested in {interests_str}{budget_str}.
            
            {processed_data.combined_context}
            
            # Instructions for Itinerary Creation:
            
            1. Create a day-by-day itinerary with logical geographical grouping of attractions
            2. For each day include:
               - Morning activities/attractions (including recommended start time)
               - Lunch recommendation (with cuisine type)
               - Afternoon activities/attractions
               - Evening activities and dinner recommendation
               - Approximate costs where available
               - Transportation tips between locations
            3. Start with a brief overview of {request.location} focusing on {request.category} aspects
            4. Include practical tips like best times to visit specific attractions, ticket information, dress codes, etc.
            5. Conclude with general travel tips specific to {request.location}
            
            Format the response as a well-structured markdown document with clear headings and bullet points.
            """
            
            result = await self.agent.run(prompt)
            return result.output

async def process_itinerary_request(request: ItineraryRequest) -> str:
    """Process an itinerary request and return the generated itinerary."""
    generator = ItineraryGenerator()
    
    # Step 1: Gather and process data
    processed_data = await generator.gather_data(request)
    
    # Step 2: Generate itinerary
    itinerary = await generator.generate_itinerary(request, processed_data)
    
    return itinerary

if __name__ == "__main__":
    # Example usage for testing
    async def test():
        request = ItineraryRequest(
            location="Kyoto",
            category="cultural",
            days=3,
            interests=["temples", "gardens", "traditional crafts"],
            budget="medium"
        )
        result = await process_itinerary_request(request)
        print(result)
    
    asyncio.run(test())
