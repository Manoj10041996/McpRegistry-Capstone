from fastapi import FastAPI
from app.registry.routes import router as registry_router

app=FastAPI(title="Agent Platform")
app.include_router(registry_router)

@app.get("/health")
def health()->dict[str,str]:
    return {"status":"ok"}