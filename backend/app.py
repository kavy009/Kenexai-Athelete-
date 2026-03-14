"""
Flask Backend API - Athlete Performance Analytics
Serves REST API for dashboards, ML predictions, and GenAI coaching chatbot
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import re
from etl_pipeline import ETLPipeline
from ml_models import MLModels

app = Flask(__name__)
CORS(app)

# ──────────── Initialize ETL & ML on startup ────────────
print("Initializing backend...")
etl = ETLPipeline()
etl.run_full_pipeline()
ml = MLModels(etl)
ml.train_all()
print("Backend ready!\n")


# ════════════════════════════════════════
# DATA QUALITY & EDA
# ════════════════════════════════════════
@app.route('/api/data-quality')
def data_quality():
    return jsonify(etl.data_quality_report)

@app.route('/api/eda')
def eda():
    return jsonify(etl.get_eda_data())


# ════════════════════════════════════════
# PLAYERS
# ════════════════════════════════════════
@app.route('/api/players')
def get_players():
    perf = etl.gold['fact_player_performance']
    search = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    sort_by = request.args.get('sort_by', 'performance_score')
    order = request.args.get('order', 'desc')

    df = perf.copy()
    if search:
        df = df[df['player_name'].str.lower().str.contains(search, na=False)]

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=(order == 'asc'))

    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = df.iloc[start:end]

    cols = ['player_api_id', 'player_name', 'age', 'height', 'weight', 'preferred_foot',
            'overall_rating', 'potential', 'performance_score', 'attack_score',
            'midfield_score', 'defense_score', 'physical_score']
    if 'cluster_name' in page_data.columns:
        cols.append('cluster_name')

    result = page_data[cols].fillna('').to_dict('records')
    for r in result:
        for k, v in r.items():
            if isinstance(v, (np.integer, np.int64)):
                r[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                r[k] = round(float(v), 2)

    return jsonify({
        'players': result,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })


@app.route('/api/players/<int:player_api_id>')
def get_player(player_api_id):
    perf = etl.gold['fact_player_performance']
    player = perf[perf['player_api_id'] == player_api_id]
    if player.empty:
        return jsonify({'error': 'Player not found'}), 404

    p = player.iloc[0]
    skill_cols = ['crossing', 'finishing', 'heading_accuracy', 'short_passing', 'volleys',
                  'dribbling', 'curve', 'free_kick_accuracy', 'long_passing', 'ball_control',
                  'acceleration', 'sprint_speed', 'agility', 'reactions', 'balance',
                  'shot_power', 'jumping', 'stamina', 'strength', 'long_shots',
                  'aggression', 'interceptions', 'positioning', 'vision', 'penalties',
                  'marking', 'standing_tackle', 'sliding_tackle']

    result = {
        'player_api_id': int(p['player_api_id']),
        'player_name': str(p['player_name']),
        'age': round(float(p['age']), 1) if pd.notna(p['age']) else None,
        'height': round(float(p['height']), 1) if pd.notna(p['height']) else None,
        'weight': round(float(p['weight']), 1) if pd.notna(p['weight']) else None,
        'preferred_foot': str(p['preferred_foot']) if pd.notna(p['preferred_foot']) else None,
        'overall_rating': round(float(p['overall_rating']), 1) if pd.notna(p['overall_rating']) else None,
        'potential': round(float(p['potential']), 1) if pd.notna(p['potential']) else None,
        'performance_score': round(float(p['performance_score']), 1) if pd.notna(p['performance_score']) else None,
        'attack_score': round(float(p['attack_score']), 1) if pd.notna(p['attack_score']) else None,
        'midfield_score': round(float(p['midfield_score']), 1) if pd.notna(p['midfield_score']) else None,
        'defense_score': round(float(p['defense_score']), 1) if pd.notna(p['defense_score']) else None,
        'physical_score': round(float(p['physical_score']), 1) if pd.notna(p['physical_score']) else None,
        'cluster_name': str(p.get('cluster_name', '')) if pd.notna(p.get('cluster_name')) else None,
        'skills': {}
    }
    for col in skill_cols:
        val = p.get(col)
        result['skills'][col] = round(float(val), 1) if pd.notna(val) else None

    # Injury risk
    injury_pred = ml.predict_injury_risk(player_api_id)
    result['injury_risk'] = injury_pred

    return jsonify(result)


@app.route('/api/players/<int:player_api_id>/injury-risk')
def player_injury_risk(player_api_id):
    result = ml.predict_injury_risk(player_api_id)
    if result is None:
        return jsonify({'error': 'Player not found'}), 404
    return jsonify(result)


# ════════════════════════════════════════
# TEAMS & LEAGUES
# ════════════════════════════════════════
@app.route('/api/teams')
def get_teams():
    teams = etl.gold['dim_team']
    search = request.args.get('search', '').lower()
    df = teams.copy()
    if search:
        df = df[df['team_long_name'].str.lower().str.contains(search, na=False)]

    cols = ['team_api_id', 'team_long_name', 'team_short_name',
            'buildUpPlaySpeed', 'buildUpPlayPassing',
            'chanceCreationPassing', 'chanceCreationCrossing', 'chanceCreationShooting',
            'defencePressure', 'defenceAggression', 'defenceTeamWidth']
    available_cols = [c for c in cols if c in df.columns]
    result = df[available_cols].fillna(0).head(100).to_dict('records')
    for r in result:
        for k, v in r.items():
            if isinstance(v, (np.integer, np.int64)):
                r[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                r[k] = round(float(v), 2)
    return jsonify(result)


@app.route('/api/leagues')
def get_leagues():
    leagues = etl.gold['dim_league']
    result = leagues[['id', 'league_name', 'country_name']].fillna('').to_dict('records')
    return jsonify(result)


# ════════════════════════════════════════
# ML PREDICTIONS
# ════════════════════════════════════════
@app.route('/api/player-clusters')
def player_clusters():
    return jsonify(ml.get_cluster_data())


@app.route('/api/match-prediction')
def match_prediction():
    home = request.args.get('home_team_id', type=int)
    away = request.args.get('away_team_id', type=int)
    if not home or not away:
        return jsonify({'error': 'Provide home_team_id and away_team_id'}), 400
    return jsonify(ml.predict_match(home, away))


@app.route('/api/ml-metrics')
def ml_metrics():
    return jsonify(ml.metrics)


# ════════════════════════════════════════
# DASHBOARD DATA
# ════════════════════════════════════════
@app.route('/api/dashboard/coach')
def coach_dashboard():
    perf = etl.gold['fact_player_performance']
    injury = etl.gold['fact_injury_risk']

    # Top performers
    top_performers = perf.nlargest(10, 'performance_score')[
        ['player_api_id', 'player_name', 'overall_rating', 'performance_score', 'age']
    ].to_dict('records')

    # High injury risk players
    high_risk_ids = injury[injury['injury_risk'] == 1]['player_api_id'].tolist()
    high_risk_players = perf[perf['player_api_id'].isin(high_risk_ids)].nlargest(10, 'performance_score')[
        ['player_api_id', 'player_name', 'overall_rating', 'performance_score']
    ].to_dict('records')
    for p in high_risk_players:
        risk = ml.predict_injury_risk(p['player_api_id'])
        p['risk_probability'] = risk['risk_probability'] if risk else 0
        p['risk_factors'] = risk['risk_factors'] if risk else []

    # Squad composition by cluster
    squad_composition = []
    if 'cluster_name' in perf.columns:
        groups = perf.dropna(subset=['cluster_name']).groupby('cluster_name').size()
        for name, count in groups.items():
            squad_composition.append({'name': str(name), 'count': int(count)})

    # Performance distribution
    perf_dist = pd.cut(perf['performance_score'].dropna(), bins=[0, 40, 55, 70, 85, 100],
                       labels=['Poor', 'Below Avg', 'Average', 'Good', 'Excellent']).value_counts().to_dict()
    perf_dist = {str(k): int(v) for k, v in perf_dist.items()}

    result = {
        'top_performers': _clean_records(top_performers),
        'high_risk_players': _clean_records(high_risk_players),
        'squad_composition': squad_composition,
        'performance_distribution': perf_dist,
        'summary': {
            'total_players': int(len(perf)),
            'avg_performance': round(float(perf['performance_score'].mean()), 1),
            'high_risk_count': int(len(high_risk_ids)),
            'avg_rating': round(float(perf['overall_rating'].mean()), 1)
        }
    }
    return jsonify(result)


@app.route('/api/dashboard/scout')
def scout_dashboard():
    perf = etl.gold['fact_player_performance']

    # Young talents (high potential, age < 23)
    young_talents = perf[(perf['age'] < 23) & (perf['potential'] > 75)].nlargest(15, 'potential')[
        ['player_api_id', 'player_name', 'age', 'overall_rating', 'potential',
         'performance_score', 'attack_score', 'midfield_score', 'defense_score']
    ].to_dict('records')

    # Undervalued players (high performance, lower rating)
    perf_copy = perf.dropna(subset=['performance_score', 'overall_rating'])
    perf_copy['value_gap'] = perf_copy['performance_score'] - perf_copy['overall_rating']
    undervalued = perf_copy.nlargest(15, 'value_gap')[
        ['player_api_id', 'player_name', 'age', 'overall_rating', 'potential',
         'performance_score', 'value_gap']
    ].to_dict('records')

    # Players by position cluster
    clusters = ml.get_cluster_data() if ml.cluster_labels else []

    # Comparison data
    comparison_metrics = {
        'avg_by_foot': perf.groupby('preferred_foot').agg({
            'overall_rating': 'mean', 'performance_score': 'mean'
        }).round(1).to_dict()
    }

    result = {
        'young_talents': _clean_records(young_talents),
        'undervalued_players': _clean_records(undervalued),
        'player_clusters': clusters,
        'comparison_metrics': comparison_metrics,
        'summary': {
            'total_scouted': int(len(perf)),
            'young_talents_count': int(len(young_talents)),
            'avg_potential': round(float(perf['potential'].mean()), 1)
        }
    }
    return jsonify(result)


@app.route('/api/dashboard/analyst')
def analyst_dashboard():
    matches = etl.gold['fact_match']
    teams = etl.gold['dim_team']

    # Goals by season
    goals_by_season = matches.groupby('season').agg({
        'total_goals': ['sum', 'mean', 'count'],
        'home_team_goal': 'mean',
        'away_team_goal': 'mean'
    }).round(2)
    goals_by_season.columns = ['total_goals', 'avg_goals', 'matches', 'avg_home_goals', 'avg_away_goals']
    goals_season_data = []
    for season, row in goals_by_season.iterrows():
        goals_season_data.append({
            'season': str(season),
            'total_goals': int(row['total_goals']),
            'avg_goals': round(float(row['avg_goals']), 2),
            'matches': int(row['matches']),
            'avg_home_goals': round(float(row['avg_home_goals']), 2),
            'avg_away_goals': round(float(row['avg_away_goals']), 2)
        })

    # Result distribution
    result_dist = matches['result'].value_counts().to_dict()
    result_dist = {str(k): int(v) for k, v in result_dist.items()}

    # Top scoring teams
    home_goals = matches.groupby('home_team_api_id')['home_team_goal'].sum().reset_index()
    home_goals.columns = ['team_api_id', 'goals']
    away_goals = matches.groupby('away_team_api_id')['away_team_goal'].sum().reset_index()
    away_goals.columns = ['team_api_id', 'goals']
    total_goals = pd.concat([home_goals, away_goals]).groupby('team_api_id')['goals'].sum().reset_index()
    total_goals = total_goals.merge(teams[['team_api_id', 'team_long_name']], on='team_api_id', how='left')
    top_scoring = total_goals.nlargest(15, 'goals')[['team_long_name', 'goals']].to_dict('records')

    # ML model performance
    ml_performance = ml.metrics

    result = {
        'goals_by_season': goals_season_data,
        'result_distribution': result_dist,
        'top_scoring_teams': _clean_records(top_scoring),
        'ml_performance': ml_performance,
        'summary': {
            'total_matches': int(len(matches)),
            'total_goals': int(matches['total_goals'].sum()),
            'avg_goals_per_match': round(float(matches['total_goals'].mean()), 2),
            'seasons': int(matches['season'].nunique()),
            'teams': int(len(teams))
        }
    }
    return jsonify(result)


# ════════════════════════════════════════
# GenAI COACHING CHATBOT
# ════════════════════════════════════════
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    response = generate_coaching_response(user_message)
    return jsonify(response)


def generate_coaching_response(message):
    """GenAI-style coaching chatbot using rule-based NLP with keyword extraction"""
    message_lower = message.lower()
    perf = etl.gold['fact_player_performance']
    injury_data = etl.gold['fact_injury_risk']

    # Intent detection
    intent = detect_intent(message_lower)

    if intent == 'player_search':
        return handle_player_search(message, message_lower, perf)
    elif intent == 'injury_risk':
        return handle_injury_query(message, message_lower, perf, injury_data)
    elif intent == 'top_players':
        return handle_top_players(message_lower, perf)
    elif intent == 'compare_players':
        return handle_player_comparison(message, message_lower, perf)
    elif intent == 'team_info':
        return handle_team_query(message, message_lower)
    elif intent == 'coaching_advice':
        return handle_coaching_advice(message, message_lower, perf)
    elif intent == 'match_prediction':
        return handle_match_prediction_chat(message, message_lower)
    elif intent == 'stats':
        return handle_stats_query(message_lower, perf)
    else:
        return handle_general(message_lower, perf)


def detect_intent(msg):
    if any(w in msg for w in ['injury', 'risk', 'hurt', 'injured', 'fitness', 'fatigue']):
        return 'injury_risk'
    if any(w in msg for w in ['top', 'best', 'highest', 'ranking', 'leaderboard']):
        return 'top_players'
    if any(w in msg for w in ['compare', 'versus', 'vs', 'difference between']):
        return 'compare_players'
    if any(w in msg for w in ['team', 'club', 'squad']):
        return 'team_info'
    if any(w in msg for w in ['coach', 'training', 'improve', 'recommendation', 'advice', 'develop', 'plan']):
        return 'coaching_advice'
    if any(w in msg for w in ['predict', 'match', 'outcome', 'winner', 'result']):
        return 'match_prediction'
    if any(w in msg for w in ['stats', 'statistics', 'average', 'total', 'count', 'how many']):
        return 'stats'
    if any(w in msg for w in ['who is', 'tell me about', 'info', 'player', 'show me', 'find']):
        return 'player_search'
    return 'general'


def find_player_by_name(name_query, perf):
    name_lower = name_query.lower()
    matches = perf[perf['player_name'].str.lower().str.contains(name_lower, na=False)]
    if len(matches) == 0:
        # Try partial matching
        words = name_lower.split()
        for word in words:
            if len(word) > 3:
                matches = perf[perf['player_name'].str.lower().str.contains(word, na=False)]
                if len(matches) > 0:
                    break
    return matches


def extract_player_name(message, message_lower):
    # Remove common question words to isolate player name
    stop_words = ['who', 'is', 'tell', 'me', 'about', 'how', 'what', 'the', 'player',
                  'show', 'find', 'info', 'injury', 'risk', 'for', 'of', 'compare',
                  'with', 'versus', 'vs', 'and', 'coaching', 'advice', 'training',
                  'plan', 'improve', 'can', 'you', 'please', 'performing', 'doing',
                  'does', 'stats', 'statistics', 'score', 'rating', 'a', 'an']
    words = message.split()
    name_parts = [w for w in words if w.lower().strip('?.,!') not in stop_words and len(w) > 1]
    return ' '.join(name_parts)


def handle_player_search(message, message_lower, perf):
    name = extract_player_name(message, message_lower)
    if not name:
        return {
            'type': 'text',
            'message': "Please provide a player name. For example: 'Tell me about Lionel Messi'",
            'suggestions': ['Who is Messi?', 'Tell me about Ronaldo', 'Show me Neymar stats']
        }

    matches = find_player_by_name(name, perf)
    if matches.empty:
        return {
            'type': 'text',
            'message': f"I couldn't find a player matching '{name}'. Try a different spelling or name.",
            'suggestions': ['Show top 10 players', 'List players with high potential']
        }

    player = matches.iloc[0]
    injury = ml.predict_injury_risk(int(player['player_api_id']))

    return {
        'type': 'player_profile',
        'message': f"Here's the profile for **{player['player_name']}**:",
        'player': {
            'name': str(player['player_name']),
            'age': round(float(player['age']), 1) if pd.notna(player['age']) else None,
            'overall_rating': round(float(player['overall_rating'])) if pd.notna(player['overall_rating']) else None,
            'potential': round(float(player['potential'])) if pd.notna(player['potential']) else None,
            'performance_score': round(float(player['performance_score']), 1) if pd.notna(player['performance_score']) else None,
            'preferred_foot': str(player['preferred_foot']) if pd.notna(player['preferred_foot']) else None,
            'attack_score': round(float(player['attack_score']), 1) if pd.notna(player['attack_score']) else None,
            'midfield_score': round(float(player['midfield_score']), 1) if pd.notna(player['midfield_score']) else None,
            'defense_score': round(float(player['defense_score']), 1) if pd.notna(player['defense_score']) else None,
            'physical_score': round(float(player['physical_score']), 1) if pd.notna(player['physical_score']) else None,
            'cluster': str(player.get('cluster_name', '')) if pd.notna(player.get('cluster_name')) else None,
        },
        'injury_risk': injury,
        'suggestions': [f'Coaching advice for {player["player_name"]}',
                       f'Injury risk for {player["player_name"]}',
                       f'Compare {player["player_name"]} with other players']
    }


def handle_injury_query(message, message_lower, perf, injury_data):
    name = extract_player_name(message, message_lower)
    if name:
        matches = find_player_by_name(name, perf)
        if not matches.empty:
            player = matches.iloc[0]
            risk = ml.predict_injury_risk(int(player['player_api_id']))
            if risk:
                status_emoji = "🔴" if risk['risk_level'] == 'High' else "🟢"
                msg = f"{status_emoji} **{player['player_name']}** - Injury Risk: **{risk['risk_level']}** ({risk['risk_probability']}%)\n\n"
                if risk['risk_factors']:
                    msg += "**Risk Factors:**\n" + "\n".join([f"⚠️ {f}" for f in risk['risk_factors']])
                else:
                    msg += "No significant risk factors detected."

                return {
                    'type': 'injury_analysis',
                    'message': msg,
                    'player_name': str(player['player_name']),
                    'risk': risk,
                    'suggestions': [f'Coaching plan for {player["player_name"]}',
                                   'Show all high-risk players',
                                   f'Full profile of {player["player_name"]}']
                }

    # Show high-risk players summary
    high_risk = injury_data[injury_data['injury_risk'] == 1]
    high_risk_with_names = high_risk.merge(perf[['player_api_id', 'player_name', 'overall_rating']], on='player_api_id')
    top_risk = high_risk_with_names.nlargest(10, 'fatigue_index')[['player_name', 'fatigue_index', 'training_load']].to_dict('records')

    return {
        'type': 'injury_overview',
        'message': f"📊 **Injury Risk Overview**\n\n🔴 High Risk Players: **{len(high_risk)}**\n🟢 Low Risk Players: **{len(injury_data) - len(high_risk)}**\n\nTop 10 highest fatigue players shown below:",
        'high_risk_players': _clean_records(top_risk),
        'summary': {
            'high_risk_count': int(len(high_risk)),
            'low_risk_count': int(len(injury_data) - len(high_risk)),
            'avg_fatigue': round(float(injury_data['fatigue_index'].mean()), 2)
        },
        'suggestions': ['Injury risk for Messi', 'Coaching advice for high-risk players', 'Show player fitness data']
    }


def handle_top_players(message_lower, perf):
    n = 10
    nums = re.findall(r'\d+', message_lower)
    if nums:
        n = min(int(nums[0]), 50)

    sort_by = 'performance_score'
    if 'attack' in message_lower:
        sort_by = 'attack_score'
    elif 'defense' in message_lower or 'defend' in message_lower:
        sort_by = 'defense_score'
    elif 'midfield' in message_lower or 'passing' in message_lower:
        sort_by = 'midfield_score'
    elif 'physical' in message_lower or 'athletic' in message_lower:
        sort_by = 'physical_score'
    elif 'potential' in message_lower or 'young' in message_lower:
        sort_by = 'potential'

    top = perf.nlargest(n, sort_by)[['player_name', 'overall_rating', sort_by, 'age']].to_dict('records')

    return {
        'type': 'leaderboard',
        'message': f"🏆 **Top {n} Players by {sort_by.replace('_', ' ').title()}**",
        'players': _clean_records(top),
        'metric': sort_by,
        'suggestions': ['Top 10 by attack score', 'Top 10 by potential', 'Best defenders', 'Show young talents']
    }


def handle_player_comparison(message, message_lower, perf):
    separators = [' vs ', ' versus ', ' compared to ', ' and ', ' with ']
    parts = None
    for sep in separators:
        if sep in message_lower:
            parts = message_lower.split(sep)
            break

    if not parts or len(parts) < 2:
        return {
            'type': 'text',
            'message': "Please use format: 'Compare Player A vs Player B'",
            'suggestions': ['Compare Messi vs Ronaldo', 'Compare Neymar versus Hazard']
        }

    p1_matches = find_player_by_name(parts[0].strip(), perf)
    p2_matches = find_player_by_name(parts[1].strip(), perf)

    if p1_matches.empty or p2_matches.empty:
        return {
            'type': 'text',
            'message': "Could not find one or both players. Please check the names.",
            'suggestions': ['Compare Messi vs Ronaldo']
        }

    p1, p2 = p1_matches.iloc[0], p2_matches.iloc[0]
    compare_cols = ['overall_rating', 'potential', 'performance_score', 'attack_score',
                    'midfield_score', 'defense_score', 'physical_score', 'age']

    comparison = {}
    for col in compare_cols:
        v1 = round(float(p1[col]), 1) if pd.notna(p1[col]) else 0
        v2 = round(float(p2[col]), 1) if pd.notna(p2[col]) else 0
        comparison[col] = {'player1': v1, 'player2': v2, 'difference': round(v1 - v2, 1)}

    return {
        'type': 'comparison',
        'message': f"⚔️ **{p1['player_name']} vs {p2['player_name']}**",
        'player1': {'name': str(p1['player_name']), 'overall': round(float(p1['overall_rating'])) if pd.notna(p1['overall_rating']) else 0},
        'player2': {'name': str(p2['player_name']), 'overall': round(float(p2['overall_rating'])) if pd.notna(p2['overall_rating']) else 0},
        'comparison': comparison,
        'suggestions': [f'Coaching advice for {p1["player_name"]}', f'Injury risk for {p2["player_name"]}']
    }


def handle_team_query(message, message_lower):
    teams = etl.gold['dim_team']
    name = extract_player_name(message, message_lower)
    if name:
        team_matches = teams[teams['team_long_name'].str.lower().str.contains(name.lower(), na=False)]
        if not team_matches.empty:
            team = team_matches.iloc[0]
            return {
                'type': 'team_profile',
                'message': f"🏟️ **{team['team_long_name']}**",
                'team': {
                    'name': str(team['team_long_name']),
                    'short_name': str(team.get('team_short_name', '')),
                    'buildUpPlaySpeed': _safe_float(team.get('buildUpPlaySpeed')),
                    'buildUpPlayPassing': _safe_float(team.get('buildUpPlayPassing')),
                    'chanceCreationShooting': _safe_float(team.get('chanceCreationShooting')),
                    'defencePressure': _safe_float(team.get('defencePressure')),
                    'defenceAggression': _safe_float(team.get('defenceAggression')),
                },
                'suggestions': ['Predict match for this team', 'Show team rankings']
            }

    team_list = teams['team_long_name'].head(20).tolist()
    return {
        'type': 'team_list',
        'message': "Here are some teams in the database:",
        'teams': team_list,
        'suggestions': ['Tell me about Barcelona', 'Manchester United team info']
    }


def handle_coaching_advice(message, message_lower, perf):
    name = extract_player_name(message, message_lower)
    if not name:
        return {
            'type': 'text',
            'message': "Please specify a player for coaching advice. Example: 'Coaching advice for Messi'",
            'suggestions': ['Coaching advice for Ronaldo', 'Training plan for Neymar']
        }

    matches = find_player_by_name(name, perf)
    if matches.empty:
        return {
            'type': 'text',
            'message': f"Player '{name}' not found.",
            'suggestions': ['Show top players', 'Coaching advice for Messi']
        }

    player = matches.iloc[0]
    injury = ml.predict_injury_risk(int(player['player_api_id']))

    # Generate personalized recommendations
    recommendations = []
    training_plan = []

    # Weakness analysis
    scores = {
        'Attack': float(player['attack_score']) if pd.notna(player['attack_score']) else 50,
        'Midfield': float(player['midfield_score']) if pd.notna(player['midfield_score']) else 50,
        'Defense': float(player['defense_score']) if pd.notna(player['defense_score']) else 50,
        'Physical': float(player['physical_score']) if pd.notna(player['physical_score']) else 50,
    }
    weakest = min(scores, key=scores.get)
    strongest = max(scores, key=scores.get)

    recommendations.append(f"✅ **Strength**: {strongest} skills are excellent ({scores[strongest]:.0f}/100)")
    recommendations.append(f"📈 **Focus Area**: {weakest} needs the most improvement ({scores[weakest]:.0f}/100)")

    # Detailed skill recommendations
    if scores['Attack'] < 60:
        training_plan.append("⚽ **Finishing Drills**: 3x/week - Focus on shooting accuracy and positioning")
        training_plan.append("🎯 **Target Practice**: Daily volleys and heading accuracy exercises")
    if scores['Midfield'] < 60:
        training_plan.append("🔄 **Passing Circuits**: 4x/week - Short and long passing under pressure")
        training_plan.append("👁️ **Vision Training**: Tactical awareness and through-ball exercises")
    if scores['Defense'] < 60:
        training_plan.append("🛡️ **Defensive Positioning**: 3x/week - 1v1 defending and marking drills")
        training_plan.append("🦶 **Tackling Workshop**: Standing and sliding tackle technique")
    if scores['Physical'] < 65:
        training_plan.append("🏃 **Sprint Intervals**: 3x/week - 20m/40m sprint drills")
        training_plan.append("💪 **Strength Training**: 2x/week - Core and leg strengthening")
        training_plan.append("🧘 **Agility Work**: Ladder drills and cone exercises")

    # Potential-based advice
    potential = float(player['potential']) if pd.notna(player['potential']) else 0
    current = float(player['overall_rating']) if pd.notna(player['overall_rating']) else 0
    if potential - current > 5:
        recommendations.append(f"🌟 **High Ceiling**: Gap of {potential - current:.0f} between current ({current:.0f}) and potential ({potential:.0f}) - invest in development!")
    elif potential - current < 2:
        recommendations.append(f"📊 **Peak Performance**: Player is near their peak ({current:.0f}/{potential:.0f}) - focus on maintenance")

    # Injury-based advice
    if injury and injury['risk_level'] == 'High':
        recommendations.append("⚠️ **Injury Alert**: High injury risk detected - reduce training intensity")
        training_plan.append("🏥 **Recovery Protocol**: Mandatory rest days, ice bath therapy, sleep optimization")
        training_plan.append("📉 **Load Management**: Reduce match minutes by 20% over next 4 weeks")

    if not training_plan:
        training_plan.append("📋 **Maintenance Plan**: Continue current training regime with progressive overload")
        training_plan.append("🔄 **Cross-Training**: Add variety with swimming or cycling for recovery")

    return {
        'type': 'coaching_plan',
        'message': f"🧑‍🏫 **Personalized Coaching Plan for {player['player_name']}**",
        'player_name': str(player['player_name']),
        'recommendations': recommendations,
        'training_plan': training_plan,
        'scores': {k: round(v, 1) for k, v in scores.items()},
        'injury_risk': injury,
        'suggestions': [f'Compare {player["player_name"]} with top players',
                       f'Show {player["player_name"]} full stats',
                       'Show training plans for high-risk players']
    }


def handle_match_prediction_chat(message, message_lower):
    teams = etl.gold['dim_team']
    # Try to find "team1 vs team2" pattern
    separators = [' vs ', ' versus ', ' against ']
    for sep in separators:
        if sep in message_lower:
            parts = message_lower.split(sep)
            if len(parts) == 2:
                t1 = teams[teams['team_long_name'].str.lower().str.contains(parts[0].strip(), na=False)]
                t2 = teams[teams['team_long_name'].str.lower().str.contains(parts[1].strip(), na=False)]
                if not t1.empty and not t2.empty:
                    result = ml.predict_match(int(t1.iloc[0]['team_api_id']), int(t2.iloc[0]['team_api_id']))
                    return {
                        'type': 'match_prediction',
                        'message': f"⚽ **Match Prediction**: {result.get('home_team', '')} vs {result.get('away_team', '')}",
                        'prediction': result,
                        'suggestions': ['Predict another match', 'Show team rankings']
                    }

    return {
        'type': 'text',
        'message': "Please use format: 'Predict Barcelona vs Real Madrid'",
        'suggestions': ['Predict Barcelona vs Real Madrid', 'Predict Arsenal vs Chelsea']
    }


def handle_stats_query(message_lower, perf):
    eda = etl.get_eda_data()
    return {
        'type': 'statistics',
        'message': "📊 **Database Statistics**",
        'stats': {
            **eda['summary_stats'],
            **eda['match_stats'],
            **eda['injury_overview']
        },
        'suggestions': ['Show top players', 'Show injury overview', 'Show team stats']
    }


def handle_general(message_lower, perf):
    return {
        'type': 'help',
        'message': "👋 **Hi! I'm your AI Coaching Assistant.** Here's what I can help with:\n\n"
                   "🔍 **Player Search**: 'Tell me about Messi'\n"
                   "🏆 **Rankings**: 'Top 10 players by attack'\n"
                   "⚔️ **Comparisons**: 'Compare Messi vs Ronaldo'\n"
                   "🏥 **Injury Analysis**: 'Injury risk for Neymar'\n"
                   "🧑‍🏫 **Coaching Plans**: 'Coaching advice for Hazard'\n"
                   "⚽ **Match Predictions**: 'Predict Barcelona vs Real Madrid'\n"
                   "📊 **Statistics**: 'Show me stats'\n"
                   "🏟️ **Team Info**: 'Tell me about Barcelona'",
        'suggestions': ['Top 10 players', 'Show injury overview', 'Compare Messi vs Ronaldo',
                       'Coaching advice for Neymar', 'Predict Barcelona vs Real Madrid']
    }


def _safe_float(val):
    if pd.notna(val):
        try:
            return round(float(val), 1)
        except:
            return None
    return None

def _clean_records(records):
    """Convert numpy types to Python native types"""
    cleaned = []
    for r in records:
        clean = {}
        for k, v in r.items():
            if isinstance(v, (np.integer, np.int64)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                clean[k] = round(float(v), 2)
            elif isinstance(v, (list, dict)):
                clean[k] = v
            else:
                clean[k] = v
        cleaned.append(clean)
    return cleaned


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
