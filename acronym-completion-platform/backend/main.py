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

class ProcessingConfig:
    def __init__(self):
        self.llm = "gemini"
        # Load API keys from environment variables
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.grok_api_key = os.getenv("GROK_API_KEY", "")
        self.batch_size = 25  # Default batch size
        self.grade_prompt = "Please provide a clear and concise definition for this acronym, suitable for grade {grade} students."
        self.grade_filter = {
            "enabled": False,
            "single_grade": None,
            "grade_range": None
        }
        self.enrichment = {
            "enabled": True,  # Default to enabled
            "add_missing_definitions": True,
            "generate_descriptions": True,
            "suggest_tags": True,
            "use_web_search": False,
            "use_internal_kb": True
        }
        self.starting_point = {
            "enabled": False,
            "acronym": None
        }
        self.rate_limiting = {
            "enabled": True,
            "requests_per_second": 0.5,  # 1 request per 2 seconds
            "burst_size": 1,
            "max_retries": 3
        }
        self.output_format = {
            "include_definitions": True,
            "include_descriptions": True,
            "include_tags": True,
            "include_grade": True,
            "include_metadata": False
        }
        self.caching = {
            "enabled": True,
            "ttl_seconds": 86400  # 24 hours
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
        self.rate_limiting["requests_per_second"] = rate_limiting.get("requestsPerSecond", self.rate_limiting["requests_per_second"])
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
        
        self.grade_prompt = config.get("gradePrompt", self.grade_prompt)

processing_config = ProcessingConfig()

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
async def process_files(template_file: UploadFile = File(...), acronyms_file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)):
    try:
        # Save the uploaded files
        template_path = "template.csv"
        acronyms_path = "acronyms.csv"
        
        with open(template_path, "wb") as buffer:
            content = await template_file.read()
            buffer.write(content)
        
        with open(acronyms_path, "wb") as buffer:
            content = await acronyms_file.read()
            buffer.write(content)
        
        # Read the files
        template_df = pd.read_csv(template_path)
        acronyms_df = pd.read_csv(acronyms_path)
        
        # If no header row exists in acronyms_df, add one and rename the first column to 'acronym'
        if len(acronyms_df.columns) >= 1 and 'acronym' not in acronyms_df.columns:
            acronyms_df.columns = ['acronym'] + [f'col_{i}' for i in range(1, len(acronyms_df.columns))]
        
        # Validate the acronyms file
        if 'acronym' not in acronyms_df.columns:
            raise HTTPException(status_code=400, detail="Acronyms file must contain an 'acronym' column")
        
        # Apply starting point filter if enabled
        if processing_config.starting_point["enabled"] and processing_config.starting_point["acronym"]:
            start_acronym = processing_config.starting_point["acronym"]
            # Find the index of the starting acronym
            start_index = acronyms_df[acronyms_df["acronym"] == start_acronym].index
            if not start_index.empty:
                start_idx = start_index[0]
                acronyms_df = acronyms_df.iloc[start_idx:].reset_index(drop=True)
            else:
                # If acronym not found, start from beginning
                print(f"Starting acronym '{start_acronym}' not found in the list. Starting from beginning.")
        
        # Apply grade filtering if enabled
        if processing_config.grade_filter["enabled"]:
            if processing_config.grade_filter["single_grade"]:
                # Filter by single grade
                grade = processing_config.grade_filter["single_grade"]
                acronyms_df = acronyms_df[acronyms_df["acronym"].isin(
                    template_df[template_df["grade"] == grade]["acronym"]
                )].reset_index(drop=True)
            elif processing_config.grade_filter["grade_range"]:
                # Filter by grade range
                start_grade = processing_config.grade_filter["grade_range"]["start"]
                end_grade = processing_config.grade_filter["grade_range"]["end"]
                
                # Convert grades to numeric if possible
                try:
                    start_grade_num = float(start_grade)
                    end_grade_num = float(end_grade)
                    # Filter template by grade range
                    filtered_template = template_df[
                        (template_df["grade"].apply(lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.', '').isdigit() else 0) >= start_grade_num) &
                        (template_df["grade"].apply(lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.', '').isdigit() else 0) <= end_grade_num)
                    ]
                except (ValueError, TypeError):
                    # If grades are not numeric, filter as strings
                    filtered_template = template_df[
                        (template_df["grade"] >= start_grade) &
                        (template_df["grade"] <= end_grade)
                    ]
                
                acronyms_df = acronyms_df[acronyms_df["acronym"].isin(filtered_template["acronym"])].reset_index(drop=True)
        
        # Process the acronyms in batches
        results = []
        batch_size = processing_config.batch_size
        
        for i in range(0, len(acronyms_df), batch_size):
            batch = acronyms_df.iloc[i:i+batch_size]
            batch_results = []
            
            for _, row in batch.iterrows():
                acronym = row["acronym"]
                # Convert grade to Python int or str if it's a string
                grade_value = template_df[template_df["acronym"] == acronym]["grade"].iloc[0] if acronym in template_df["acronym"].values else "general"
                grade = int(grade_value) if isinstance(grade_value, (int, float, np.number)) else str(grade_value)
                
                # Get definition from AI service
                try:
                    if processing_config.llm == "gemini":
                        definition = await gemini_service.get_definition(acronym, str(grade))
                    else:
                        definition = await grok_service.get_definition(acronym, str(grade))
                except Exception as e:
                    print(f"Error getting definition for {acronym}: {str(e)}")
                    definition = f"Error: {str(e)}"
                
                # Enrich the acronym if enabled
                description = ""
                tags = ""
                if processing_config.enrichment["enabled"]:
                    try:
                        if processing_config.llm == "gemini":
                            enrichment = await gemini_service.enrich_acronym(acronym, definition, str(grade))
                        else:
                            enrichment = await grok_service.enrich_acronym(acronym, definition, str(grade))
                        
                        description = enrichment.get("description", "")
                        tags = enrichment.get("tags", "")
                    except Exception as e:
                        print(f"Error enriching acronym {acronym}: {str(e)}")
                
                batch_results.append({
                    "acronym": acronym,
                    "definition": definition,
                    "description": description,
                    "tags": tags,
                    "grade": grade
                })
            
            results.extend(batch_results)
        
        # Save results to CSV
        results_df = pd.DataFrame(results)
        results_df.to_csv("enriched_acronyms.csv", index=False)
        
        return JSONResponse(content={"results": results})
    except Exception as e:
        print(f"Error in process_files: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
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