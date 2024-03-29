import asyncio
import socketio
import random
import json
# Create a Socket.IO client
sio = socketio.AsyncClient()

# Global variables for game state
map = []
snakes = {}  # Dictionary of snake positions
foods = []  # List of food positions
player_id = None  # To be set upon registration
FRAME_RATE = 0.1  # Time between moves

# Function to convert direction array to string
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

# Event handler for successful connection
@sio.event
async def connect():
    print("Connected to the server")
    player_id = input("Please enter your player ID: ")
    await sio.emit("register", {"player_id": player_id})

# Event handler for disconnection
@sio.event
async def disconnect():
    print("Disconnected from the server")

# Event handler for receiving game state updates
@sio.event
async def state(data):
    global map, snakes, foods
    data = json.loads(data)
    map = data["map"]
    snakes = data["snakes_pos"]
    foods = data["foods_pos"]
    # if player_id is not in snakes.keys(), disconnect
    if player_id is None: return
    if str(player_id) not in snakes.keys():
        await sio.emit("exit")
        await sio.disconnect()


# Event handler for handling registration confirmation
@sio.event
async def register(data):
    print("Registered as player", data["player_id"])
    global player_id
    player_id = data["player_id"]
    print(f"Registered as player {player_id}")
    # After registration, start sending moves
    asyncio.create_task(send_moves())

# Coroutine to send move commands based on the game state
async def send_moves():
    
    while True:
        global map, snakes, player_id, foods
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
        print(f"Sending move: {random_direction}")
        message = {"type": "move", "direction": random_direction}
        await sio.emit("move", message)
        await asyncio.sleep(FRAME_RATE)  # pause for a second between messages

# Main coroutine to connect to the server
async def main():
    await sio.connect('https://ntuim-multiplayer-snake-game-server.azurewebsites.net/')
    # await sio.connect('http://localhost:3000')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
