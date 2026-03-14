"""
Conversation Context Manager — Multi-turn memory, pronoun resolution, topic tracking
"""
import re
from collections import deque


class ConversationContext:
    def __init__(self, max_history=20):
        self.history = deque(maxlen=max_history)
        self.last_player = None
        self.last_player_id = None
        self.last_team = None
        self.last_topic = None
        self.last_intent = None
        self.mentioned_players = []
        self.mentioned_teams = []

    def add_turn(self, role, message, intent=None, entities=None):
        self.history.append({
            'role': role, 'message': message,
            'intent': intent, 'entities': entities or {}
        })
        if role == 'assistant' and intent:
            self.last_intent = intent
        if entities:
            if entities.get('player_name'):
                self.last_player = entities['player_name']
                self.last_player_id = entities.get('player_id')
                if self.last_player not in self.mentioned_players:
                    self.mentioned_players.append(self.last_player)
            if entities.get('team_name'):
                self.last_team = entities['team_name']
                if self.last_team not in self.mentioned_teams:
                    self.mentioned_teams.append(self.last_team)

    def resolve_pronouns(self, message):
        """Replace pronouns with actual entity names from context"""
        msg = message
        pronoun_patterns = [
            (r'\b(him|his|he)\b', self.last_player),
            (r'\b(her|she)\b', self.last_player),
            (r'\b(them|they|their)\b', self.last_player),
            (r'\bthat player\b', self.last_player),
            (r'\bthis player\b', self.last_player),
            (r'\bthat team\b', self.last_team),
            (r'\bthis team\b', self.last_team),
        ]
        for pattern, replacement in pronoun_patterns:
            if replacement:
                msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
        return msg

    def get_context_summary(self):
        """Get summary for response generation"""
        return {
            'last_player': self.last_player,
            'last_player_id': self.last_player_id,
            'last_team': self.last_team,
            'last_topic': self.last_topic,
            'last_intent': self.last_intent,
            'recent_players': self.mentioned_players[-5:],
            'recent_teams': self.mentioned_teams[-5:],
            'turn_count': len(self.history),
        }

    def get_recent_history(self, n=5):
        return list(self.history)[-n:]
