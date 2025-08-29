


import asyncio
import threading
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from supabase import acreate_client, AsyncClient

from cluster import clustered_data_visualization, elbow_method, clustered_family_income, common_program_enrolled, \
    cluster_student_profile
from exportExcel import export_data
from models import StudentInterface

app = FastAPI()

# Allow frontend to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()
# Supabase client setup
url =  os.getenv('SUPABASE_URL')
key =  os.getenv('SUPABASE_KEY')
SUPABASE: AsyncClient = None
df = []

data_updated = asyncio.Event()

# Handle Supabase real-time change
async def handle_record_inserted(payload):
    global df
    try:
        response = await SUPABASE.table("studentTable").select("*").execute()
        df = response.data
        print("📦 Updated Data from Supabase")
        data_updated.set()
    except Exception as e:
        print("❌ Error fetching data:", e)

# Setup and subscribe to real-time
async def initialize_supabase():
    global SUPABASE
    SUPABASE = await acreate_client(url, key)
    channel = SUPABASE.channel("student_changes")

    await channel.on_postgres_changes(
        event="*",
        schema="public",
        table="studentTable",
        callback=lambda payload: asyncio.create_task(handle_record_inserted(payload))
    ).subscribe()

    # Initial fetch
    try:
        response = await SUPABASE.table("studentTable").select("*").execute()
        global df
        df = response.data
        print("✅ Initial Data Loaded")
    except Exception as e:
        print("❌ Error during initial fetch:", e)

# Background thread for real-time listener
def start_realtime_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_supabase())
    loop.run_forever()

# Start background listener
threading.Thread(target=start_realtime_listener, daemon=True).start()

@app.get("/clustered-student-data")
def get_student_clustered_data():
    return clustered_data_visualization(df).to_dict(orient="records")

@app.get("/elbow-method")
def get_elbow_method_data():
    return elbow_method(df)

@app.get("/clustered-family-income")
def get_family_income_category():
    return clustered_family_income(df)

@app.get("/clustered-common-program")
def get_common_program_enrolled():
    return common_program_enrolled(df)

@app.get("/cluster-student-profile")
def get_clustered_student_profile():
    return cluster_student_profile(df)

@app.post("/export-data")
def export_student_data(list_of_students:List[StudentInterface]):
    return export_data(list_of_students)
