# Travel Itinerary Generator

A FastAPI web application that generates personalized travel itineraries using AI. This service allows users to input their destination, travel style, duration, interests, and budget to receive a tailored day-by-day travel plan.

## Features

- **Personalized Itineraries**: Generate custom travel plans based on your preferences
- **Web Research**: Uses AI to search and synthesize information from various travel sources
- **Interactive Web Interface**: Easy-to-use form for submitting itinerary requests
- **Background Processing**: Handles requests asynchronously with status tracking
- **Result Caching**: Saves previously generated itineraries for faster responses

## Tech Stack

- **Backend**: FastAPI, Python
- **AI Integration**: Groq LLM API (llama-3.3-70b-versatile)
- **Data Fetching**: Custom MCP (Machine Callable Program) for web searches
- **Frontend**: HTML, CSS, JavaScript with Jinja2 templates

## Requirements

- Python 3.7+
- Groq API key

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/DhanushPrince/Travel_Itenary_Agent.git
cd travel-itinerary-generator
```

### 2. Set up environment

The easiest way to start is by using the startup script which checks dependencies and sets up the environment:

```bash
python start.py
```

Alternatively, you can set up manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p templates static cache

# Set up environment variables
cp .env.example .env  # Then edit .env with your API keys
```

### 3. Add your API keys

Edit the `.env` file and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the application

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload
```

The application will be available at http://localhost:8000

## Usage

1. Open your browser and go to http://localhost:8000
2. Fill in the itinerary request form:
   - **Location**: Where you want to travel (e.g., "Kyoto", "Paris", "New York")
   - **Category**: Type of travel (e.g., "cultural", "adventure", "relaxation")
   - **Days**: Duration of your trip (default: 3)
   - **Interests**: Specific activities or attractions you're interested in
   - **Budget**: Your spending level (e.g., "budget", "medium", "luxury")
3. Submit the form and wait for your itinerary to be generated
4. View your personalized day-by-day travel plan

## API Endpoints

- `GET /`: Main page with the itinerary request form
- `POST /generate-itinerary`: Submit an itinerary generation request
- `GET /itinerary-status/{request_id}`: Check the status of a pending request

## Project Structure

```
├── main.py                  # FastAPI application
├── mcp_itinerary_scraper.py # AI-based web scraping and itinerary generation
├── start.py                 # Environment setup and startup script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (API keys)
├── templates/               # HTML templates
│   └── index.html           # Main page template
├── static/                  # Static assets (CSS, JS, images)
└── cache/                   # Cached itineraries
```

## Development

### Adding New Features

To extend the functionality:

1. For new destination types or categories, update the search queries in `mcp_itinerary_scraper.py`
2. To modify the itinerary format, update the prompt in the `generate_itinerary` method
3. For UI changes, edit the templates in the `templates` directory

### Troubleshooting

- If you encounter MCP server errors, ensure you have the correct version of `pydantic_ai` installed
- For API key issues, verify your `.env` file is properly configured
- Check logs for detailed error information

## License

[MIT License](LICENSE)

## Acknowledgements

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI capabilities powered by [Groq](https://groq.com/) and [Pydantic AI](https://github.com/pydantic/pydantic-ai)
