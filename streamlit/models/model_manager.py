import streamlit as st
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)

@st.cache_resource
def get_image_classifier():
    """Returns HF pipeline for umm-maybe/AI-image-detector."""
    try:
        from transformers import pipeline
        return pipeline('image-classification', model='umm-maybe/AI-image-detector')
    except Exception as e:
        logger.warning(f"Failed to load image classifier: {e}")
        return None

@st.cache_resource
def get_whisper_model():
    """Returns whisper model base."""
    try:
        import whisper
        return whisper.load_model('base')
    except Exception as e:
        logger.warning(f"Failed to load whisper model: {e}")
        return None

@st.cache_resource
def get_sentence_transformer():
    """Returns SentenceTransformer model."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        logger.warning(f"Failed to load sentence transformer: {e}")
        return None

@st.cache_resource
def get_spacy_model():
    """Returns spacy model, downloads if missing."""
    try:
        import spacy
        try:
            return spacy.load('en_core_web_sm')
        except OSError:
            logger.info("Downloading spacy en_core_web_sm model...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            return spacy.load('en_core_web_sm')
    except Exception as e:
        logger.warning(f"Failed to load spacy model: {e}")
        return None
