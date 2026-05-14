from aiohttp import web


async def list_users(request):
    return web.json_response([])


async def create_user(request):
    data = await request.json()
    return web.json_response(data, status=201)


async def get_user(request):
    user_id = request.match_info['id']
    return web.json_response({'id': user_id})


async def update_user(request):
    user_id = request.match_info['id']
    data = await request.json()
    return web.json_response({'id': user_id, **data})


async def delete_user(request):
    return web.Response(status=204)


async def health_check(request):
    return web.json_response({'status': 'ok'})


app = web.Application()
app.router.add_get('/users', list_users)
app.router.add_post('/users', create_user)
app.router.add_get('/users/{id}', get_user)
app.router.add_put('/users/{id}', update_user)
app.router.add_delete('/users/{id}', delete_user)
app.router.add_route('GET', '/health', health_check)

if __name__ == '__main__':
    web.run_app(app, port=8080)
