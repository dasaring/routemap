from sanic import Sanic
from sanic.response import json

app = Sanic("MyApp")


@app.get("/health")
async def health_check(request):
    return json({"status": "ok"})


@app.get("/users")
async def list_users(request):
    return json({"users": []})


@app.post("/users")
async def create_user(request):
    return json({"created": True}, status=201)


@app.get("/users/<user_id:int>")
async def get_user(request, user_id):
    return json({"id": user_id})


@app.put("/users/<user_id:int>")
async def update_user(request, user_id):
    return json({"updated": True})


@app.delete("/users/<user_id:int>")
async def delete_user(request, user_id):
    return json({}, status=204)


@app.route("/items", methods=["GET", "POST"])
async def items(request):
    if request.method == "GET":
        return json({"items": []})
    return json({"created": True}, status=201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
