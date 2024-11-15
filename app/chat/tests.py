from django.test import TestCase
from .models import Message

class MessageModelTest(TestCase):

    def setUp(self):
        self.message1 = Message.objects.create(
            username='user1',
            room='room1',
            content='Hello, this is a test message.',
        )
        self.message2 = Message.objects.create(
            username='user2',
            room='room1',
            content='Another test message.',
        )

    def test_message_creation(self):
        self.assertEqual(self.message1.username, 'user1')
        self.assertEqual(self.message1.room, 'room1')
        self.assertEqual(self.message1.content, 'Hello, this is a test message.')
        self.assertIsNotNone(self.message1.date_added)

        self.assertEqual(self.message2.username, 'user2')
        self.assertEqual(self.message2.room, 'room1')
        self.assertEqual(self.message2.content, 'Another test message.')
        self.assertIsNotNone(self.message2.date_added)

    def test_message_ordering(self):
        messages = Message.objects.all()
        self.assertEqual(messages[0], self.message1)
        self.assertEqual(messages[1], self.message2)