import os
import sys
from dotenv import load_dotenv

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables (LangSmith configs & API keys)
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes

from agents.graph import aria_graph, ARIAInput, ARIAOutput

app = FastAPI(
    title="ARIA Multi-Agent Orchestra API",
    version="1.0.0",
    description="LangServe REST API and LangSmith-traced microservice for ARIA Multi-Agent Analytics Platform.",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint for container and deployment orchestration."""
    return {
        "status": "healthy",
        "service": "ARIA Orchestra LangServe API",
        "langsmith_tracing": os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
        "langsmith_project": os.getenv("LANGCHAIN_PROJECT", "ARIA-Orchestra")
    }

# Mount the ARIA LangGraph multi-agent workflow
add_routes(
    app,
    aria_graph,
    path="/aria",
    input_type=ARIAInput,
    output_type=ARIAOutput,
    enable_feedback_endpoint=True,
)

if __name__ == "__main__":
    import uvicorn
    print("Starting ARIA LangServe microservice on http://localhost:8000 ...")
    print("Interactive Playground available at: http://localhost:8000/aria/playground")
    print("OpenAPI Specification available at: http://localhost:8000/docs")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
