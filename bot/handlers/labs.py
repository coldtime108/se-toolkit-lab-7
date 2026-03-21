async def handle_labs(lms_client):
    try:
        items = await lms_client.get("/items/")
        labs = [item["title"] for item in items if item.get("type") == "lab"]
        if not labs:
            return "⚠️ No labs found."
        return "📋 Available labs:\n" + "\n".join(f"- {title}" for title in labs)
    except Exception as e:
        return f"❌ Failed to fetch labs: {e}"
