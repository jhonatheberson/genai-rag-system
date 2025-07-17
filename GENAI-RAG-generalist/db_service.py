import os
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InMemoryDBService:
    def __init__(self):
        self.documents = {}
        self.conversations = {}
        self.chunks = {}
        self.logger = logging.getLogger(__name__)

    def store_document(self, metadata: Dict) -> str:
        doc_id = str(uuid.uuid4())
        metadata['upload_time'] = datetime.now()
        self.documents[doc_id] = metadata
        self.logger.info(f"Stored document with ID: {doc_id}")
        return doc_id

    def store_chunks(self, document_id: str, chunks: List[Dict]) -> List[str]:
        chunk_ids = []
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            chunk['document_id'] = document_id
            chunk['created_at'] = datetime.now()
            self.chunks[chunk_id] = chunk
            chunk_ids.append(chunk_id)
        self.logger.info(f"Stored {len(chunk_ids)} chunks for document {document_id}")
        return chunk_ids

    def store_conversation(self, session_id: str, message: Dict):
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                'messages': [],
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'documents': set()
            }
        message['timestamp'] = datetime.now()
        if doc_context := message.get('document_context', {}):
            if 'filename' in doc_context:
                self.conversations[session_id]['documents'].add(doc_context['filename'])
            elif 'documents' in doc_context:
                self.conversations[session_id]['documents'].update(doc_context.get('documents', []))
        
        self.conversations[session_id]['messages'].append(message)
        self.conversations[session_id]['last_accessed'] = datetime.now().isoformat()
        self.logger.info(f"Stored conversation message for session {session_id}")

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        if session_id in self.conversations:
            self.conversations[session_id]['last_accessed'] = datetime.now().isoformat()
            return self.conversations[session_id].get('messages', [])
        return []

    def clear_conversation(self, session_id: str) -> bool:
        """Clear the conversation history and document references for a session."""
        try:
            if session_id in self.conversations:
                # Preserve session metadata but clear messages and documents
                created_at = self.conversations[session_id].get('created_at')
                self.conversations[session_id] = {
                    'messages': [],
                    'created_at': created_at,
                    'last_accessed': datetime.now().isoformat(),
                    'documents': set()
                }
                self.logger.info(f"Cleared conversation history and documents for session {session_id}")
                return True
            else:
                self.logger.warning(f"No conversation found for session {session_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error clearing conversation: {str(e)}")
            return False

    def cleanup_expired_sessions(self, expiry_hours: int = 24):
        """Remove expired conversation sessions."""
        expiry_time = datetime.now().timestamp() - (expiry_hours * 3600)
        expired_sessions = []
        for session_id, session in self.conversations.items():
            last_message = session['messages'][-1] if session['messages'] else None
            if last_message and last_message['timestamp'].timestamp() < expiry_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.conversations[session_id]
        self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def get_document_stats(self) -> Dict:
        stats = {
            'total_documents': len(self.documents),
            'total_chunks': len(self.chunks),
            'total_size': sum(doc.get('file_size', 0) for doc in self.documents.values()),
            'formats': list(set(doc.get('format', '') for doc in self.documents.values()))
        }
        self.logger.info("Retrieved document statistics successfully")
        return stats

    def get_document_by_id(self, document_id: str) -> Optional[Dict]:
        return self.documents.get(document_id)

    def get_chunks_by_document(self, document_id: str) -> List[Dict]:
        return [chunk for chunk in self.chunks.values() if chunk['document_id'] == document_id]

# Create a singleton instance
db_service = InMemoryDBService()
