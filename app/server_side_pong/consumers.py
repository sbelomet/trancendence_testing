import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from jsonschema import validate, ValidationError
import logging
logging.basicConfig(level=logging.DEBUG)


PADDLE_SPEED = 5
BALL_SPEED = 5
BALL_RADIUS = 10
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_HEIGHT = 100

class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		#Accept the WebSocket connection
		await self.accept()
		# InitialIze the game state (you can adapt this to fit you needs)
		self.game_state = {
		'ball': {'x': SCREEN_WIDTH / 2, 'y': SCREEN_HEIGHT / 2, 'vx': BALL_SPEED, 'vy': BALL_SPEED},
			'players': {
				"player1": {"x": 50, "y": (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2)},
					'player2': {'x': SCREEN_WIDTH - 50, 'y': (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2)}
		   }
		}
    	# Send the initial game state to the client
		await self.send_game_state()

		# start the game loop
		asyncio.create_task(self.game_loop())

	async def disconnect(self, close_code):
		pass

	async def receive(self, text_data):
		# Parse the received JSON data
		data = json.loads(text_data)
		
		player_id = data.get("player_id")
		paddle_movement = data.get("movement")  # Should be either 'up' or 'down'

		# logging.debug(f"Before update: {self.game_state}")

		
		if player_id in self.game_state['players']:
			player = self.game_state['players'][player_id]
			if paddle_movement == 'up':
				player['y'] = max(player['y'] - PADDLE_SPEED, 0) #Don-t go above the screen
			elif paddle_movement == 'down':
				player['y'] = min(player['y'] + PADDLE_SPEED, SCREEN_HEIGHT - PADDLE_HEIGHT) #Don't go below the screen
		
		# logging.debug(f"After update: {self.game_state}")


		# Broadcast the updated game state
		await self.send_game_state()

	async def game_loop(self):
		while True:
			# Update ball position
			self.update_ball_position()
			
			# Broadcast updated game state
			await self.send_game_state()

			# Run at 60 frames per second
			await asyncio.sleep(1 / 60)
	
	def update_ball_position(self):
		ball = self.game_state['ball']

		#Update ball coordinates
		ball['x'] += ball["vx"]
		ball['y'] += ball['vy']

		#check for collision with top or bottom wall
		if ball['y'] <= 0 or ball['y'] >= SCREEN_HEIGHT:
			ball['vy'] = -ball["vy"]
		
		#Check for collIsion with paddles
		player1 = self.game_state['players']['player1']
		player2 = self.game_state['players']['player2']
		
		if (ball["x"] <= player1["x"] + BALL_RADIUS and player1["y"] <= ball["y"] <= player1["y"] + PADDLE_HEIGHT):
			ball["vx"] = -ball["vx"]

		if (ball["x"] >= player2["x"] - BALL_RADIUS and player2["y"] <= ball["y"] <= player2["y"] + PADDLE_HEIGHT):
			ball["vx"] = -ball["vx"]
		
		# Check for scoring (ball going out of bounds)
		if ball["x"] < 0 or ball["x"] > SCREEN_WIDTH:
            # Reset the ball position to the center
			ball["x"] = SCREEN_WIDTH / 2
			ball["y"] = SCREEN_HEIGHT / 2
			ball["vx"] = BALL_SPEED if ball["x"] < 0 else -BALL_SPEED
			ball["vy"] = BALL_SPEED
	
	async def send_game_state(self):
		# logging.debug(f"Sending game state: {self.game_state}")
		await self.send(text_data=json.dumps(self.game_state))
