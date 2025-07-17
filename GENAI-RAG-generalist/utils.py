import re
from typing import List

# Global settings
MAX_CHUNK_SIZE = 800  
SIMILARITY_THRESHOLD = 0.7

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using regex."""
    # Basic sentence splitting pattern
    pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]

def validate_file_type(file_type: str) -> bool:
    """Validate if file type is supported."""
    return file_type in [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/html'
         'text/csv',
        'application/csv'
    ]

def sanitize_text(text: str) -> str:
    """Clean and sanitize text content."""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Remove special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text
