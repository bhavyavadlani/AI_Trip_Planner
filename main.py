from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from utils.save_to_document import save_document
from starlette.responses import JSONResponse
import os
import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class QueryRequest(BaseModel):
    question: str
    model_provider: str = "groq"

@app.post("/query")
async def query_travel_agent(query: QueryRequest):#
    try:
        print(f"Received query: {query}")
        provider = query.model_provider if query.model_provider in ["groq", "openai"] else "groq"
        graph = GraphBuilder(model_provider=provider)
        react_app = graph()

        try:
            png_graph = react_app.get_graph().draw_mermaid_png()
            with open("my_graph.png", "wb") as f:
                f.write(png_graph)
            print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        except Exception as graph_err:
            print(f"Could not generate graph visualization: {graph_err}")

        # Invoke the LangGraph agent workflow
        messages = {"messages": [query.question]}
        output = react_app.invoke(messages)

        # If result is dict with messages:
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
        else:
            final_output = str(output)
        
        # Save the plan to output document
        saved_file = save_document(final_output)
        
        return {
            "answer": final_output,
            "saved_file": saved_file
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
