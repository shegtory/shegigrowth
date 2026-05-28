from database import mark_target_done
def handler(request):
    if request.method == "POST":
        body = request.json
        user_id = body.get("user_id")
        account_id = body.get("account_id")
        if not user_id or not account_id:
            return {"error": "missing fields"}, 400
        mark_target_done(user_id, account_id)
        return {"status": "done"}
    return {"error": "method not allowed"}, 405
