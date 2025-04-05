# Acronym Completion Platform

A web platform that automatically enriches acronym datasets with definitions, descriptions, and tags using AI.

## Features

- Upload CSV templates and acronym datasets
- Automatic enrichment using Grok API (primary) and Gemini API (fallback)
- Export enriched data in CSV format
- Modern UI with Next.js and TailwindCSS
- FastAPI backend with robust error handling

## Tech Stack

- **Frontend**: Next.js + TailwindCSS
- **Backend**: FastAPI (Python)
- **AI Services**: 
  - Grok API (primary)
  - Gemini API (fallback)
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
   Create a `.env` file in the backend directory with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   GROK_API_KEY=your_grok_api_key
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

## AI Integration

The platform uses a dual-AI approach:
1. **Grok API** (Primary): Used as the main AI service for acronym enrichment
2. **Gemini API** (Fallback): Automatically used if Grok API fails

Both services use the same prompt template and return consistent JSON responses.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 