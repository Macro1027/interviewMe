"""
Main API Module

This module provides the main FastAPI application for the project's API.
"""

import logging
import time
from typing import Dict, List, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from ...ai.nlp import TextAnalyzer
from ...utils.config_loader import ConfigLoader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load configuration
config = ConfigLoader().load_settings()
api_config = config.get("api", {})

# Create FastAPI app
app = FastAPI(
    title="AI Project API",
    description="API for accessing AI capabilities",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_config.get("allowed_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Rate limiting middleware
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """Add rate limiting headers to responses."""
    # This is a simple implementation; production would use Redis or similar
    start_time = time.time()
    
    # Set arbitrary rate limits for demonstration
    rate_limit = 100
    rate_limit_remaining = 99
    rate_limit_reset = int(time.time()) + 60
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-Rate-Limit-Limit"] = str(rate_limit)
    response.headers["X-Rate-Limit-Remaining"] = str(rate_limit_remaining)
    response.headers["X-Rate-Limit-Reset"] = str(rate_limit_reset)
    
    # Add processing time header
    processing_time = time.time() - start_time
    response.headers["X-Processing-Time"] = str(processing_time)
    
    return response


# Models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class NLPAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = Field(..., description="Type of analysis: sentiment, entity, intent, summarization")
    model: Optional[str] = None


class NLPAnalysisResponse(BaseModel):
    analysis: Dict
    model_used: str
    processing_time: float


# Auth routes
@app.post("/api/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get an access token for API access."""
    # In a real app, this would authenticate against a database
    if form_data.username == "admin" and form_data.password == "password":
        return {
            "access_token": "dummy_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


# NLP routes
@app.post("/api/nlp/analyze", response_model=NLPAnalysisResponse)
async def analyze_text(
    request: NLPAnalysisRequest, token: str = Depends(oauth2_scheme)
):
    """Analyze text using NLP models."""
    try:
        # In production, validate token here
        
        # Initialize text analyzer
        analyzer = TextAnalyzer(model_name=request.model)
        
        # Analyze text
        result = analyzer.analyze(request.text)
        
        # Return response based on analysis_type
        if request.analysis_type == "sentiment":
            analysis = {"sentiment": result.sentiment}
        elif request.analysis_type == "entity":
            analysis = {"entities": result.entities}
        elif request.analysis_type == "intent":
            # Intent analysis would be implemented separately
            analysis = {"intent": "not_implemented"}
        elif request.analysis_type == "summarization":
            # Summarization would be implemented separately
            analysis = {"summary": "not_implemented"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported analysis type: {request.analysis_type}",
            )
        
        return {
            "analysis": analysis,
            "model_used": result.model_used,
            "processing_time": result.processing_time,
        }
    except Exception as e:
        logger.error(f"Error in analyze_text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing text: {str(e)}",
        )


# Health check
@app.get("/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": str(exc.detail),
            "code": exc.status_code,
            "timestamp": time.time(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "timestamp": time.time(),
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get port from configuration
    port = api_config.get("port", 8000)
    
    logger.info(f"Starting API server on port {port}")
    uvicorn.run(
        "main:app",
        host=api_config.get("host", "0.0.0.0"),
        port=port,
        reload=api_config.get("debug", True),
    ) 