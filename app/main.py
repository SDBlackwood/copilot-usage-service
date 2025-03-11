from fastapi import FastAPI

app = FastAPI()


@app.get("/usage")
async def get_usage():
    return {"usage": [
        {
            "message_id": 123,
            "timestamp": "2021-01-01T00:00:00Z",
            "report_name": "Report 1",
            "credits_used": 100
        },
        {
            "message_id": 124,
            "timestamp": "2021-01-01T00:00:00Z",
            "report_name": "Report 2",
            "credits_used": 200
        }
    ]}
