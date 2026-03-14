"""
NLP Intent Engine — Semantic intent understanding with fuzzy matching
Replaces rigid regex patterns with probabilistic scoring
"""
import re
from difflib import SequenceMatcher

# Intent definitions with keywords, phrases, and semantic weight
INTENTS = {
    'player_profile': {
        'keywords': ['about', 'profile', 'analysis', 'analyze', 'who is', 'show me', 'tell me', 'details', 'info', 'assessment', 'overview', 'how is', 'how good', 'what about', 'evaluate', 'stats for', 'statistics for', 'breakdown'],
        'requires_entity': 'player', 'priority': 5,
    },
    'injury_risk': {
        'keywords': ['injury', 'injured', 'injury risk', 'risk of injury', 'hurt', 'health', 'medical', 'will get injured', 'injury prediction', 'injury probability', 'at risk', 'susceptible', 'vulnerable'],
        'requires_entity': 'player', 'priority': 8,
    },
    'fatigue': {
        'keywords': ['fatigue', 'tired', 'exhausted', 'fatigue level', 'fatigue report', 'energy', 'stamina level', 'rest', 'recovery', 'workload', 'overworked', 'overplayed', 'should rest', 'need rest', 'which players should we rest'],
        'requires_entity': 'optional_player', 'priority': 7,
    },
    'top_players': {
        'keywords': ['top', 'best', 'highest', 'leading', 'rankings', 'leaderboard', 'who are the best', 'strongest', 'fastest', 'most skilled', 'elite', 'star players', 'best attacking', 'best defending'],
        'requires_entity': None, 'priority': 4,
    },
    'declining_players': {
        'keywords': ['declining', 'dropping', 'decreasing', 'falling', 'worsening', 'performance drop', 'getting worse', 'lost form', 'poor form', 'underperforming', 'performing poorly', 'why is .* performing poorly', 'why .* playing bad'],
        'requires_entity': None, 'priority': 6,
    },
    'improving_players': {
        'keywords': ['improving', 'rising', 'growing', 'developing', 'getting better', 'improved', 'on the rise', 'breakthrough', 'emerging', 'promising'],
        'requires_entity': None, 'priority': 6,
    },
    'compare': {
        'keywords': ['compare', 'vs', 'versus', 'against', 'compared to', 'difference between', 'better than', 'who is better', 'head to head between players'],
        'requires_entity': 'two_players', 'priority': 9,
    },
    'lineup': {
        'keywords': ['lineup', 'starting xi', 'starting eleven', 'formation', 'recommend lineup', 'best team', 'optimal lineup', 'who should start', 'who should play', 'starting lineup'],
        'requires_entity': 'optional_team', 'priority': 7,
    },
    'match_prediction': {
        'keywords': ['predict', 'prediction', 'forecast', 'who will win', 'who wins', 'match outcome', 'match result', 'odds', 'chances'],
        'requires_entity': 'two_teams', 'priority': 9,
    },
    'anomalies': {
        'keywords': ['anomaly', 'anomalies', 'unusual', 'abnormal', 'irregular', 'strange', 'weird', 'outlier', 'suspicious', 'unexpected'],
        'requires_entity': None, 'priority': 5,
    },
    'team_info': {
        'keywords': ['team', 'squad', 'roster', 'club', 'team analysis', 'team info'],
        'requires_entity': 'team', 'priority': 4,
    },
    'statistics': {
        'keywords': ['stats', 'statistics', 'overview', 'summary', 'dashboard', 'numbers', 'how many', 'total', 'count', 'overall stats', 'platform overview', 'show stats'],
        'requires_entity': None, 'priority': 3,
    },
    'head_to_head': {
        'keywords': ['head to head', 'h2h', 'history between', 'match history', 'record against', 'past matches', 'previous matches between'],
        'requires_entity': 'two_teams', 'priority': 8,
    },
    'coaching': {
        'keywords': ['coaching', 'training', 'development', 'improve', 'coaching plan', 'training plan', 'how to improve', 'development plan', 'help .* improve', 'make .* better', 'drills', 'exercises', 'workout'],
        'requires_entity': 'player', 'priority': 7,
    },
    'greeting': {
        'keywords': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'greetings', 'whats up', "what's up", 'sup'],
        'requires_entity': None, 'priority': 1,
    },
    'thanks': {
        'keywords': ['thanks', 'thank you', 'appreciate', 'great', 'awesome', 'nice', 'good job', 'helpful', 'perfect', 'excellent'],
        'requires_entity': None, 'priority': 1,
    },
    'help': {
        'keywords': ['help', 'what can you do', 'capabilities', 'features', 'menu', 'options', 'guide'],
        'requires_entity': None, 'priority': 2,
    },
}

# Patterns for extracting comparison entities
VS_PATTERN = re.compile(r'(.+?)\s+(?:vs\.?|versus|against|compared?\s+(?:to|with))\s+(.+)', re.I)
PREDICT_PATTERN = re.compile(r'(?:predict|prediction|forecast|who\s+(?:will\s+)?wins?)\s+(.+?)\s+(?:vs\.?|versus|against)\s+(.+)', re.I)
NUMBER_PATTERN = re.compile(r'\b(\d+)\b')


class NLPIntentEngine:
    def __init__(self):
        self.intents = INTENTS

    def understand(self, message, context=None):
        """Score all intents and return best match with extracted entities"""
        msg = message.lower().strip()

        # Score each intent
        scores = {}
        for intent_name, intent_def in self.intents.items():
            score = self._score_intent(msg, intent_def)
            scores[intent_name] = score

        # Sort by score (descending), then priority
        ranked = sorted(scores.items(), key=lambda x: (x[1], self.intents[x[0]]['priority']), reverse=True)
        best_intent = ranked[0][0] if ranked[0][1] > 0 else 'general'
        best_score = ranked[0][1]

        # If score is very low, check context for follow-up
        if best_score < 0.3 and context:
            best_intent = self._infer_from_context(msg, context) or best_intent

        # Extract entities
        entities = self._extract_entities(msg, best_intent, message)

        return {
            'intent': best_intent,
            'confidence': min(best_score, 1.0),
            'entities': entities,
            'all_scores': {k: round(v, 2) for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]},
        }

    def _score_intent(self, msg, intent_def):
        """Score how well a message matches an intent using fuzzy keyword matching"""
        score = 0
        for keyword in intent_def['keywords']:
            if keyword in msg:
                # Exact match
                score += 1.0
            else:
                # Fuzzy match for multi-word keywords
                words = keyword.split()
                if len(words) > 1:
                    ratio = SequenceMatcher(None, keyword, msg).ratio()
                    if ratio > 0.6:
                        score += ratio * 0.5
                # Check if individual significant words appear
                for w in words:
                    if len(w) > 3 and w in msg:
                        score += 0.3
        return score

    def _infer_from_context(self, msg, context):
        """Infer intent from conversation context for follow-up questions"""
        ctx = context.get_context_summary()

        # "What about his defense?" after player analysis
        if ctx['last_intent'] == 'player_profile' and ctx['last_player']:
            if any(w in msg for w in ['defense', 'attack', 'midfield', 'physical', 'skill', 'rating']):
                return 'player_profile'
            if any(w in msg for w in ['injury', 'risk', 'health']):
                return 'injury_risk'
            if any(w in msg for w in ['fatigue', 'tired', 'rest']):
                return 'fatigue'
            if any(w in msg for w in ['coaching', 'improve', 'train', 'develop']):
                return 'coaching'

        # "Compare with Ronaldo" after Messi analysis
        if ctx['last_player'] and any(w in msg for w in ['compare', 'vs', 'versus', 'against', 'better']):
            return 'compare'

        return None

    def _extract_entities(self, msg, intent, original_msg):
        """Extract player names, team names, numbers, metrics"""
        entities = {}

        # Extract number (for "top N")
        num_match = NUMBER_PATTERN.search(msg)
        if num_match:
            entities['count'] = int(num_match.group(1))

        # Extract metric keywords
        metric_map = {
            'attack': 'attack_score', 'attacking': 'attack_score', 'offense': 'attack_score',
            'defense': 'defense_score', 'defending': 'defense_score', 'defensive': 'defense_score',
            'midfield': 'midfield_score', 'physical': 'physical_score',
            'rating': 'overall_rating', 'overall': 'overall_rating',
            'potential': 'potential', 'performance': 'performance_score',
            'speed': 'sprint_speed', 'sprint': 'sprint_speed',
            'stamina': 'stamina', 'finishing': 'finishing', 'dribbling': 'dribbling',
            'passing': 'short_passing', 'shooting': 'finishing',
        }
        for keyword, metric in metric_map.items():
            if keyword in msg:
                entities['metric'] = metric
                break

        # Extract formation
        for f in ['4-3-3', '4-4-2', '3-5-2', '4-2-3-1', '3-4-3', '4-1-4-1']:
            if f in msg:
                entities['formation'] = f
                break

        # VS pattern for comparisons / predictions
        vs_match = VS_PATTERN.search(original_msg)
        if vs_match and intent in ('compare', 'match_prediction', 'head_to_head'):
            entities['entity1'] = vs_match.group(1).strip().rstrip('?.,! ')
            entities['entity2'] = vs_match.group(2).strip().rstrip('?.,! ')

        predict_match = PREDICT_PATTERN.search(original_msg)
        if predict_match:
            entities['entity1'] = predict_match.group(1).strip().rstrip('?.,! ')
            entities['entity2'] = predict_match.group(2).strip().rstrip('?.,! ')

        return entities
