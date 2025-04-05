# Acronym Completion Platform API Documentation

## Endpoints

### Health Check
```http
GET /health
```
Returns the health status of the API.

**Response**
```json
{
    "status": "healthy"
}
```

### Update Configuration
```http
POST /update-config
```
Updates the processing configuration.

**Request Body**
```json
{
    "selectedLLM": "gemini",
    "geminiApiKey": "your-api-key",
    "grokApiKey": "your-api-key",
    "processingBatchSize": 10,
    "gradePrompt": "Custom prompt for grade {grade}"
}
```

**Response**
```json
{
    "status": "success"
}
```

### Upload Template
```http
POST /upload-template
```
Uploads and validates a CSV template file.

**Request**
- Content-Type: multipart/form-data
- Body: file (CSV)

**Response**
```json
{
    "message": "Template file uploaded successfully"
}
```

### Upload Acronyms
```http
POST /upload-acronyms
```
Uploads and validates an acronyms CSV file.

**Request**
- Content-Type: multipart/form-data
- Body: file (CSV)

**Response**
```json
{
    "message": "Acronyms file uploaded successfully"
}
```

### Process Files
```http
POST /process
```
Processes the uploaded template and acronyms files using AI models.

**Request**
- Content-Type: multipart/form-data
- Body: 
  - template_file (CSV)
  - acronyms_file (CSV)

**Response**
```json
{
    "results": [
        {
            "acronym": "ABC",
            "definition": "AI-generated definition",
            "description": "",
            "tags": "",
            "grade": "3"
        }
    ]
}
```

### Download Results
```http
GET /download-results
```
Downloads the processed results as a CSV file.

**Response**
- Content-Type: text/csv
- Content-Disposition: attachment; filename="results.csv"

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "detail": "Error message describing the issue"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error message"
}
```

## File Formats

### Template CSV
Required columns:
- acronym: The acronym to process
- grade: The target grade level (1-5)

### Acronyms CSV
Required columns:
- acronym: The acronym to process

## Notes

- All file uploads must be in CSV format
- The API supports both Grok and Gemini AI models for processing
- Batch processing is configurable through the update-config endpoint
- Results are stored temporarily and can be downloaded through the download-results endpoint 