"""
Text Analyzer Module

This module provides text analysis capabilities, including sentiment analysis,
named entity recognition, and other NLP tasks.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import spacy
from transformers import pipeline

from ...utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Data class for storing text analysis results."""
    text: str
    sentiment: Dict[str, float]
    entities: List[Dict[str, Union[str, float]]]
    language: str
    model_used: str
    processing_time: float  # in seconds
    
    def to_dict(self) -> Dict:
        """Convert analysis result to dictionary."""
        return {
            "text": self.text,
            "sentiment": self.sentiment,
            "entities": self.entities,
            "language": self.language,
            "model_used": self.model_used,
            "processing_time": self.processing_time
        }
    
    def to_json(self) -> str:
        """Convert analysis result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class TextAnalyzer:
    """Class for analyzing text using various NLP models."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the text analyzer.
        
        Args:
            model_name: Name of the NLP model to use. If None, uses the default model
                        from the configuration.
        """
        self.config = ConfigLoader().load_model_config()["models"]["nlp"]
        
        if model_name is None:
            model_name = self.config["transformer_model"]["name"]
        
        self.model_name = model_name
        logger.info(f"Initializing TextAnalyzer with model: {model_name}")
        
        # Load spaCy model for basic NLP tasks
        self.nlp = spacy.load(self.config["spacy_model"]["name"])
        
        # Load transformer models for advanced tasks
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=0 if self.config["spacy_model"].get("use_gpu", False) else -1
        )
    
    def analyze(self, text: str) -> AnalysisResult:
        """Analyze the given text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            AnalysisResult object containing analysis results.
        """
        import time
        start_time = time.time()
        
        # Basic processing with spaCy
        doc = self.nlp(text)
        
        # Get language
        language = doc.lang_
        
        # Extract entities
        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]
        
        # Get sentiment
        sentiment_result = self.sentiment_analyzer(text)
        sentiment = {
            sentiment_result[0]["label"]: sentiment_result[0]["score"]
        }
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return AnalysisResult(
            text=text,
            sentiment=sentiment,
            entities=entities,
            language=language,
            model_used=self.model_name,
            processing_time=processing_time
        )


if __name__ == "__main__":
    # Example usage
    analyzer = TextAnalyzer()
    result = analyzer.analyze("I love using this NLP library for analyzing text. Apple Inc. is a great company.")
    print(result.to_json()) 