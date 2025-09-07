from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    tenant_id: str
    question: str

class Citation(BaseModel):
    document: str
    page: int
    document_type: str
    confidence: float

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float
    has_knowledge_gap: bool = False
    suggestions: Optional[List[str]] = None

class DocumentInfo(BaseModel):
    id: str
    name: str
    type: str
    pages: int
    status: str = "ready"