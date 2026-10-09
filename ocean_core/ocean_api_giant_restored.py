"""
OCEAN CORE 8030 API
===================
Standalone FastAPI application - completely isolated from main.py

Port: 8030
Features:
- Query endpoint (natural language → intelligent response)
- Data sources status
- Knowledge exploration
- Curiosity threads
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

# Local imports
from data_sources import get_data_sources_manager
from external_apis import get_external_apis_manager
from query_processor import get_query_processor, QueryIntent
from knowledge_engine import get_knowledge_engine, KnowledgeResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ocean_api")

# Initialize FastAPI app
app = FastAPI(
    title="Curiosity Ocean 8030",
    description="Universal Knowledge Aggregation Engine - Completely Isolated",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
data_sources_manager = None
external_apis_manager = None
query_processor = None
knowledge_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize all managers on startup"""
    global data_sources_manager, external_apis_manager, query_processor, knowledge_engine
    
    logger.info("🌊 Ocean Core 8030 starting up...")
    
    try:
        # Initialize all managers in parallel
        data_sources_manager = await get_data_sources_manager()
        external_apis_manager = await get_external_apis_manager()
        query_processor = await get_query_processor()
        knowledge_engine = await get_knowledge_engine(data_sources_manager, external_apis_manager)
        
        logger.info("✅ Ocean Core 8030 initialized successfully")
    except Exception as e:
        logger.error(f"❌ Ocean Core 8030 initialization failed: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Curiosity Ocean 8030",
        "version": "2.0.0",
        "status": "operational",
        "uptime": "active",
        "description": "Universal Knowledge Aggregation Engine",
        "endpoints": [
            "/api/query - Natural language query",
            "/api/status - Service status",
            "/api/sources - Available data sources",
            "/api/threads/{topic} - Curiosity exploration",
            "/api/docs - OpenAPI documentation"
        ]
    }


@app.get("/api/status")
async def get_status():
    """Get service status"""
    if not data_sources_manager:
        return {"status": "initializing"}
    
    try:
        source_status = await data_sources_manager.get_source_status()
        
        return {
            "service": "Curiosity Ocean 8030",
            "status": "operational",
            "initialized": True,
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                name: {
                    "status": info.status,
                    "records": info.record_count,
                    "quality": info.quality_score,
                    "last_update": info.last_update
                }
                for name, info in source_status.items()
            },
            "components": {
                "data_sources": "operational",
                "external_apis": "operational",
                "query_processor": "operational",
                "knowledge_engine": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sources")
async def get_sources():
    """List available data sources"""
    if not data_sources_manager:
        raise HTTPException(status_code=503, detail="Service initializing")
    
    try:
        source_status = await data_sources_manager.get_source_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "internal_sources": {
                name: {
                    "type": info.source_type.value,
                    "status": info.status,
                    "records": info.record_count,
                    "quality_score": info.quality_score
                }
                for name, info in source_status.items()
            },
            "external_sources": [
                {
                    "name": "Wikipedia",
                    "api": "https://en.wikipedia.org/w/api.php",
                    "status": "operational"
                },
                {
                    "name": "Arxiv",
                    "api": "http://export.arxiv.org/api/query",
                    "status": "operational"
                },
                {
                    "name": "PubMed",
                    "api": "https://pubmed.ncbi.nlm.nih.gov/api/",
                    "status": "operational"
                },
                {
                    "name": "GitHub",
                    "api": "https://api.github.com",
                    "status": "operational"
                },
                {
                    "name": "DBpedia",
                    "api": "https://dbpedia.org/sparql",
                    "status": "operational"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Sources list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def query_ocean(
    question: str = Query(..., description="Natural language question"),
    include_external: bool = Query(True, description="Include external knowledge sources"),
    limit_results: int = Query(5, description="Limit results per source")
):
    """
    Query Ocean - Main intelligence endpoint
    
    Examples:
    - "What is the status of Elbasan laboratory?"
    - "How are the agents performing today?"
    - "What are the latest system metrics?"
    - "Tell me about neurogenesis and consciousness"
    """
    
    if not question or len(question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not query_processor or not knowledge_engine:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"🧠 Received query: {question}")
        
        # 1. Process query
        processed = await query_processor.process(question)
        
        # 2. Generate answer
        response = await knowledge_engine.answer_query(question, processed)
        
        # Convert dataclass to dict
        response_dict = {
            "query": response.query,
            "intent": response.intent,
            "response": response.main_response,
            "key_findings": response.key_findings,
            "sources": response.sources_cited,
            "confidence": response.confidence_score,
            "processing_time_ms": response.processing_time_ms,
            "curiosity_threads": [
                {
                    "topic": thread.topic,
                    "question": thread.initial_question,
                    "related_topics": thread.related_topics,
                    "continue_with": thread.continue_suggestions,
                    "sources": thread.sources_used
                }
                for thread in response.curiosity_threads
            ],
            "timestamp": response.timestamp
        }
        
        return response_dict
        
    except ValueError as e:
        logger.warning(f"Query validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/labs")
async def get_labs():
    """Get all location labs data"""
    if not data_sources_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        labs_data = await data_sources_manager.location_labs.get_all_labs_data()
        return labs_data
    except Exception as e:
        logger.error(f"Labs data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents")
async def get_agents():
    """Get all agent telemetry"""
    if not data_sources_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        agents_data = await data_sources_manager.agent_telemetry.get_all_agents_data()
        return agents_data
    except Exception as e:
        logger.error(f"Agents data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threads/{topic}")
async def get_curiosity_thread(topic: str):
    """Get curiosity threads for exploration"""
    
    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")
    
    # Map common topics to threads
    threads_map = {
        "laboratory": {
            "topic": "Geographic Laboratory Networks",
            "related": ["Elbasan", "Tirana", "Durrës", "Shkodër", "Vlorë", "Korça"],
            "explore": [
                "What domains are most active?",
                "Which locations have highest quality data?",
                "What's the correlation between lab domains?",
                "How are labs interconnected across countries?"
            ]
        },
        "agents": {
            "topic": "Agent Intelligence & Decisions",
            "related": ["ALBA", "ALBI", "Blerina", "AGIEM", "ASI"],
            "explore": [
                "What are the top agent decisions?",
                "Which agent has highest confidence?",
                "What anomalies were detected?",
                "How do agents coordinate?"
            ]
        },
        "system": {
            "topic": "System Infrastructure & Performance",
            "related": ["CPU", "Memory", "Latency", "Uptime"],
            "explore": [
                "What are current metrics?",
                "Are there performance bottlenecks?",
                "How's resource utilization?",
                "What's the trend over time?"
            ]
        }
    }
    
    thread = threads_map.get(topic.lower())
    
    if not thread:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found")
    
    return {
        "topic": thread["topic"],
        "related_entities": thread["related"],
        "explore_further": thread["explore"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ocean-core-8030",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🌊 Starting Curiosity Ocean 8030...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8030,
        log_level="info"
    )
