import pytest
import json
import asyncio
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from hello_django.routing import application

PADDLE_SPEED = 5
BALL_SPEED = 5
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_HEIGHT = 100

@pytest.mark.asyncio
class PongConsumerTest(TestCase):
    async def test_connect(self):
        # Create a communicator for the PongConsumer, simulating the websocket
        communicator = WebsocketCommunicator(application, "/ws/server_side_pong/")
        
        # Connect to the WebSocket
        connected, _ = await communicator.connect()
        assert connected

        # Receive the initial game state from the server
        response = await communicator.receive_json_from()
        assert 'players' in response
        assert 'ball' in response

        # Disconnect from the WebSocket
        await communicator.disconnect()

    async def test_paddle_movement(self):
        # Create a communicator for the PongConsumer, simulating the websocket
        communicator = WebsocketCommunicator(application, "/ws/server_side_pong/")
        
        # Connect to the WebSocket
        connected, _ = await communicator.connect()
        assert connected

        # Receive the initial game state from the server
        response = await communicator.receive_json_from()
        # print("Initial game state received:", response)  # Debugging output

        # Send movement message (player 1 moving up)
        move_message = {
            "player_id": "player1",
            "movement": "up"
        }

        await communicator.send_json_to(move_message)

		# Wait briefly to ensure the game state is updated
        # await asyncio.sleep(1)

        # Receive multiple messages to ensure we get the right one
        response = await communicator.receive_json_from()
        response2 = await communicator.receive_json_from()

        # Use the latest message (or compare both)
        response = response2

        # print("Updated game state received:", response)  # Debugging output
        updated_player_y = response['players']['player1']['y']

        # Check that player 1 moved up by PADDLE_SPEED
        expected_y = (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2) - PADDLE_SPEED
        assert updated_player_y == expected_y, (
    	f"Expected player Y position to be {expected_y}, but got {updated_player_y} instead."
		)


        # Disconnect from the WebSocket
        await communicator.disconnect()

    async def test_ball_movement(self):
        # Create a communicator for the PongConsumer, simulating the websocket
        communicator = WebsocketCommunicator(application, "/ws/server_side_pong/")
        
        # Connect to the WebSocket
        connected, _ = await communicator.connect()
        assert connected

        # Receive the initial game state from the server
        await communicator.receive_json_from()

        # Let the game loop run for a short period to move the ball
        await asyncio.sleep(0.1)

        # Receive the updated game state from the server
        response = await communicator.receive_json_from()
        ball_position = response['ball']

        # Check if the ball's position has updated
        assert ball_position['x'] != SCREEN_WIDTH / 2 or ball_position['y'] != SCREEN_HEIGHT / 2

        # Disconnect from the WebSocket
        await communicator.disconnect()