# Multiplayer Snake Game using Python and Socket Programming
## Description
This is a simple multiplayer snake game using python and socket programming. The game is run on a server and multiple clients can connect to the server to play the game. The server is responsible for handling the game logic and broadcasting the game state to all the clients. The clients are responsible for controlling the snake using code. Also, there is a simple UI for the clients to see the game state.
## Demo
![demo](<demo.gif>)
## Installation
1. Clone the repository
```bash
git clone https://github.com/YouMingYeh/multiplayer-snake-game-websocket
```
2. Install the required packages
```bash
pip install -r requirements.txt
```
## Usage
1. Start the server
```bash
python server.py
```
2. Start the clients
```bash
python client.py # for each client
```
3. Open the UI in the browser
```bash
http://localhost:3000
```
