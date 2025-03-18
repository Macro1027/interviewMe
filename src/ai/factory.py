"""
Factory for creating AI service instances.
"""
from typing import Dict, Optional, Type, Union

from src.ai.interfaces import (
    ICompletionService,
    IEmbeddingService,
    ISentimentAnalysisService,
    ISpeechRecognitionService,
    ISpeechSynthesisService
)
from src.ai.openai_service import OpenAIService
from src.ai.perplexity_service import PerplexityService
from src.utils.config import get_settings
from src.utils.logger import setup_logger

# Initialize settings and logger
settings = get_settings()
logger = setup_logger(__name__)

# Service provider mapping
_completion_services: Dict[str, Type[ICompletionService]] = {
    "openai": OpenAIService,
    "perplexity": PerplexityService,
    # Add more providers as they are implemented
    # "azure": AzureOpenAIService,
    # "anthropic": AnthropicService,
}

_embedding_services: Dict[str, Type[IEmbeddingService]] = {
    # Will be implemented later
    # "openai": OpenAIEmbeddingService,
    # "azure": AzureEmbeddingService,
}

_speech_recognition_services: Dict[str, Type[ISpeechRecognitionService]] = {
    # Will be implemented later
    # "google": GoogleSpeechRecognitionService,
    # "azure": AzureSpeechRecognitionService,
    # "amazon": AmazonSpeechRecognitionService,
}

_speech_synthesis_services: Dict[str, Type[ISpeechSynthesisService]] = {
    # Will be implemented later
    # "elevenlabs": ElevenLabsSpeechSynthesisService,
    # "azure": AzureSpeechSynthesisService,
    # "amazon": AmazonPollyService,
}

_sentiment_analysis_services: Dict[str, Type[ISentimentAnalysisService]] = {
    # Will be implemented later
    # "openai": OpenAISentimentAnalysisService,
    # "azure": AzureSentimentAnalysisService,
    # "amazon": AmazonComprehendService,
}

# Service instances (cached)
_service_instances: Dict[str, object] = {}


def get_completion_service(provider: Optional[str] = None) -> ICompletionService:
    """
    Get a completion service instance.
    
    Args:
        provider: Service provider name (default: from settings or "openai")
        
    Returns:
        ICompletionService: Completion service instance
    
    Raises:
        ValueError: If provider is not supported
    """
    # Determine provider
    provider = provider or settings.COMPLETION_PROVIDER or "openai"
    
    # Check if service class exists
    if provider not in _completion_services:
        available = ", ".join(_completion_services.keys())
        raise ValueError(f"Unsupported completion provider: {provider}. Available: {available}")
    
    # Check if instance already exists
    instance_key = f"completion_{provider}"
    if instance_key in _service_instances:
        return _service_instances[instance_key]
    
    # Create new instance
    service_class = _completion_services[provider]
    instance = service_class()
    
    # Cache instance
    _service_instances[instance_key] = instance
    
    logger.info(f"Created completion service with provider: {provider}")
    return instance


def get_embedding_service(provider: Optional[str] = None) -> IEmbeddingService:
    """
    Get an embedding service instance.
    
    Args:
        provider: Service provider name (default: from settings or "openai")
        
    Returns:
        IEmbeddingService: Embedding service instance
    
    Raises:
        ValueError: If provider is not supported
    """
    # Determine provider
    provider = provider or settings.EMBEDDING_PROVIDER or "openai"
    
    # Check if service class exists
    if provider not in _embedding_services:
        available = ", ".join(_embedding_services.keys())
        raise ValueError(f"Unsupported embedding provider: {provider}. Available: {available}")
    
    # Check if instance already exists
    instance_key = f"embedding_{provider}"
    if instance_key in _service_instances:
        return _service_instances[instance_key]
    
    # Create new instance
    service_class = _embedding_services[provider]
    instance = service_class()
    
    # Cache instance
    _service_instances[instance_key] = instance
    
    logger.info(f"Created embedding service with provider: {provider}")
    return instance


def get_speech_recognition_service(provider: Optional[str] = None) -> ISpeechRecognitionService:
    """
    Get a speech recognition service instance.
    
    Args:
        provider: Service provider name (default: from settings or "google")
        
    Returns:
        ISpeechRecognitionService: Speech recognition service instance
    
    Raises:
        ValueError: If provider is not supported
    """
    # Determine provider
    provider = provider or settings.SPEECH_RECOGNITION_PROVIDER or "google"
    
    # Check if service class exists
    if provider not in _speech_recognition_services:
        available = ", ".join(_speech_recognition_services.keys())
        raise ValueError(f"Unsupported speech recognition provider: {provider}. Available: {available}")
    
    # Check if instance already exists
    instance_key = f"speech_recognition_{provider}"
    if instance_key in _service_instances:
        return _service_instances[instance_key]
    
    # Create new instance
    service_class = _speech_recognition_services[provider]
    instance = service_class()
    
    # Cache instance
    _service_instances[instance_key] = instance
    
    logger.info(f"Created speech recognition service with provider: {provider}")
    return instance


def get_speech_synthesis_service(provider: Optional[str] = None) -> ISpeechSynthesisService:
    """
    Get a speech synthesis service instance.
    
    Args:
        provider: Service provider name (default: from settings or "elevenlabs")
        
    Returns:
        ISpeechSynthesisService: Speech synthesis service instance
    
    Raises:
        ValueError: If provider is not supported
    """
    # Determine provider
    provider = provider or settings.SPEECH_SYNTHESIS_PROVIDER or "elevenlabs"
    
    # Check if service class exists
    if provider not in _speech_synthesis_services:
        available = ", ".join(_speech_synthesis_services.keys())
        raise ValueError(f"Unsupported speech synthesis provider: {provider}. Available: {available}")
    
    # Check if instance already exists
    instance_key = f"speech_synthesis_{provider}"
    if instance_key in _service_instances:
        return _service_instances[instance_key]
    
    # Create new instance
    service_class = _speech_synthesis_services[provider]
    instance = service_class()
    
    # Cache instance
    _service_instances[instance_key] = instance
    
    logger.info(f"Created speech synthesis service with provider: {provider}")
    return instance


def get_sentiment_analysis_service(provider: Optional[str] = None) -> ISentimentAnalysisService:
    """
    Get a sentiment analysis service instance.
    
    Args:
        provider: Service provider name (default: from settings or "openai")
        
    Returns:
        ISentimentAnalysisService: Sentiment analysis service instance
    
    Raises:
        ValueError: If provider is not supported
    """
    # Determine provider
    provider = provider or settings.SENTIMENT_ANALYSIS_PROVIDER or "openai"
    
    # Check if service class exists
    if provider not in _sentiment_analysis_services:
        available = ", ".join(_sentiment_analysis_services.keys())
        raise ValueError(f"Unsupported sentiment analysis provider: {provider}. Available: {available}")
    
    # Check if instance already exists
    instance_key = f"sentiment_analysis_{provider}"
    if instance_key in _service_instances:
        return _service_instances[instance_key]
    
    # Create new instance
    service_class = _sentiment_analysis_services[provider]
    instance = service_class()
    
    # Cache instance
    _service_instances[instance_key] = instance
    
    logger.info(f"Created sentiment analysis service with provider: {provider}")
    return instance 