# Acronym Completion Platform

A web platform that automatically enriches acronym datasets with definitions, descriptions, and tags using AI.

## Features

- Upload CSV templates and acronym datasets
- Automatic enrichment using Grok API (primary) and Gemini API (fallback)
- Uses the free unlimited Gemini 1.0 Pro model for AI processing
- Export enriched data in CSV format
- Modern UI with Next.js and TailwindCSS
- FastAPI backend with robust error handling

## Tech Stack

- **Frontend**: Next.js + TailwindCSS
- **Backend**: FastAPI (Python)
- **AI Services**: 
  - Grok API (primary)
  - Gemini API (fallback) - Using the free unlimited Gemini 1.0 Pro model
- **File Handling**: pandas + FastAPI

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```env
   GEMINI_API_KEY_1=AIzaSyCZqWALaH7rxtl55oPps8njy6rG4SJRllo
   GEMINI_API_KEY_2=AIzaSyCEoUdTaxCqi4NZnLKwzPUOTnKitFBp53s
   GEMINI_API_KEY_3=AIzaSyBde09qqU4WrwVCjADP7CTskOBY6quPW-4
   GEMINI_API_KEY_4=AIzaSyBdB3wmrVQYH2BGmQwj25gExBrQuw_tgGA
   GEMINI_API_KEY_5=AIzaSyCUMBnz6aEjrMKmzKsUquIAstbOTV3iLq5
   GROK_API_KEY=your_grok_api_key
   NEXT_PUBLIC_API_URL=http://localhost:8000
   SECRET_KEY=your_secret_key
   ```

4. Start the servers:
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

## API Endpoints

- `POST /upload-template`: Upload CSV template
- `POST /upload-acronyms`: Upload acronyms CSV
- `POST /process-acronyms`: Process acronyms using AI
- `GET /download-results`: Download enriched CSV

## API Key Configuration

The platform supports multiple Gemini API keys for load balancing. You can configure API keys in two ways:

1. Single API key (default):
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

2. Multiple API keys for load balancing:
   ```
   GEMINI_API_KEY=your_primary_api_key_here
   GEMINI_API_KEY_1=your_secondary_api_key_here
   GEMINI_API_KEY_2=your_tertiary_api_key_here
   # Add more keys as needed
   ```

The system will automatically distribute requests across available API keys and handle rate limiting and quota management. When a key hits its quota limit, the system will automatically switch to another available key.

### Load Balancing Features

- Automatic distribution of requests across multiple API keys
- Error tracking and automatic key rotation on failures
- Quota management with automatic cooldown periods
- Usage-based load balancing to prevent overloading any single key
- Random jitter to prevent thundering herd problems

## AI Integration

The platform uses a dual-AI approach:
1. **Grok API** (Primary): Used as the main AI service for acronym enrichment
2. **Gemini API** (Fallback): Automatically used if Grok API fails, utilizing the free unlimited Gemini 1.0 Pro model

Both services use the same prompt template and return consistent JSON responses.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 