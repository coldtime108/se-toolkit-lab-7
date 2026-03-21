async def handle_health(lms_client):
    try:
        items = await lms_client.get("/items/")
        count = len(items)
        return f"✅ Backend is healthy and running. Items in database: {count}"
    except Exception as e:
        return f"❌ Backend error: {e}"
