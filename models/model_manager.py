"""Central model registry. Models are cached so each is loaded at most once
per process. Uses st.cache_resource when running under Streamlit and a plain
functools cache otherwise (so the pipeline also works in tests/scripts)."""

import logging
import subprocess
import sys
from functools import lru_cache

logger = logging.getLogger(__name__)

try:
    import streamlit as st
    _cache = st.cache_resource
except Exception:  # streamlit not installed (e.g. evaluation scripts)
    _cache = lru_cache(maxsize=None)


@_cache
def get_image_classifier():
    """Returns HF pipeline for umm-maybe/AI-image-detector (or None)."""
    try:
        from transformers import pipeline
        return pipeline('image-classification', model='umm-maybe/AI-image-detector')
    except Exception as e:
        logger.warning(f"Failed to load image classifier: {e}")
        return None


@_cache
def get_whisper_model():
    """Returns whisper 'base' model (or None)."""
    try:
        import whisper
        return whisper.load_model('base')
    except Exception as e:
        logger.warning(f"Failed to load whisper model: {e}")
        return None


@_cache
def get_sentence_transformer():
    """Returns SentenceTransformer model (or None)."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        logger.warning(f"Failed to load sentence transformer: {e}")
        return None


@_cache
def get_spacy_model():
    """Returns spaCy model, downloading it if missing (or None)."""
    try:
        import spacy
        try:
            return spacy.load('en_core_web_sm')
        except OSError:
            logger.info("Downloading spacy en_core_web_sm model...")
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
            )
            return spacy.load('en_core_web_sm')
    except Exception as e:
        logger.warning(f"Failed to load spacy model: {e}")
        return None
