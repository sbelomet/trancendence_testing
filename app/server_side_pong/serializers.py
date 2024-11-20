from rest_framework import serializers
from server_side_pong.models import Game, GamePlayer

class GamePlayerSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()  # Dynamically resolve the player details

    class Meta:
        model = GamePlayer
        fields = ['player', 'score']

    def get_player(self, obj):
        # Import UserDetailSerializer dynamically here
        from users.serializers import UserDetailSerializer
        serializer = UserDetailSerializer(obj.player, context=self.context)
        return serializer.data

class GameSerializer(serializers.ModelSerializer):
    players = GamePlayerSerializer(source='gameplayer_set', many=True)
    winner = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['id', 'rounds_needed', 'start_time', 'end_time', 'status', 'players', 'winner']

    def get_winner(self, obj):
        if obj.winner:
            # Import UserDetailSerializer dynamically
            from users.serializers import UserDetailSerializer
            serializer = UserDetailSerializer(obj.winner, context=self.context)
            return serializer.data
        return None
