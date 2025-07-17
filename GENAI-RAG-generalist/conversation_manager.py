from typing import List, Dict, Optional
import time
from datetime import datetime
import uuid
import logging
from db_service import db_service

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, max_history: int = 10, session_expiry: int = 3600):
        self.max_history = max_history
        self.session_expiry = session_expiry  # Session expiry in seconds

    def create_session(self) -> str:
        """Create a new conversation session with clean state."""
        try:
            session_id = str(uuid.uuid4())
            # Initialize session with empty message list and no document references
            db_service.store_conversation(session_id, {
                "role": "system",
                "content": "Session started",
                "timestamp": datetime.now().isoformat(),
                "document_context": {}  # Empty document context
            })
            logger.info(f"Created new session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise RuntimeError("Failed to create new session") from e

    def add_message(self, session_id: str, role: str, content: str, document_context: Optional[Dict] = None):
        """Add a message to the conversation history with document context."""
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "document_context": document_context if document_context else {}
            }
            
            # Store in db_service
            db_service.store_conversation(session_id, message)
            logger.info(f"Added message to session {session_id}")
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise RuntimeError("Failed to add message to conversation") from e

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get the conversation history for a session."""
        try:
            return db_service.get_conversation_history(session_id)
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        try:
            db_service.cleanup_expired_sessions(expiry_hours=self.session_expiry // 3600)
            logger.info("Cleaned up expired sessions")
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")

    def clear_history(self, session_id: str) -> bool:
        """Clear the conversation history and document references for a session."""
        try:
            success = db_service.clear_conversation(session_id)
            if success:
                # Reset session with a clean state message
                db_service.store_conversation(session_id, {
                    "role": "system",
                    "content": "Conversation cleared",
                    "timestamp": datetime.now().isoformat(),
                    "document_context": {}
                })
                logger.info(f"Successfully cleared conversation history and documents for session {session_id}")
            else:
                logger.warning(f"Failed to clear conversation history for session {session_id}")
            return success
        except Exception as e:
            logger.error(f"Error clearing conversation history: {str(e)}")
            return False

    def get_session_info(self, session_id: str) -> Dict:
        """Get session information."""
        try:
            history = self.get_history(session_id)
            if not history:
                return {}
            
            active_documents = set()
            for message in history:
                if doc_context := message.get('document_context'):
                    if isinstance(doc_context, dict):
                        if 'filename' in doc_context:
                            active_documents.add(doc_context['filename'])
                        elif 'documents' in doc_context:
                            active_documents.update(doc_context.get('documents', []))
            
            last_message = history[-1]
            return {
                "created_at": history[0]['timestamp'],
                "last_accessed": last_message['timestamp'],
                "message_count": len(history),
                "active_documents": list(active_documents)
            }
        except Exception as e:
            logger.error(f"Error retrieving session info: {str(e)}")
            return {}

    def get_active_documents(self, session_id: str) -> set:
        """Get the set of active documents in the conversation."""
        try:
            history = self.get_history(session_id)
            active_docs = set()
            for message in history:
                if doc_context := message.get('document_context'):
                    if isinstance(doc_context, dict):
                        if 'filename' in doc_context:
                            active_docs.add(doc_context['filename'])
                        elif 'documents' in doc_context:
                            active_docs.update(doc_context.get('documents', []))
            return active_docs
        except Exception as e:
            logger.error(f"Error retrieving active documents: {str(e)}")
            return set()

    def get_context_window(self, session_id: str, window_size: int = 3) -> List[Dict[str, str]]:
        """Get recent conversation context for a session."""
        try:
            history = self.get_history(session_id)
            return history[-window_size * 2:] if history else []
        except Exception as e:
            logger.error(f"Error retrieving context window: {str(e)}")
            return []
