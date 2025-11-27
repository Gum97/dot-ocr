#!/usr/bin/env python3
"""
Script to run the API server
"""
import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(description='Run dots.ocr API server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload (development)')
    parser.add_argument('--cpu', action='store_true', help='Force CPU mode')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    
    args = parser.parse_args()
    
    # Set environment variables
    if args.cpu:
        os.environ['DEVICE'] = 'cpu'
        print("🖥️  Running in CPU mode")
    
    # Import and run
    import uvicorn
    from api.main import app
    
    print("="*60)
    print("🚀 Starting dots.ocr API Server")
    print(f"📍 Host: {args.host}:{args.port}")
    print(f"📖 Docs: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/docs")
    print("="*60)
    
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info"
    )

if __name__ == "__main__":
    main()
