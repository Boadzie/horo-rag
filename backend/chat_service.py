from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from models import QueryResponse, Citation, DocumentInfo
from typing import Dict, List
import os
import hashlib

class ChatService:
    def __init__(self):
        # Configure LlamaIndex with Ollama
        Settings.llm = Ollama(model="gemma3", base_url="http://localhost:11434")
        Settings.embed_model = OllamaEmbedding(model_name="bge-m3", base_url="http://localhost:11434")
        
        # In-memory storage per tenant
        self.tenant_indices: Dict[str, VectorStoreIndex] = {}
        self.tenant_documents: Dict[str, List[DocumentInfo]] = {}
    
    def detect_document_type(self, filename: str, content: str = "") -> str:
        """Detect document type from filename and content"""
        name = filename.lower()
        content_lower = content.lower()
        
        if any(word in name for word in ['policy', 'procedure', 'rule']):
            return "Policy"
        elif any(word in name for word in ['handbook', 'manual', 'guide']):
            return "Handbook"  
        elif any(word in name for word in ['finance', 'financial', 'budget', 'revenue']):
            return "Finance"
        elif any(word in content_lower for word in ['loan', 'credit', 'lending']):
            return "Policy"
        elif any(word in content_lower for word in ['onboard', 'training', 'employee']):
            return "Handbook"
        else:
            return "Document"
    
    def estimate_pages(self, content: str) -> int:
        """Estimate page count from content length"""
        return max(1, len(content) // 2000)
    
    async def upload_document(self, tenant_id: str, filename: str, content: str) -> DocumentInfo:
        """Process and index document"""
        # Create document ID
        doc_id = hashlib.md5(f"{tenant_id}_{filename}".encode()).hexdigest()[:8]
        
        # Detect type and estimate pages
        doc_type = self.detect_document_type(filename, content)
        pages = self.estimate_pages(content)
        
        # Create LlamaIndex document with metadata
        document = Document(
            text=content,
            metadata={
                "filename": filename,
                "document_type": doc_type,
                "tenant_id": tenant_id,
                "doc_id": doc_id,
                "pages": pages
            }
        )
        
        # Create or update index for tenant
        if tenant_id not in self.tenant_indices:
            self.tenant_indices[tenant_id] = VectorStoreIndex([])
            self.tenant_documents[tenant_id] = []
        
        # Add to index
        self.tenant_indices[tenant_id].insert(document)
        
        # Store document info
        doc_info = DocumentInfo(
            id=doc_id,
            name=filename,
            type=doc_type,
            pages=pages
        )
        self.tenant_documents[tenant_id].append(doc_info)
        
        return doc_info
    
    def extract_citations(self, source_nodes, tenant_id: str) -> List[Citation]:
        """Extract citations from retrieval results"""
        citations = []
        for node in source_nodes:
            metadata = node.metadata
            citations.append(Citation(
                document=metadata.get("filename", "Unknown"),
                page=min(metadata.get("pages", 1), max(1, len(node.text) // 500)),
                document_type=metadata.get("document_type", "Document"),
                confidence=node.score if hasattr(node, 'score') else 0.8
            ))
        return citations
    
    def detect_knowledge_gap(self, question: str, answer: str) -> tuple[bool, List[str]]:
        """Detect if query indicates missing information"""
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Knowledge gap indicators
        gap_indicators = [
            "don't have information",
            "not found",
            "no information",
            "unable to find"
        ]
        
        has_gap = any(indicator in answer_lower for indicator in gap_indicators)
        
        # Generate suggestions based on question intent
        suggestions = []
        if any(word in question_lower for word in ['loan', 'credit', 'lending']):
            suggestions = ["Loan Policy Document", "Credit Guidelines", "Lending Procedures"]
        elif any(word in question_lower for word in ['onboard', 'training', 'employee']):
            suggestions = ["Employee Handbook", "Training Manual", "HR Policies"]
        elif any(word in question_lower for word in ['finance', 'revenue', 'cac', 'budget']):
            suggestions = ["Financial Reports", "Budget Documents", "Growth Metrics"]
        elif any(word in question_lower for word in ['customer', 'client', 'acquisition']):
            suggestions = ["Customer Data", "Sales Reports", "Marketing Analytics"]
        else:
            suggestions = ["Business Documents", "Policy Manual", "Operational Guidelines"]
        
        return has_gap, suggestions
    
    async def query(self, tenant_id: str, question: str) -> QueryResponse:
        """Query tenant's documents"""
        # Check if tenant has documents
        if tenant_id not in self.tenant_indices:
            return QueryResponse(
                answer="I don't have any documents to search. Please upload your business documents first.",
                citations=[],
                confidence=0.0,
                has_knowledge_gap=True,
                suggestions=["Business Documents", "Policy Manual"]
            )
        
        try:
            # Query the index
            query_engine = self.tenant_indices[tenant_id].as_query_engine(
                similarity_top_k=3,
                response_mode="compact"
            )
            
            response = query_engine.query(question)
            
            # Extract citations
            citations = self.extract_citations(response.source_nodes, tenant_id)
            
            # Check for knowledge gaps
            has_gap, suggestions = self.detect_knowledge_gap(question, response.response)
            
            # Calculate confidence based on citations and response quality
            confidence = 0.9 if citations and len(response.response) > 50 else 0.3
            
            return QueryResponse(
                answer=response.response,
                citations=citations,
                confidence=confidence,
                has_knowledge_gap=has_gap,
                suggestions=suggestions if has_gap else None
            )
            
        except Exception as e:
            return QueryResponse(
                answer=f"I encountered an error while searching your documents: {str(e)}",
                citations=[],
                confidence=0.0,
                has_knowledge_gap=True,
                suggestions=["Please try rephrasing your question"]
            )
    
    def get_documents(self, tenant_id: str) -> List[DocumentInfo]:
        """Get all documents for tenant"""
        return self.tenant_documents.get(tenant_id, [])

# Global instance
chat_service = ChatService()