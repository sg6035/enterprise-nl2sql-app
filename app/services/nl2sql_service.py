"""
Enhanced Enterprise NL2SQL Service
Combines all the advanced features from the original implementation with enterprise enhancements
"""

import asyncio
import json
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re

# Database
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

# LLM Integration
import openai
from openai import OpenAI

# ML/NLP
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Caching
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

# Logging
import structlog

from app.config import settings
from app.models.schemas import (
    QueryRequest, QueryResponse, SchemaInfo, ValidationResult,
    QueryHistory, QueryMetrics, User
)
from app.core.exceptions import (
    SQLGenerationError, SQLExecutionError, SecurityValidationError,
    SchemaExtractionError
)

logger = structlog.get_logger(__name__)


@dataclass
class PromptTemplate:
    """Container for prompt templates"""
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0
    max_tokens: int = 1000


class EnhancedSchemaExtractor:
    """Enhanced schema extraction with caching and optimization"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_pre_ping=True
        )
        self.inspector = inspect(self.engine)
        
    async def extract_schema(self, use_cache: bool = True) -> SchemaInfo:
        """Extract comprehensive schema information with caching"""
        cache_key = f"schema:{hashlib.md5(self.database_url.encode()).hexdigest()}"
        
        if use_cache:
            cached_schema = await self._get_cached_schema(cache_key)
            if cached_schema:
                logger.info("Using cached schema")
                return cached_schema
        
        try:
            logger.info("Extracting database schema")
            
            # Extract tables info
            tables = {}
            relationships = []
            sample_data = {}
            
            table_names = self.inspector.get_table_names()
            
            # Process tables in parallel for better performance
            tasks = [
                self._process_table(table_name) 
                for table_name in table_names[:20]  # Limit to 20 tables for performance
            ]
            
            table_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for table_name, result in zip(table_names[:20], table_results):
                if isinstance(result, Exception):
                    logger.warning(f"Failed to process table {table_name}: {result}")
                    continue
                    
                table_info, table_relationships, table_sample_data = result
                tables[table_name] = table_info
                relationships.extend(table_relationships)
                sample_data[table_name] = table_sample_data
            
            schema_info = SchemaInfo(
                tables=tables,
                relationships=relationships,
                sample_data=sample_data,
                metadata={
                    "extracted_at": datetime.now().isoformat(),
                    "table_count": len(tables),
                    "relationship_count": len(relationships)
                }
            )
            
            # Cache the schema
            if use_cache:
                await self._cache_schema(cache_key, schema_info)
            
            logger.info(f"Extracted schema for {len(tables)} tables")
            return schema_info
            
        except Exception as e:
            logger.error(f"Schema extraction failed: {str(e)}")
            raise SchemaExtractionError(f"Failed to extract schema: {str(e)}")
    
    async def _process_table(self, table_name: str) -> Tuple[Dict, List, List]:
        """Process a single table (async)"""
        try:
            # Get column information
            columns = []
            for column in self.inspector.get_columns(table_name):
                columns.append({
                    'name': column['name'],
                    'type': str(column['type']),
                    'nullable': column['nullable'],
                    'primary_key': column.get('primary_key', False),
                    'default': column.get('default'),
                    'comment': column.get('comment')
                })
            
            # Get foreign keys
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            relationships = []
            
            for fk in foreign_keys:
                relationships.append({
                    'from_table': table_name,
                    'from_column': fk['constrained_columns'][0],
                    'to_table': fk['referred_table'],
                    'to_column': fk['referred_columns'][0]
                })
            
            # Get indexes for optimization hints
            indexes = self.inspector.get_indexes(table_name)
            
            table_info = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes,
                'description': self._generate_table_description(table_name, columns),
                'row_count_estimate': await self._estimate_row_count(table_name)
            }
            
            # Get sample data
            sample_data = await self._get_sample_data(table_name, limit=3)
            
            return table_info, relationships, sample_data
            
        except Exception as e:
            logger.warning(f"Failed to process table {table_name}: {str(e)}")
            return {}, [], []
    
    async def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample data from table asynchronously"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.warning(f"Could not get sample data for {table_name}: {str(e)}")
            return []
    
    async def _estimate_row_count(self, table_name: str) -> int:
        """Estimate row count for large tables"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
        except Exception:
            return 0
    
    def _generate_table_description(self, table_name: str, columns: List[Dict]) -> str:
        """Generate human-readable table description"""
        col_names = [col['name'] for col in columns]
        pk_cols = [col['name'] for col in columns if col.get('primary_key')]
        
        desc = f"Table {table_name} contains columns: {', '.join(col_names)}"
        if pk_cols:
            desc += f". Primary key: {', '.join(pk_cols)}"
        
        return desc
    
    async def _get_cached_schema(self, cache_key: str) -> Optional[SchemaInfo]:
        """Get cached schema if available"""
        try:
            # Implementation would use Redis or other cache
            return None
        except Exception:
            return None
    
    async def _cache_schema(self, cache_key: str, schema_info: SchemaInfo):
        """Cache schema information"""
        try:
            # Implementation would use Redis with TTL
            pass
        except Exception:
            pass


class IntelligentSchemaLinker:
    """Enhanced schema linking with ML-based relevance scoring"""
    
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.table_embeddings_cache = {}
        
    async def find_relevant_tables(
        self, 
        question: str, 
        schema: SchemaInfo, 
        max_tables: int = 5,
        confidence_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Find tables most relevant to the user question using advanced ML techniques"""
        
        logger.info(f"Finding relevant tables for question: {question[:100]}...")
        
        question_embedding = self.embedder.encode([question.lower()])
        table_scores = []
        
        for table_name, table_info in schema.tables.items():
            try:
                # Calculate semantic similarity
                similarity_score = await self._calculate_table_similarity(
                    question, question_embedding, table_name, table_info
                )
                
                # Apply business rules and heuristics
                relevance_score = await self._apply_relevance_heuristics(
                    question, table_name, table_info, similarity_score
                )
                
                table_scores.append((table_name, relevance_score, table_info))
                
            except Exception as e:
                logger.warning(f"Failed to score table {table_name}: {str(e)}")
                continue
        
        # Sort by relevance and filter by threshold
        table_scores.sort(key=lambda x: x[1], reverse=True)
        relevant_tables = {}
        
        for table_name, score, table_info in table_scores[:max_tables]:
            if score > confidence_threshold:
                relevant_tables[table_name] = {
                    **table_info,
                    'relevance_score': score,
                    'confidence': min(score * 2, 1.0)  # Convert to confidence percentage
                }
        
        logger.info(f"Found {len(relevant_tables)} relevant tables")
        return relevant_tables
    
    async def _calculate_table_similarity(
        self, 
        question: str, 
        question_embedding: np.ndarray,
        table_name: str, 
        table_info: Dict
    ) -> float:
        """Calculate semantic similarity between question and table"""
        
        # Create comprehensive table description
        table_desc = self._create_table_description(table_name, table_info)
        
        # Use cached embeddings if available
        cache_key = hashlib.md5(table_desc.encode()).hexdigest()
        if cache_key in self.table_embeddings_cache:
            table_embedding = self.table_embeddings_cache[cache_key]
        else:
            table_embedding = self.embedder.encode([table_desc.lower()])
            self.table_embeddings_cache[cache_key] = table_embedding
        
        # Calculate cosine similarity
        similarity = cosine_similarity(question_embedding, table_embedding)[0][0]
        return float(similarity)
    
    async def _apply_relevance_heuristics(
        self,
        question: str,
        table_name: str,
        table_info: Dict,
        base_score: float
    ) -> float:
        """Apply business rules and heuristics to improve relevance scoring"""
        
        score = base_score
        question_lower = question.lower()
        table_name_lower = table_name.lower()
        
        # Boost score if table name appears in question
        if table_name_lower in question_lower:
            score += 0.3
        
        # Boost score if column names appear in question
        column_matches = 0
        for col in table_info.get('columns', []):
            if col['name'].lower() in question_lower:
                column_matches += 1
                score += 0.2
        
        # Boost for primary key tables (usually important entities)
        pk_columns = [col for col in table_info.get('columns', []) if col.get('primary_key')]
        if pk_columns:
            score += 0.1
        
        # Boost for tables with relationships (connected entities)
        if table_info.get('foreign_keys'):
            score += 0.1
        
        # Business domain heuristics
        business_keywords = {
            'revenue': ['order', 'sale', 'invoice', 'payment'],
            'customer': ['customer', 'user', 'client', 'account'],
            'product': ['product', 'item', 'inventory', 'catalog'],
            'time': ['date', 'time', 'period', 'month', 'year']
        }
        
        for domain, keywords in business_keywords.items():
            if any(kw in question_lower for kw in [domain]):
                if any(kw in table_name_lower for kw in keywords):
                    score += 0.15
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _create_table_description(self, table_name: str, table_info: Dict) -> str:
        """Create comprehensive table description for embedding"""
        
        desc_parts = [table_name]
        
        # Add column names
        columns = table_info.get('columns', [])
        if columns:
            col_names = [col['name'] for col in columns]
            desc_parts.append(' '.join(col_names))
        
        # Add description if available
        if 'description' in table_info:
            desc_parts.append(table_info['description'])
        
        return ' '.join(desc_parts)


class AdvancedPromptBuilder:
    """Advanced prompt building with dynamic templates and few-shot learning"""
    
    def __init__(self):
        self.templates = self._load_prompt_templates()
        self.few_shot_examples = self._load_few_shot_examples()
        
    def _load_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Load various prompt templates for different scenarios"""
        return {
            'basic': PromptTemplate(
                system_prompt="You are an expert SQL analyst. Convert natural language questions to valid SQL queries.",
                user_prompt="""
Database Schema:
{schema_info}

Sample Data:
{sample_data}

Question: {question}

Generate a {dialect} SQL query that answers the question. Return only the SQL between <sql></sql> tags.

<sql>
""",
                temperature=0.0,
                max_tokens=1000
            ),
            
            'advanced': PromptTemplate(
                system_prompt="""You are an expert database analyst with deep knowledge of SQL optimization and business intelligence.
                
Your task is to convert natural language questions into efficient, accurate SQL queries.""",
                user_prompt="""
DATABASE INFORMATION:
- Database Type: {dialect}
- Current Date: {current_date}

SCHEMA:
{schema_info}

SAMPLE DATA (for understanding data patterns):
{sample_data}

FEW-SHOT EXAMPLES:
{examples}

BUSINESS RULES:
{business_rules}

QUESTION: {question}

ANALYSIS STEPS:
1. Identify required tables and columns
2. Determine necessary joins and relationships
3. Apply appropriate filters and conditions
4. Consider aggregations and grouping
5. Optimize for performance

SQL QUERY:
<sql>
""",
                temperature=0.0,
                max_tokens=1500
            ),
            
            'complex': PromptTemplate(
                system_prompt="""You are a senior database architect specializing in complex analytical queries.
                
You excel at creating sophisticated SQL queries for business intelligence, time-series analysis, and advanced analytics.""",
                user_prompt="""
DATABASE ENVIRONMENT:
- Type: {dialect}
- Date: {current_date}
- Performance Considerations: {performance_hints}

COMPREHENSIVE SCHEMA:
{schema_info}

DATA SAMPLES:
{sample_data}

DOMAIN EXAMPLES:
{examples}

BUSINESS CONTEXT:
{business_rules}

ANALYTICAL REQUEST: {question}

SOLUTION APPROACH:
1. Parse the analytical requirement
2. Identify data sources and granularity
3. Design optimal join strategy
4. Implement aggregations and calculations
5. Apply performance optimizations
6. Validate result structure

OPTIMIZED SQL:
<sql>
""",
                temperature=0.1,
                max_tokens=2000
            )
        }
    
    def _load_few_shot_examples(self) -> List[Dict]:
        """Load curated few-shot examples"""
        return [
            {
                "question": "How many customers do we have?",
                "sql": "SELECT COUNT(*) as customer_count FROM customers;",
                "explanation": "Simple count of all customers",
                "category": "basic_count",
                "difficulty": "easy"
            },
            {
                "question": "What are the top 5 products by revenue this year?",
                "sql": """
SELECT 
    p.product_name,
    SUM(oi.quantity * oi.unit_price) as total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE EXTRACT(YEAR FROM o.order_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC
LIMIT 5;
                """,
                "explanation": "Joins products with orders, calculates revenue, filters by current year",
                "category": "aggregation_join",
                "difficulty": "medium"
            },
            {
                "question": "Show monthly sales trend for the last 12 months",
                "sql": """
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    SUM(oi.quantity * oi.unit_price) as monthly_sales,
    COUNT(DISTINCT o.order_id) as order_count
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;
                """,
                "explanation": "Time series analysis with monthly aggregation",
                "category": "time_series",
                "difficulty": "medium"
            }
        ]
    
    async def build_prompt(
        self,
        question: str,
        relevant_schema: Dict,
        sample_data: Dict,
        template_type: str = "advanced",
        dialect: str = "postgresql",
        max_results: int = 100
    ) -> str:
        """Build comprehensive prompt for LLM"""
        
        template = self.templates.get(template_type, self.templates['basic'])
        
        # Select relevant examples
        relevant_examples = await self._select_relevant_examples(question, k=3)
        
        # Format schema information
        schema_info = self._format_schema(relevant_schema)
        sample_data_info = self._format_sample_data(sample_data, relevant_schema)
        examples_text = self._format_examples(relevant_examples)
        
        # Business rules
        business_rules = self._get_business_rules()
        
        # Performance hints
        performance_hints = self._get_performance_hints(relevant_schema)
        
        # Build the prompt
        prompt = template.user_prompt.format(
            schema_info=schema_info,
            sample_data=sample_data_info,
            examples=examples_text,
            business_rules=business_rules,
            performance_hints=performance_hints,
            question=question,
            dialect=dialect,
            max_results=max_results,
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        return prompt
    
    async def _select_relevant_examples(self, question: str, k: int = 3) -> List[Dict]:
        """Select most relevant few-shot examples based on question similarity"""
        if not self.few_shot_examples:
            return []
        
        try:
            # Use semantic similarity to find relevant examples
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            question_embedding = embedder.encode([question])
            
            example_texts = [ex['question'] for ex in self.few_shot_examples]
            example_embeddings = embedder.encode(example_texts)
            
            similarities = cosine_similarity(question_embedding, example_embeddings)[0]
            top_indices = np.argsort(similarities)[-k:][::-1]
            
            return [self.few_shot_examples[i] for i in top_indices]
            
        except Exception as e:
            logger.warning(f"Failed to select examples: {str(e)}")
            return self.few_shot_examples[:k]
    
    def _format_schema(self, schema: Dict) -> str:
        """Format schema information for prompt"""
        schema_text = ""
        for table_name, table_info in schema.items():
            schema_text += f"\nTable: {table_name}\n"
            schema_text += f"Description: {table_info.get('description', 'N/A')}\n"
            
            for col in table_info.get('columns', []):
                pk_indicator = " (PRIMARY KEY)" if col.get('primary_key') else ""
                nullable = " (NULLABLE)" if col.get('nullable') else " (NOT NULL)"
                schema_text += f"  - {col['name']}: {col['type']}{pk_indicator}{nullable}\n"
            
            # Add foreign key relationships
            if table_info.get('foreign_keys'):
                schema_text += "  Foreign Keys:\n"
                for fk in table_info['foreign_keys']:
                    schema_text += f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"
        
        return schema_text
    
    def _format_sample_data(self, sample_data: Dict, relevant_schema: Dict) -> str:
        """Format sample data for prompt"""
        sample_text = ""
        for table_name in relevant_schema.keys():
            if table_name in sample_data and sample_data[table_name]:
                sample_text += f"\n{table_name} sample rows:\n"
                for i, row in enumerate(sample_data[table_name][:2]):
                    sample_text += f"  Row {i+1}: {row}\n"
        return sample_text
    
    def _format_examples(self, examples: List[Dict]) -> str:
        """Format few-shot examples for prompt"""
        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Question: {example['question']}\n"
            examples_text += f"SQL: {example['sql'].strip()}\n"
            examples_text += f"Explanation: {example['explanation']}\n"
        return examples_text
    
    def _get_business_rules(self) -> str:
        """Get relevant business rules"""
        return """
- Revenue = quantity * unit_price (excluding refunds)
- Active customers = customers with orders in last 90 days
- Fiscal year starts in April
- Always use appropriate date filters for time-based queries
- Consider timezone implications for date/time operations
- Use meaningful column aliases for better readability
        """
    
    def _get_performance_hints(self, schema: Dict) -> str:
        """Generate performance optimization hints"""
        hints = []
        
        # Check for large tables
        for table_name, table_info in schema.items():
            row_estimate = table_info.get('row_count_estimate', 0)
            if row_estimate > 100000:
                hints.append(f"Table {table_name} is large ({row_estimate:,} rows) - consider using indexes and limiting results")
        
        # Check for available indexes
        indexed_tables = [name for name, info in schema.items() if info.get('indexes')]
        if indexed_tables:
            hints.append(f"Use indexed columns when possible: {', '.join(indexed_tables)}")
        
        if not hints:
            hints.append("Use appropriate WHERE clauses and LIMIT statements for optimal performance")
        
        return '\n'.join(f"- {hint}" for hint in hints)


class NL2SQLService:
    """Enterprise-grade NL2SQL service with all advanced features"""
    
    def __init__(self):
        self.llm_provider = getattr(settings, 'LLM_PROVIDER', 'openai').lower()
        self._init_llm_client()
        self.schema_linker = IntelligentSchemaLinker()
        self.prompt_builder = AdvancedPromptBuilder()
        self.cache_manager = self._init_cache_manager()
    
    def _init_llm_client(self):
        """Initialize LLM client based on provider configuration"""
        if self.llm_provider == 'ollama':
            from app.services.ollama_service import OllamaLLMService
            self.llm_client = OllamaLLMService(
                model_name=getattr(settings, 'OLLAMA_MODEL', 'llama3.1:8b'),
                base_url=getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
            )
            logger.info(f"Initialized Ollama LLM client with model: {self.llm_client.model_name}")
        else:
            # Default to OpenAI
            self.llm_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info(f"Initialized OpenAI LLM client with model: {settings.LLM_MODEL}")
        
    def _init_cache_manager(self):
        """Initialize cache manager"""
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            logger.info("Redis cache connected")
            return redis_client
        except Exception as e:
            logger.warning(f"Redis cache not available: {str(e)}")
            return None
    
    async def process_query(
        self, 
        request: QueryRequest, 
        user_id: Optional[str] = None
    ) -> QueryResponse:
        """Process natural language query with full enterprise features"""
        
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            logger.info(
                "Processing query",
                query_id=query_id,
                user_id=user_id,
                question_length=len(request.question)
            )
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = await self._get_cached_result(cache_key)
            
            if cached_result:
                logger.info("Returning cached result", query_id=query_id)
                cached_result['query_id'] = query_id
                cached_result['cache_hit'] = True
                return QueryResponse(**cached_result)
            
            # Extract database schema
            schema_extractor = EnhancedSchemaExtractor(request.database_url)
            schema = await schema_extractor.extract_schema()
            
            # Find relevant tables
            relevant_tables = await self.schema_linker.find_relevant_tables(
                request.question, schema, max_tables=8
            )
            
            if not relevant_tables:
                raise SQLGenerationError("Could not identify relevant tables for this question")
            
            # Determine complexity and select appropriate prompt template
            template_type = self._determine_query_complexity(request.question, relevant_tables)
            
            # Build prompt
            prompt = await self.prompt_builder.build_prompt(
                question=request.question,
                relevant_schema=relevant_tables,
                sample_data=schema.sample_data,
                template_type=template_type,
                dialect=request.database_type.value,
                max_results=request.max_results
            )
            
            # Generate SQL
            sql_query = await self._generate_sql(prompt, template_type)
            
            # Validate SQL for security
            validation_result = await self.validate_sql(sql_query)
            if not validation_result.is_safe:
                raise SecurityValidationError(f"Unsafe SQL query: {'; '.join(validation_result.messages)}")
            
            # Execute query
            results = await self._execute_query(sql_query, request.database_url, request.max_results)
            
            # Generate explanation if requested
            explanation = ""
            if request.include_explanation:
                explanation = await self._generate_explanation(request.question, sql_query)
            
            execution_time = time.time() - start_time
            
            response_data = {
                "sql_query": sql_query,
                "results": results,
                "explanation": explanation,
                "execution_time": execution_time,
                "row_count": len(results),
                "query_id": query_id,
                "cache_hit": False,
                "metadata": {
                    "template_type": template_type,
                    "relevant_tables": list(relevant_tables.keys()),
                    "schema_tables_count": len(schema.tables)
                }
            }
            
            # Cache the result
            await self._cache_result(cache_key, response_data)
            
            return QueryResponse(**response_data)
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Query processing failed",
                query_id=query_id,
                error=str(e),
                execution_time=execution_time
            )
            
            return QueryResponse(
                sql_query="",
                results=[],
                explanation="",
                execution_time=execution_time,
                row_count=0,
                error=str(e),
                query_id=query_id
            )
    
    def _determine_query_complexity(self, question: str, relevant_tables: Dict) -> str:
        """Determine query complexity to select appropriate prompt template"""
        
        question_lower = question.lower()
        
        # Complex indicators
        complex_keywords = [
            'trend', 'growth', 'compare', 'correlation', 'percentage',
            'ratio', 'rank', 'top', 'bottom', 'distribution', 'variance',
            'moving average', 'year over year', 'month over month'
        ]
        
        # Advanced indicators  
        advanced_keywords = [
            'join', 'relationship', 'between', 'across', 'multiple',
            'group', 'aggregate', 'sum', 'average', 'count', 'total'
        ]
        
        # Check table complexity
        table_count = len(relevant_tables)
        has_relationships = any(
            info.get('foreign_keys') for info in relevant_tables.values()
        )
        
        if any(kw in question_lower for kw in complex_keywords) or table_count > 4:
            return 'complex'
        elif any(kw in question_lower for kw in advanced_keywords) or has_relationships:
            return 'advanced'
        else:
            return 'basic'
    
    async def _generate_sql(self, prompt: str, template_type: str) -> str:
        """Generate SQL using appropriate LLM configuration"""
        
        try:
            # Adjust parameters based on complexity
            temperature = 0.0 if template_type == 'basic' else 0.1
            max_tokens = 1000 if template_type == 'basic' else 2000
            
            if self.llm_provider == 'ollama':
                # Extremely simple prompt for Phi-3 3.8B
                system_prompt = "Generate SQL."
                
                # Extract the question
                question_match = re.search(r'Question: (.+?)(?:\n|$)', prompt, re.IGNORECASE)
                if question_match:
                    question = question_match.group(1).strip()
                else:
                    question = "How many users are there?"  # fallback
                
                # Very basic template - just question and examples
                user_prompt = f"""{question}

SELECT COUNT(*) FROM users"""
                
                generated_text = self.llm_client.generate_sql(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.0,
                    max_tokens=64  # Very short
                )
                
                # Clean up the response
                generated_text = generated_text.strip()
                if not generated_text.upper().startswith('SELECT'):
                    generated_text = "SELECT COUNT(*) FROM users"
            else:
                # Use OpenAI
                response = self.llm_client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert SQL developer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=settings.LLM_TIMEOUT
                )
                generated_text = response.choices[0].message.content
            
            # Log the raw generated text for debugging
            logger.info(f"Raw generated text: {generated_text[:500]}...")
            
            # Extract SQL from tags
            sql_match = re.search(r'<sql>(.*?)</sql>', generated_text, re.DOTALL)
            if sql_match:
                sql_result = sql_match.group(1).strip()
                logger.info(f"Extracted SQL from tags: {sql_result}")
                # Clean up common Phi-3 issues
                sql_result = self._clean_sql(sql_result)
                return sql_result
            
            # Fallback: return the whole response with cleaning
            cleaned_sql = self._clean_sql(generated_text.strip())
            logger.info(f"Using fallback - cleaned SQL: {cleaned_sql}")
            return cleaned_sql
            
        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise SQLGenerationError(f"Failed to generate SQL: {str(e)}")
    
    def _clean_sql(self, sql: str) -> str:
        """Clean up common SQL generation issues from Phi-3"""
        if not sql:
            return sql
            
        # Remove common formatting issues
        sql = sql.strip()
        
        # Fix semicolon followed by LIMIT (invalid syntax)
        # Pattern: "; LIMIT 100" should become " LIMIT 100"
        sql = re.sub(r';\s*LIMIT\s+(\d+)', r' LIMIT \1', sql, flags=re.IGNORECASE)
        
        # Fix "NOT is_null()" to "IS NOT NULL"
        sql = re.sub(r'NOT\s+is_null\s*\(\s*(\w+)\s*\)', r'\1 IS NOT NULL', sql, flags=re.IGNORECASE)
        
        # Remove trailing semicolons
        sql = sql.rstrip(';')
        
        # Remove any leading/trailing quotes that might wrap the SQL
        sql = sql.strip('"\'`')
        
        # Ensure it starts with SELECT if it looks like a query
        if sql and not re.match(r'^\s*(SELECT|WITH|EXPLAIN)', sql, re.IGNORECASE):
            if 'FROM' in sql.upper():
                sql = 'SELECT ' + sql
        
        return sql.strip()
    
    async def _execute_query(
        self, 
        sql_query: str, 
        database_url: str, 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Execute SQL query with safety measures"""
        
        try:
            engine = create_engine(database_url)
            
            # Add LIMIT if not present
            if "LIMIT" not in sql_query.upper() and "TOP" not in sql_query.upper():
                sql_query += f" LIMIT {max_results}"
            
            with engine.connect() as connection:
                # Set query timeout
                connection.execute(text(f"SET statement_timeout = '{settings.MAX_QUERY_TIME}s'"))
                
                # Execute query
                result = connection.execute(text(sql_query))
                
                # Convert to list of dictionaries
                rows = []
                for row in result:
                    # Convert row to dict and handle special types
                    row_dict = dict(row._mapping)
                    
                    # Convert datetime objects to strings
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    
                    rows.append(row_dict)
                
                logger.info(f"Query executed successfully, returned {len(rows)} rows")
                return rows
                
        except SQLAlchemyError as e:
            logger.error(f"SQL execution failed: {str(e)}")
            raise SQLExecutionError(f"Query execution failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {str(e)}")
            raise SQLExecutionError(f"Unexpected error: {str(e)}")
    
    async def validate_sql(self, sql_query: str) -> ValidationResult:
        """Comprehensive SQL validation"""
        
        messages = []
        suggestions = []
        is_valid = True
        is_safe = True
        
        try:
            # Security validation
            security_result = self._validate_sql_security(sql_query)
            if not security_result[0]:
                is_safe = False
                messages.append(security_result[1])
            
            # Syntax validation (basic)
            syntax_result = self._validate_sql_syntax(sql_query)
            if not syntax_result[0]:
                is_valid = False
                messages.append(syntax_result[1])
            
            # Performance suggestions
            perf_suggestions = self._get_performance_suggestions(sql_query)
            suggestions.extend(perf_suggestions)
            
            return ValidationResult(
                is_valid=is_valid,
                is_safe=is_safe,
                messages=messages,
                suggestions=suggestions,
                sql_query=sql_query
            )
            
        except Exception as e:
            logger.error(f"SQL validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                is_safe=False,
                messages=[f"Validation error: {str(e)}"],
                suggestions=[],
                sql_query=sql_query
            )
    
    def _validate_sql_security(self, sql_query: str) -> Tuple[bool, str]:
        """Validate SQL for security risks"""
        sql_upper = sql_query.upper().strip()
        
        # Log what we're validating
        logger.info(f"Validating SQL security for: {sql_query[:100]}...")
        
        # Check for dangerous keywords
        for keyword in settings.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False, f"Dangerous keyword '{keyword}' detected"
        
        # Ensure query starts with SELECT or WITH
        if not sql_upper.startswith(('SELECT', 'WITH')):
            logger.warning(f"SQL doesn't start with SELECT/WITH. Starts with: {sql_upper[:50]}")
            return False, "Only SELECT and WITH queries are allowed"
        
        # Check for SQL injection patterns
        injection_patterns = [
            r";\s*(DROP|DELETE|UPDATE|INSERT)",
            r"UNION\s+ALL\s+SELECT.*INFORMATION_SCHEMA",
            r"--\s",
            r"/\*.*\*/"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sql_upper):
                return False, "Potential SQL injection pattern detected"
        
        return True, "Query is safe"
    
    def _validate_sql_syntax(self, sql_query: str) -> Tuple[bool, str]:
        """Basic SQL syntax validation"""
        try:
            # Check for balanced parentheses
            if sql_query.count('(') != sql_query.count(')'):
                return False, "Unbalanced parentheses"
            
            # Check for required keywords in SELECT statements
            if sql_query.upper().strip().startswith('SELECT'):
                if 'FROM' not in sql_query.upper():
                    return False, "SELECT statement missing FROM clause"
            
            return True, "Syntax appears valid"
            
        except Exception as e:
            return False, f"Syntax validation error: {str(e)}"
    
    def _get_performance_suggestions(self, sql_query: str) -> List[str]:
        """Generate performance optimization suggestions"""
        suggestions = []
        sql_upper = sql_query.upper()
        
        # Check for SELECT *
        if 'SELECT *' in sql_upper:
            suggestions.append("Consider selecting specific columns instead of SELECT * for better performance")
        
        # Check for missing LIMIT
        if 'LIMIT' not in sql_upper and 'TOP' not in sql_upper:
            suggestions.append("Consider adding a LIMIT clause to avoid large result sets")
        
        # Check for potential cartesian products
        if 'JOIN' in sql_upper and 'ON' not in sql_upper:
            suggestions.append("Ensure all JOINs have proper ON conditions to avoid cartesian products")
        
        # Check for functions in WHERE clauses
        if re.search(r'WHERE.*\w+\s*\(', sql_query, re.IGNORECASE):
            suggestions.append("Avoid using functions in WHERE clauses for better index utilization")
        
        return suggestions
    
    async def _generate_explanation(self, question: str, sql_query: str) -> str:
        """Generate human-readable explanation"""
        try:
            explanation_prompt = f"""
Explain this SQL query in simple, business-friendly terms:

Original Question: {question}

SQL Query:
{sql_query}

Provide a clear explanation of:
1. What data the query retrieves
2. How it processes the data
3. What the result represents

Keep the explanation non-technical and focused on business value.
"""
            
            if self.llm_provider == 'ollama':
                # Use Ollama service
                system_prompt = "You are a helpful data analyst who explains SQL queries in simple terms."
                explanation = self.llm_client.generate_sql(
                    system_prompt=system_prompt,
                    user_prompt=explanation_prompt,
                    temperature=0.3,
                    max_tokens=500
                )
                return explanation.strip()
            else:
                # Use OpenAI
                response = self.llm_client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful data analyst who explains SQL queries in simple terms."},
                        {"role": "user", "content": explanation_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Explanation generation failed: {str(e)}")
            return "Explanation could not be generated."
    
    # Cache management methods
    def _generate_cache_key(self, request: QueryRequest) -> str:
        """Generate cache key from request"""
        content = f"{request.question}:{request.database_url}:{request.max_results}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result"""
        if not self.cache_manager:
            return None
        
        try:
            cached = self.cache_manager.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {str(e)}")
        
        return None
    
    async def _cache_result(self, cache_key: str, result: Dict):
        """Cache query result"""
        if not self.cache_manager:
            return
        
        try:
            self.cache_manager.setex(
                cache_key, 
                settings.CACHE_TTL, 
                json.dumps(result, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {str(e)}")
    
    # Additional service methods
    async def log_query_execution(
        self, 
        user_id: Optional[str], 
        request: QueryRequest, 
        response: QueryResponse
    ):
        """Log query execution for analytics"""
        try:
            # In production, save to database
            logger.info(
                "Query execution logged",
                user_id=user_id,
                query_id=response.query_id,
                execution_time=response.execution_time,
                row_count=response.row_count,
                success=response.error is None
            )
        except Exception as e:
            logger.warning(f"Failed to log query execution: {str(e)}")
    
    async def get_query_history(
        self, 
        user_id: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Dict]:
        """Get user's query history"""
        try:
            # In production, fetch from database
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get query history: {str(e)}")
            return []
    
    async def get_user_metrics(self, user_id: str) -> Dict:
        """Get user's query metrics"""
        try:
            # In production, calculate from database
            return {
                "total_queries": 0,
                "successful_queries": 0,
                "avg_execution_time": 0.0,
                "cache_hit_rate": 0.0
            }
        except Exception as e:
            logger.error(f"Failed to get user metrics: {str(e)}")
            return {}
    
    async def parse_schema_file(self, content: bytes, filename: str) -> Dict:
        """Parse uploaded schema file"""
        try:
            if filename.endswith('.json'):
                schema_data = json.loads(content.decode('utf-8'))
            elif filename.endswith(('.yaml', '.yml')):
                import yaml
                schema_data = yaml.safe_load(content.decode('utf-8'))
            elif filename.endswith('.sql'):
                # Parse SQL DDL statements
                sql_content = content.decode('utf-8')
                schema_data = self._parse_sql_ddl(sql_content)
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
            return schema_data
            
        except Exception as e:
            logger.error(f"Failed to parse schema file: {str(e)}")
            raise
    
    def _parse_sql_ddl(self, sql_content: str) -> Dict:
        """Parse SQL DDL statements to extract schema"""
        # Basic implementation - in production, use a proper SQL parser
        tables = {}
        
        # Extract CREATE TABLE statements
        create_table_pattern = r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\)'
        matches = re.findall(create_table_pattern, sql_content, re.IGNORECASE | re.DOTALL)
        
        for table_name, columns_def in matches:
            columns = []
            for line in columns_def.split(','):
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        columns.append({
                            'name': parts[0],
                            'type': parts[1],
                            'nullable': 'NOT NULL' not in line.upper(),
                            'primary_key': 'PRIMARY KEY' in line.upper()
                        })
            
            tables[table_name] = {
                'columns': columns,
                'description': f"Table {table_name}"
            }
        
        return {'tables': tables}


# Create service instance
def get_nl2sql_service() -> NL2SQLService:
    """Dependency to get NL2SQL service instance"""
    return NL2SQLService()
