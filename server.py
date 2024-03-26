import asyncio
import websockets
import json
from aiohttp import web

from MultiplayerSnakeGame import MultiplayerSnakeGame

players = {}
game_active = False
next_player_id = 0
socks = set()
FRAME_RATE = 0.5

async def register_player(websocket):
    global next_player_id
    global players
    global game
    player_id = int(next_player_id)
    next_player_id += 1
    game.spawn_snake(player_id)
    players[websocket] = player_id
    return player_id


async def unregister_player(websocket):
    player_id = players.pop(websocket, None)
    if player_id is not None:
        game.remove_snake(player_id)


async def game_loop():
    global game_active
    global game
    print("Game loop started")
    while game_active:
        game.update()
        for websocket in players.keys():
            in_game_player_ids = [snake.player_id for snake in game.snakes]
            if players[websocket] not in in_game_player_ids:
                print(f"Player {players[websocket]} lost")
                await websocket.close()

        await asyncio.sleep(FRAME_RATE)


async def broadcast_loop():
    while True:
        await broadcast_game_state()
        await asyncio.sleep(0.1)


async def broadcast_game_state():
    global players
    global game
    global socks

    snakes_pos = {
        snake.player_id: {"body": snake.body, "direction": snake.direction}
        for snake in game.snakes
    }
    foods_pos = [food.position for food in game.foods]

    state = json.dumps(
        {
            "type": "state",
            "map": game.map,
            "snakes_pos": snakes_pos,
            "foods_pos": foods_pos,
        }
    )
    for sock in socks:
        await sock.send(state)


async def handle_message(websocket, message):
    global players
    global game
    data = json.loads(message)
    player_id = players[websocket]
    if data["type"] == "move":
        direction = (0, 0)
        if data["direction"] == "up":
            direction = (0, -1)
        elif data["direction"] == "down":
            direction = (0, 1)
        elif data["direction"] == "left":
            direction = (-1, 0)
        elif data["direction"] == "right":
            direction = (1, 0)

        game.change_direction(player_id, direction)
        return
    if data["type"] == "exit":
        await websocket.close()
        return


async def handle_connection(websocket, path):
    global players
    global game
    global sock

    socks.add(websocket)
    print(f"New connection: {websocket}")

    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "register":
                player_id = await register_player(websocket)
                print(f"New player registered: {player_id}")
                await websocket.send(
                    json.dumps({"type": "register", "player_id": player_id})
                )
            else:
                await handle_message(websocket, message)

    finally:
        await unregister_player(websocket)
        print(f"Connection closed: {websocket}")
        socks.remove(websocket)
        print(f"Remaining connections: {len(socks)}")
        
async def handle(request):
    with open('./index.html', 'r') as f:
        return web.Response(text=f.read(), content_type='text/html')


game = MultiplayerSnakeGame()
game_active = True

async def start_http_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3000)
    await site.start()

async def start_websocket_server():
    async with websockets.serve(handle_connection, "localhost", 6789):
        await asyncio.Future()  # Run forever


async def main():
    # Start the game and broadcast loops as background tasks
    asyncio.create_task(game_loop())
    asyncio.create_task(broadcast_loop())

    # Start both servers
    await asyncio.gather(
        start_http_server(),
        start_websocket_server(),
    )

asyncio.run(main())



