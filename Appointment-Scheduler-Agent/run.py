if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="src.main:app", port=5000, reload=True)

# from src.main import app
