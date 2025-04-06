from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import pandas as pd
import os
from typing import List, Optional
import json
from dotenv import load_dotenv
from ai_service import AIService
from grok_service import GrokService
from auth import (
    Token, User, authenticate_user, create_access_token, 
    get_current_active_user, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from monitoring import track_performance, track_api_call, get_performance_metrics, save_metrics_to_file
import numpy as np
import traceback

# Load environment variables
load_dotenv()

class ProcessingConfig:
    def __init__(self):
        self.llm = "gemini"  # Default to Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.grok_api_key = os.getenv("GROK_API_KEY", "")
        
        self.batch_size = 250  # Default batch size
        
        self.grade_filter = {
            "enabled": False,
            "single_grade": None,
            "grade_range": None
        }
        
        self.enrichment = {
            "enabled": True,
            "add_missing_definitions": True,
            "generate_descriptions": True,
            "suggest_tags": True,
            "use_web_search": True,
            "use_internal_kb": True
        }
        
        self.starting_point = {
            "enabled": False,
            "acronym": None
        }
        
        self.rate_limiting = {
            "enabled": True,
            "requests_per_minute": 60,
            "burst_size": 10,
            "max_retries": 3
        }
        
        self.output_format = {
            "include_definitions": True,
            "include_descriptions": True,
            "include_tags": True,
            "include_grade": True,
            "include_metadata": True
        }
        
        self.caching = {
            "enabled": True,
            "ttl_seconds": 3600
        }

    def update(self, config: dict):
        self.llm = config.get("selectedLLM", self.llm)
        # Only update API keys if they are provided in the config
        if "geminiApiKey" in config:
            self.gemini_api_key = config["geminiApiKey"]
            os.environ["GEMINI_API_KEY"] = self.gemini_api_key
        if "grokApiKey" in config:
            self.grok_api_key = config["grokApiKey"]
            os.environ["GROK_API_KEY"] = self.grok_api_key
        
        # Update processing config
        processing_config = config.get("processingConfig", {})
        self.batch_size = processing_config.get("batchSize", self.batch_size)
        
        # Update grade filter
        grade_filter = processing_config.get("gradeFilter", {})
        self.grade_filter["enabled"] = grade_filter.get("enabled", self.grade_filter["enabled"])
        self.grade_filter["single_grade"] = grade_filter.get("singleGrade", self.grade_filter["single_grade"])
        self.grade_filter["grade_range"] = grade_filter.get("gradeRange", self.grade_filter["grade_range"])
        
        # Update enrichment
        enrichment = processing_config.get("enrichment", {})
        self.enrichment["enabled"] = enrichment.get("enabled", self.enrichment["enabled"])
        self.enrichment["add_missing_definitions"] = enrichment.get("addMissingDefinitions", self.enrichment["add_missing_definitions"])
        self.enrichment["generate_descriptions"] = enrichment.get("generateDescriptions", self.enrichment["generate_descriptions"])
        self.enrichment["suggest_tags"] = enrichment.get("suggestTags", self.enrichment["suggest_tags"])
        self.enrichment["use_web_search"] = enrichment.get("useWebSearch", self.enrichment["use_web_search"])
        self.enrichment["use_internal_kb"] = enrichment.get("useInternalKb", self.enrichment["use_internal_kb"])
        
        # Update starting point
        starting_point = processing_config.get("startingPoint", {})
        self.starting_point["enabled"] = starting_point.get("enabled", self.starting_point["enabled"])
        self.starting_point["acronym"] = starting_point.get("acronym", self.starting_point["acronym"])
        
        # Update rate limiting
        rate_limiting = processing_config.get("rateLimiting", {})
        self.rate_limiting["enabled"] = rate_limiting.get("enabled", self.rate_limiting["enabled"])
        self.rate_limiting["requests_per_minute"] = rate_limiting.get("requestsPerMinute", self.rate_limiting["requests_per_minute"])
        self.rate_limiting["burst_size"] = rate_limiting.get("burstSize", self.rate_limiting["burst_size"])
        self.rate_limiting["max_retries"] = rate_limiting.get("maxRetries", self.rate_limiting["max_retries"])
        
        # Update output format
        output_format = processing_config.get("outputFormat", {})
        self.output_format["include_definitions"] = output_format.get("includeDefinitions", self.output_format["include_definitions"])
        self.output_format["include_descriptions"] = output_format.get("includeDescriptions", self.output_format["include_descriptions"])
        self.output_format["include_tags"] = output_format.get("includeTags", self.output_format["include_tags"])
        self.output_format["include_grade"] = output_format.get("includeGrade", self.output_format["include_grade"])
        self.output_format["include_metadata"] = output_format.get("includeMetadata", self.output_format["include_metadata"])
        
        # Update caching
        caching = processing_config.get("caching", {})
        self.caching["enabled"] = caching.get("enabled", self.caching["enabled"])
        self.caching["ttl_seconds"] = caching.get("ttlSeconds", self.caching["ttl_seconds"])

app = FastAPI(title="Acronym Completion Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI services
processing_config = ProcessingConfig()
gemini_service = AIService(config=processing_config)
grok_service = GrokService()

# Authentication endpoints
@app.post("/token", response_model=Token)
@track_api_call("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
@track_api_call("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/health")
@track_api_call("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/metrics")
@track_api_call("/metrics")
async def get_metrics(current_user: User = Depends(get_current_active_user)):
    """Get performance metrics"""
    save_metrics_to_file()
    return get_performance_metrics()

@app.post("/update-config")
@track_api_call("/update-config")
@track_performance
async def update_config(config: dict, current_user: User = Depends(get_current_active_user)):
    """Update processing configuration"""
    processing_config.update(config)
    return {"status": "success"}

@app.post("/upload-template")
@track_api_call("/upload-template")
@track_performance
async def upload_template(file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)):
    """Upload and validate the CSV template"""
    try:
        # Save the uploaded file
        file_path = "template.csv"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate the template file
        df = pd.read_csv(file_path)
        required_columns = ["acronym", "grade"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail="Template file must contain 'acronym' and 'grade' columns")
        
        return {"message": "Template file uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-acronyms")
@track_api_call("/upload-acronyms")
@track_performance
async def upload_acronyms(file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)):
    try:
        # Save the uploaded file
        file_path = f"acronyms.csv"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Read the CSV file
        df = pd.read_csv(file_path, header=None)
        
        # If no header row exists, add one and rename the first column to 'acronym'
        if len(df.columns) >= 1:
            df.columns = ['acronym'] + [f'col_{i}' for i in range(1, len(df.columns))]
        
        # Validate the file
        if 'acronym' not in df.columns:
            raise HTTPException(status_code=400, detail="File must contain an 'acronym' column")
        
        return {"message": "Acronyms file uploaded successfully"}
    except Exception as e:
        print(f"Error uploading acronyms: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to upload acronyms: {str(e)}")

@app.post("/process")
@track_api_call("/process")
@track_performance
async def process_files(current_user: User = Depends(get_current_active_user)):
    """Process acronyms using the configured AI service"""
    try:
        # Check if template and acronyms files exist
        if not os.path.exists("template.csv") or not os.path.exists("acronyms.csv"):
            raise HTTPException(status_code=400, detail="Template and acronyms files must be uploaded first")
        
        # Read the acronyms file
        df = pd.read_csv("acronyms.csv", header=None)
        acronyms = df[0].tolist()  # Assuming acronyms are in the first column
        
        # Process acronyms in batches
        results = []
        batch_size = processing_config.batch_size
        quota_exhausted = False
        
        for i in range(0, len(acronyms), batch_size):
            batch = acronyms[i:i + batch_size]
            batch_results = []
            
            for acronym in batch:
                try:
                    # Skip processing if quota is exhausted
                    if quota_exhausted:
                        batch_results.append({
                            "acronym": acronym,
                            "definition": "Processing skipped - API quota exhausted",
                            "enrichment": {"description": "Processing skipped - API quota exhausted", "tags": "quota_exhausted"}
                        })
                        continue
                    
                    # Get definition based on selected LLM
                    if processing_config.llm == "grok":
                        if not processing_config.grok_api_key:
                            print(f"Grok API key not set, falling back to Gemini for {acronym}")
                            try:
                                definition = await gemini_service.get_definition(acronym)
                            except Exception as e:
                                if "quota" in str(e).lower() or "429" in str(e):
                                    quota_exhausted = True
                                    definition = "Processing skipped - API quota exhausted"
                                else:
                                    definition = f"Error: {str(e)}"
                        else:
                            try:
                                definition = await grok_service.get_definition(acronym)
                            except Exception as e:
                                print(f"Error with Grok API for {acronym}, falling back to Gemini: {str(e)}")
                                try:
                                    definition = await gemini_service.get_definition(acronym)
                                except Exception as gemini_error:
                                    if "quota" in str(gemini_error).lower() or "429" in str(gemini_error):
                                        quota_exhausted = True
                                        definition = "Processing skipped - API quota exhausted"
                                    else:
                                        definition = f"Error: {str(gemini_error)}"
                    else:
                        try:
                            definition = await gemini_service.get_definition(acronym)
                        except Exception as e:
                            if "quota" in str(e).lower() or "429" in str(e):
                                quota_exhausted = True
                                definition = "Processing skipped - API quota exhausted"
                            else:
                                definition = f"Error: {str(e)}"
                    
                    # Enrich acronym if enabled and quota not exhausted
                    enrichment = None
                    if processing_config.enrichment["enabled"] and not quota_exhausted:
                        if processing_config.llm == "grok":
                            if not processing_config.grok_api_key:
                                print(f"Grok API key not set, skipping enrichment for {acronym}")
                                enrichment = {"description": "Enrichment disabled - Grok API key not set", "tags": "disabled"}
                            else:
                                try:
                                    enrichment = await grok_service.enrich_acronym(acronym, definition)
                                except Exception as e:
                                    print(f"Error with Grok API enrichment for {acronym}, skipping enrichment: {str(e)}")
                                    enrichment = {"description": f"Enrichment error: {str(e)}", "tags": "error"}
                        else:
                            try:
                                enrichment = await gemini_service.enrich_acronym(acronym, definition)
                            except Exception as e:
                                if "quota" in str(e).lower() or "429" in str(e):
                                    quota_exhausted = True
                                    enrichment = {"description": "Enrichment skipped - API quota exhausted", "tags": "quota_exhausted"}
                                else:
                                    enrichment = {"description": f"Enrichment error: {str(e)}", "tags": "error"}
                    elif quota_exhausted:
                        enrichment = {"description": "Enrichment skipped - API quota exhausted", "tags": "quota_exhausted"}
                    
                    batch_results.append({
                        "acronym": acronym,
                        "definition": definition,
                        "enrichment": enrichment
                    })
                except Exception as e:
                    print(f"Error processing acronym {acronym}: {str(e)}")
                    batch_results.append({
                        "acronym": acronym,
                        "definition": f"Error: {str(e)}",
                        "enrichment": None
                    })
            
            results.extend(batch_results)
            
            # If quota is exhausted, add a message to the results
            if quota_exhausted:
                results.append({
                    "acronym": "QUOTA_EXHAUSTED",
                    "definition": "API quota has been exhausted. Remaining acronyms will be skipped.",
                    "enrichment": {"description": "Processing stopped due to API quota exhaustion", "tags": "quota_exhausted"}
                })
                break
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-results")
@track_api_call("/download-results")
@track_performance
async def download_results(current_user: User = Depends(get_current_active_user)):
    """Download the enriched acronyms CSV"""
    try:
        if not os.path.exists("enriched_acronyms.csv"):
            raise HTTPException(status_code=404, detail="Results file not found")
        return FileResponse("enriched_acronyms.csv", filename="results.csv")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 