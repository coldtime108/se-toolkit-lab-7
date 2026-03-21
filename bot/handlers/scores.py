async def handle_scores(lab, lms_client):
    if not lab:
        return "⚠️ Please specify a lab, e.g., /scores lab-04"

    lab_id = lab if lab.startswith("lab-") else f"lab-{lab}"
    try:
        data = await lms_client.get(f"/analytics/pass-rates?lab={lab_id}")
        if not data:
            return f"⚠️ No data found for {lab_id}."

        lines = []
        for item in data:
            task = item.get("task", "Unknown")
            avg_score = item.get("avg_score", 0)
            attempts = item.get("attempts", 0)
            lines.append(f"{task}: {avg_score}% ({attempts} attempts)")

        if not lines:
            return f"⚠️ No tasks found for {lab_id}."

        return f"📊 Scores for {lab_id}:\n" + "\n".join(lines)
    except Exception as e:
        return f"❌ Failed to fetch scores: {e}"
