import os
import sys
import uvicorn

def main():
    print("=" * 70)
    print("  VERIDIAN IT ASSIST — Enterprise AI Support & Decision Platform")
    print("=" * 70)
    print("  Starting FastAPI Backend & Enterprise React Single-Page Application...")
    print("  - Web Console:        http://localhost:8000")
    print("  - API Documentation:  http://localhost:8000/docs")
    print("  - Health Check:       http://localhost:8000/api/health")
    print("=" * 70)
    
    # Run uvicorn on port 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
