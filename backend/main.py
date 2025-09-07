from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import QueryRequest, QueryResponse, DocumentInfo
from chat_service import chat_service
from typing import List, Optional

app = FastAPI(title="Horo RAG MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload", response_model=DocumentInfo)
async def upload_document(
    file: UploadFile = File(...),
    x_tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Upload and process document"""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        
        if len(text_content.strip()) < 50:
            raise HTTPException(status_code=400, detail="Document too short or empty")
        
        # Process with chat service
        doc_info = await chat_service.upload_document(
            tenant_id=x_tenant_id,
            filename=file.filename,
            content=text_content
        )
        
        return doc_info
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Unable to read file. Please upload text-based documents.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Query tenant's documents"""
    if request.tenant_id != x_tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    response = await chat_service.query(request.tenant_id, request.question)
    return response

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents(x_tenant_id: str = Header(..., alias="X-Tenant-ID")):
    """List tenant's documents"""
    return chat_service.get_documents(x_tenant_id)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)