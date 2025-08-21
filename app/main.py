from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv




# ---------------------------
# Load .env
# ---------------------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
PORT = int(os.getenv("PORT", "8000"))

if not MONGO_URI:
    raise RuntimeError("MONGO_URI ناقص فملف .env")

# ---------------------------
# MongoDB
# ---------------------------
client = AsyncIOMotorClient(MONGO_URI)
db = client["tinabox"]

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(title="Tinabox API", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Tinabox API is running 🚀"}
# ---------------------------
# Schemas
# ---------------------------
class CreateCollectionIn(BaseModel):
    name: str
    visibility: str

# ---------------------------
# Startup: create index
# ---------------------------
@app.on_event("startup")
@app.on_event("startup")
async def startup():
    await db["collections"].create_index(
        "name_lc",
        name="name_lc_unique",
        unique=True
    )
    print("[mongo] index ensured: collections(name_lc UNIQUE)")


# ---------------------------
# Health check
# ---------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/mongo-ping")
async def mongo_ping():
    return await db.command("ping")

# ---------------------------
# Collections
# ---------------------------
@app.post("/v1/collections")
async def create_collection(payload: CreateCollectionIn):
    doc = {
        "name": payload.name,
        "name_lc": payload.name.lower(),
        "visibility": payload.visibility,
    }
    try:
        await db["collections"].insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "collection created", "data": doc}

@app.get("/v1/collections")
async def list_collections():
    cursor = db["collections"].find({}, {"_id": 0})
    return [doc async for doc in cursor]

@app.get("/v1/collections/{name}")
async def get_collection(name: str):
    doc = await db["collections"].find_one({"name_lc": name.lower()}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Collection not found")
    return doc
