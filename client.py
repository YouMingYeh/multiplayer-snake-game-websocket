import asyncio
import websockets
import json
import random

map = []
snakes = {}  # dictionary of snake positions
foods = []  # list of food positions


def direction_to_string(direction):
    if direction == [0, -1]:
        return "up"
    if direction == [0, 1]:
        return "down"
    if direction == [-1, 0]:
        return "left"
    if direction == [1, 0]:
        return "right"
    return None


FRAME_RATE = 0.1


async def send_messages(websocket):
    while True:
        global map
        global player_id
        global snakes
        global foods

        # Find the player's current position
        player_pos = None
        player_direction = None
        if str(player_id) in snakes.keys():
            player_pos = snakes[str(player_id)]["body"][0]
            player_direction = direction_to_string(snakes[str(player_id)]["direction"])
        # If the player's position was not found, don't send a move message
        if player_pos is None or player_direction is None:
            await asyncio.sleep(FRAME_RATE)
            continue

        # Determine possible moves
        print(f"Player position: {player_pos}")
        print(f"Player direction: {player_direction}")
        directions = []
        if (
            player_pos[0] > 0
            and (
                map[player_pos[0] - 1][player_pos[1]] == ""
                or map[player_pos[0] - 1][player_pos[1]] == "food"
            )
            and player_direction != "right"
        ):
            directions.append("left")
        if (
            player_pos[0] < len(map) - 1
            and (
                map[player_pos[0] + 1][player_pos[1]] == ""
                or map[player_pos[0] + 1][player_pos[1]] == "food"
            )
            and player_direction != "left"
        ):
            directions.append("right")
        if (
            player_pos[1] > 0
            and (
                map[player_pos[0]][player_pos[1] - 1] == ""
                or map[player_pos[0]][player_pos[1] - 1] == "food"
            )
            and player_direction != "down"
        ):
            directions.append("up")
        if (
            player_pos[1] < len(map[0]) - 1
            and (
                map[player_pos[0]][player_pos[1] + 1] == ""
                or map[player_pos[0]][player_pos[1] + 1] == "food"
            )
            and player_direction != "up"
        ):
            directions.append("down")

        # If there are no possible moves, don't send a move message
        if not directions:
            await asyncio.sleep(FRAME_RATE)
            continue

        # Choose a random direction from the possible moves
        random_direction = random.choice(directions)
        print(f"Moving {random_direction}")
        message = {"type": "move", "direction": random_direction}
        await websocket.send(json.dumps(message))
        await asyncio.sleep(FRAME_RATE)  # pause for a second between messages


async def receive_messages(websocket):
    async for message in websocket:
        data = json.loads(message)
        if data["type"] == "state":
            global map
            global snakes
            global foods
            map = data["map"]
            snakes = data["snakes_pos"]
            foods = data["foods_pos"]


player_id = None


async def connect():
    global player_id
    uri = "ws://localhost:6789"  # replace with your server's URI
    async with websockets.connect(uri) as websocket:
        register_message = {"type": "register"}
        await websocket.send(json.dumps(register_message))
        # wait for response
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            if data["type"] == "register":
                player_id = data["player_id"]
                print(f"Registered as player {player_id}")
                break

        send_task = asyncio.create_task(send_messages(websocket))
        receive_task = asyncio.create_task(receive_messages(websocket))

        # wait for either task to finish
        done, pending = await asyncio.wait(
            [send_task, receive_task], return_when=asyncio.FIRST_COMPLETED
        )

        # if one task finishes, cancel the other
        for task in pending:
            task.cancel()


# start the connection
asyncio.get_event_loop().run_until_complete(connect())
