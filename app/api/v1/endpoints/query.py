"""
Query Endpoints for NL2SQL Service
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, validator
import structlog

from app.core.security import get_current_user, require_api_key
from app.services.nl2sql_service import NL2SQLService
from app.models.schemas import QueryRequest, QueryResponse, User
from app.core.exceptions import (
    SQLGenerationError,
    SQLExecutionError,
    SecurityValidationError
)

logger = structlog.get_logger(__name__)
router = APIRouter()


class BulkQueryRequest(BaseModel):
    questions: List[str]
    database_url: str
    include_explanation: bool = True
    max_results: int = 100
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one question is required')
        if len(v) > 10:
            raise ValueError('Maximum 10 questions allowed in bulk request')
        return v


class QueryHistoryResponse(BaseModel):
    id: str
    question: str
    sql_query: str
    execution_time: float
    row_count: int
    created_at: str
    user_id: Optional[str] = None


@router.post("/execute", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    service: NL2SQLService = Depends()
):
    """
    Execute a natural language query and return SQL results
    """
    try:
        logger.info(
            "Processing query request",
            user_id=user.id if user else None,
            question=request.question[:100] + "..." if len(request.question) > 100 else request.question
        )
        
        # Process the query
        response = await service.process_query(request, user_id=user.id if user else None)
        
        # Log query execution in background
        background_tasks.add_task(
            service.log_query_execution,
            user_id=user.id if user else None,
            request=request,
            response=response
        )
        
        return response
        
    except SQLGenerationError as e:
        logger.error("SQL generation failed", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=422, detail=str(e))
    
    except SQLExecutionError as e:
        logger.error("SQL execution failed", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=400, detail=str(e))
    
    except SecurityValidationError as e:
        logger.error("Security validation failed", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/bulk", response_model=List[QueryResponse])
async def execute_bulk_queries(
    request: BulkQueryRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    service: NL2SQLService = Depends()
):
    """
    Execute multiple natural language queries in batch
    """
    try:
        logger.info(
            "Processing bulk query request",
            user_id=user.id if user else None,
            question_count=len(request.questions)
        )
        
        responses = []
        for question in request.questions:
            query_request = QueryRequest(
                question=question,
                database_url=request.database_url,
                include_explanation=request.include_explanation,
                max_results=request.max_results
            )
            
            response = await service.process_query(query_request, user_id=user.id if user else None)
            responses.append(response)
        
        return responses
        
    except Exception as e:
        logger.error("Bulk query execution failed", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=500, detail=f"Bulk query execution failed: {str(e)}")


@router.post("/validate")
async def validate_sql_query(
    sql_query: str,
    user: User = Depends(get_current_user),
    service: NL2SQLService = Depends()
):
    """
    Validate SQL query for security and syntax
    """
    try:
        validation_result = await service.validate_sql(sql_query)
        return validation_result
        
    except Exception as e:
        logger.error("SQL validation failed", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=500, detail=f"SQL validation failed: {str(e)}")


@router.post("/explain")
async def explain_sql_query(
    sql_query: str,
    question: str,
    user: User = Depends(get_current_user),
    service: NL2SQLService = Depends()
):
    """
    Generate explanation for a given SQL query
    """
    try:
        explanation = await service.generate_explanation(question, sql_query)
        return {"explanation": explanation, "sql_query": sql_query, "question": question}
        
    except Exception as e:
        logger.error("SQL explanation failed", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=500, detail=f"SQL explanation failed: {str(e)}")


@router.get("/history", response_model=List[QueryHistoryResponse])
async def get_query_history(
    limit: int = 10,
    offset: int = 0,
    user: User = Depends(get_current_user),
    service: NL2SQLService = Depends()
):
    """
    Get user's query history
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        history = await service.get_query_history(user.id, limit=limit, offset=offset)
        return history
        
    except Exception as e:
        logger.error("Failed to get query history", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=500, detail=f"Failed to get query history: {str(e)}")


@router.post("/upload-schema")
async def upload_schema_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    service: NL2SQLService = Depends()
):
    """
    Upload database schema file for analysis
    """
    try:
        if not file.filename.endswith(('.sql', '.json', '.yaml', '.yml')):
            raise HTTPException(
                status_code=400, 
                detail="Only .sql, .json, .yaml, .yml files are supported"
            )
        
        content = await file.read()
        schema_info = await service.parse_schema_file(content, file.filename)
        
        return {
            "message": "Schema file processed successfully",
            "tables_count": len(schema_info.get('tables', {})),
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error("Schema file upload failed", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=500, detail=f"Schema file upload failed: {str(e)}")


@router.get("/metrics")
async def get_query_metrics(
    user: User = Depends(get_current_user),
    service: NL2SQLService = Depends()
):
    """
    Get query execution metrics for the user
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        metrics = await service.get_user_metrics(user.id)
        return metrics
        
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e), user_id=user.id if user else None)
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


# Public endpoints (require API key only)
@router.post("/public/execute", response_model=QueryResponse)
async def execute_public_query(
    request: QueryRequest,
    api_key: str = Depends(require_api_key),
    service: NL2SQLService = Depends()
):
    """
    Public endpoint for query execution (API key authentication)
    """
    try:
        logger.info("Processing public query request", question=request.question[:100])
        response = await service.process_query(request)
        return response
        
    except Exception as e:
        logger.error("Public query execution failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@router.post("/public/validate")
async def validate_public_sql(
    sql_query: str,
    api_key: str = Depends(require_api_key),
    service: NL2SQLService = Depends()
):
    """
    Public endpoint for SQL validation (API key authentication)
    """
    try:
        validation_result = await service.validate_sql(sql_query)
        return validation_result
        
    except Exception as e:
        logger.error("Public SQL validation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"SQL validation failed: {str(e)}")
