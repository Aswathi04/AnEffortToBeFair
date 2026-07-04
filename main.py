from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, train, debias_router, explain
import routers.gemini_router as gemini_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(train.router, tags=["Audit"])
app.include_router(debias_router.router, tags=["Debias"])
app.include_router(gemini_router.router, tags=["Explain"])

@app.get("/")
async def health():
    return {"status": "Sentinel AI Backend Active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
