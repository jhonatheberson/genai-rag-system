from typing import List, Dict, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import utils
from datetime import datetime
import re
from sklearn.preprocessing import normalize
from db_service import db_service

__all__ = ['VectorStore']  # Add this line to explicitly export VectorStore

class VectorStore:
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384  # Output dimension of the chosen model
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []  # List to store metadata for each document chunk

    def add_documents(self, chunks: List[str], doc_metadata: Dict[str, any]) -> None:
        """Add document chunks to the vector store with metadata."""
        if not chunks:
            return
        
        try:
            # Convert text chunks to embeddings
            embeddings = self.encoder.encode(chunks)
            
            # Normalize embeddings for better similarity search
            normalized_embeddings = normalize(embeddings)
            
            # Add to FAISS index
            self.index.add(np.array(normalized_embeddings).astype('float32'))
            self.documents.extend(chunks)
            
            # Add metadata for each chunk
            base_metadata = doc_metadata or {}
            chunk_metadata = []
            
            # Store document in MongoDB
            document_id = db_service.store_document(base_metadata)
            
            # Prepare chunks with embeddings for MongoDB
            chunks_to_store = []
            for i, (chunk, embedding) in enumerate(zip(chunks, normalized_embeddings)):
                metadata = base_metadata.copy()
                metadata.update({
                    'chunk_index': i,
                    'chunk_size': len(chunk),
                    'total_chunks': len(chunks),
                    'added_at': datetime.now().isoformat(),
                    'text': chunk,
                    'embedding': embedding.tolist()
                })
                chunks_to_store.append(metadata)
                chunk_metadata.append(metadata)
            
            # Store chunks in MongoDB
            db_service.store_chunks(document_id, chunks_to_store)
            
            self.metadata.extend(chunk_metadata)
            
        except Exception as e:
            print(f"Error adding documents to vector store: {str(e)}")
            raise

    def get_document_stats(self) -> Dict[str, any]:
        """Get statistics about stored documents."""
        try:
            return db_service.get_document_stats()
        except Exception as e:
            print(f"Error getting document stats: {str(e)}")
            return {
                'total_documents': 0,
                'total_chunks': 0,
                'total_size': 0,
                'formats': []
            }

    def get_relevant_context(self, query: str, k: int = 5) -> Tuple[str, List[Dict[str, any]]]:
        """Retrieve relevant context and metadata for the query."""
        if not self.documents:
            return "", []
        
        try:
            # Get query embedding and normalize
            query_embedding = self.encoder.encode([query])
            normalized_query = normalize(query_embedding)
            
            # Search for similar chunks
            distances, indices = self.index.search(
                np.array(normalized_query).astype('float32'),
                k
            )
            
            # Format context with source information
            contexts = []
            metadata_list = []
            
            for idx, distance in zip(indices[0], distances[0]):
                if idx >= len(self.documents):  # Safety check
                    continue
                    
                chunk = self.documents[idx]
                metadata = self.metadata[idx]
                
                contexts.append(f"From {metadata.get('filename', 'Unknown')}:\n{chunk}")
                metadata_list.append(metadata)
            
            formatted_context = "\n\n".join(contexts)
            return formatted_context, metadata_list
            
        except Exception as e:
            print(f"Error in retrieval: {str(e)}")
            return "", []
