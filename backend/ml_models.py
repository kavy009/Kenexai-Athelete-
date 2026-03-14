"""
ML Models for Athlete Performance Analytics
- Player Performance Scoring
- Injury Risk Prediction (RandomForest)
- Match Outcome Prediction (GradientBoosting)
- Player Clustering (KMeans)
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')


class MLModels:
    def __init__(self, etl):
        self.etl = etl
        self.injury_model = None
        self.injury_scaler = None
        self.match_model = None
        self.match_scaler = None
        self.cluster_model = None
        self.cluster_scaler = None
        self.cluster_labels = None
        self.metrics = {}

    def train_all(self):
        """Train all ML models"""
        print("\n[ML] Training models...")
        self.train_injury_risk_model()
        self.train_match_prediction_model()
        self.train_player_clustering()
        print("[ML] All models trained!\n")
        return self

    # ──────────── INJURY RISK PREDICTION ────────────
    def train_injury_risk_model(self):
        injury_data = self.etl.gold['fact_injury_risk'].copy()
        features = ['avg_heart_rate', 'max_heart_rate', 'sprint_distance_km',
                     'total_distance_km', 'training_load', 'fatigue_index',
                     'sleep_hours', 'matches_last_30d', 'previous_injuries',
                     'recovery_time_hours']

        X = injury_data[features].fillna(0)
        y = injury_data['injury_risk']

        self.injury_scaler = StandardScaler()
        X_scaled = self.injury_scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        self.injury_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.injury_model.fit(X_train, y_train)

        y_pred = self.injury_model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        self.metrics['injury_risk'] = {
            'accuracy': round(acc, 4),
            'feature_importance': dict(zip(features, [round(float(x), 4) for x in self.injury_model.feature_importances_]))
        }
        print(f"  [Injury Risk] Accuracy: {acc:.2%}")

    def predict_injury_risk(self, player_api_id):
        injury_data = self.etl.gold['fact_injury_risk']
        row = injury_data[injury_data['player_api_id'] == player_api_id]
        if row.empty:
            return None

        features = ['avg_heart_rate', 'max_heart_rate', 'sprint_distance_km',
                     'total_distance_km', 'training_load', 'fatigue_index',
                     'sleep_hours', 'matches_last_30d', 'previous_injuries',
                     'recovery_time_hours']
        X = row[features].fillna(0).values
        X_scaled = self.injury_scaler.transform(X)
        prob = self.injury_model.predict_proba(X_scaled)[0]
        pred = self.injury_model.predict(X_scaled)[0]
        # Handle case where model only predicts one class
        if len(prob) == 1:
            risk_prob = 100.0 if pred == 1 else 0.0
        else:
            risk_prob = round(float(prob[1]) * 100, 1)

        risk_factors = []
        data = row.iloc[0]
        if data['fatigue_index'] > 6:
            risk_factors.append('High fatigue index')
        if data['training_load'] > 600:
            risk_factors.append('Excessive training load')
        if data['sleep_hours'] < 6.5:
            risk_factors.append('Insufficient sleep')
        if data['previous_injuries'] > 3:
            risk_factors.append('History of injuries')
        if data['matches_last_30d'] > 5:
            risk_factors.append('Match congestion')
        if data['recovery_time_hours'] > 45:
            risk_factors.append('Slow recovery')

        return {
            'risk_level': 'High' if pred == 1 else 'Low',
            'risk_probability': risk_prob,
            'risk_factors': risk_factors,
            'wearable_data': {
                'avg_heart_rate': float(data['avg_heart_rate']),
                'max_heart_rate': float(data['max_heart_rate']),
                'sprint_distance_km': float(data['sprint_distance_km']),
                'total_distance_km': float(data['total_distance_km']),
                'training_load': float(data['training_load']),
                'fatigue_index': float(data['fatigue_index']),
                'sleep_hours': float(data['sleep_hours']),
                'matches_last_30d': int(data['matches_last_30d']),
                'previous_injuries': int(data['previous_injuries']),
                'recovery_time_hours': float(data['recovery_time_hours'])
            }
        }

    # ──────────── MATCH OUTCOME PREDICTION ────────────
    def train_match_prediction_model(self):
        matches = self.etl.gold['fact_match'].copy()
        team_attrs = self.etl.gold['dim_team'].copy()

        attr_cols = ['buildUpPlaySpeed', 'buildUpPlayPassing', 'chanceCreationPassing',
                     'chanceCreationCrossing', 'chanceCreationShooting',
                     'defencePressure', 'defenceAggression', 'defenceTeamWidth']

        team_features = team_attrs[['team_api_id'] + attr_cols].copy()
        for col in attr_cols:
            team_features[col] = pd.to_numeric(team_features[col], errors='coerce')
        team_features = team_features.dropna()

        merged = matches.merge(team_features, left_on='home_team_api_id', right_on='team_api_id', how='inner', suffixes=('', ''))
        home_cols = {col: f'home_{col}' for col in attr_cols}
        merged = merged.rename(columns=home_cols)

        merged = merged.merge(team_features, left_on='away_team_api_id', right_on='team_api_id', how='inner', suffixes=('', '_away'))
        away_cols = {col: f'away_{col}' for col in attr_cols}
        # Handle the suffix
        for col in attr_cols:
            if f'{col}_away' in merged.columns:
                merged = merged.rename(columns={f'{col}_away': f'away_{col}'})
            elif col in merged.columns:
                merged = merged.rename(columns={col: f'away_{col}'})

        feature_cols = [f'home_{c}' for c in attr_cols] + [f'away_{c}' for c in attr_cols]
        available_feature_cols = [c for c in feature_cols if c in merged.columns]

        if len(available_feature_cols) < 4:
            print("  [Match Prediction] Not enough features, skipping")
            self.metrics['match_prediction'] = {'accuracy': 0, 'status': 'skipped'}
            return

        X = merged[available_feature_cols].fillna(0)
        le = LabelEncoder()
        y = le.fit_transform(merged['result'])

        self.match_scaler = StandardScaler()
        X_scaled = self.match_scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        self.match_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.match_model.fit(X_train, y_train)
        self.match_label_encoder = le
        self.match_feature_cols = available_feature_cols

        y_pred = self.match_model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        self.metrics['match_prediction'] = {
            'accuracy': round(acc, 4),
            'classes': le.classes_.tolist()
        }
        print(f"  [Match Prediction] Accuracy: {acc:.2%}")

    def predict_match(self, home_team_id, away_team_id):
        if self.match_model is None:
            return {'error': 'Model not trained'}

        team_attrs = self.etl.gold['dim_team']
        attr_cols = ['buildUpPlaySpeed', 'buildUpPlayPassing', 'chanceCreationPassing',
                     'chanceCreationCrossing', 'chanceCreationShooting',
                     'defencePressure', 'defenceAggression', 'defenceTeamWidth']

        home = team_attrs[team_attrs['team_api_id'] == home_team_id]
        away = team_attrs[team_attrs['team_api_id'] == away_team_id]

        if home.empty or away.empty:
            return {'error': 'Team not found'}

        features = {}
        for col in attr_cols:
            val = home.iloc[0].get(col, 50)
            features[f'home_{col}'] = float(val) if pd.notna(val) else 50.0
        for col in attr_cols:
            val = away.iloc[0].get(col, 50)
            features[f'away_{col}'] = float(val) if pd.notna(val) else 50.0

        X = pd.DataFrame([features])
        available = [c for c in self.match_feature_cols if c in X.columns]
        X = X[available].fillna(0)
        X_scaled = self.match_scaler.transform(X)

        probs = self.match_model.predict_proba(X_scaled)[0]
        pred = self.match_model.predict(X_scaled)[0]

        return {
            'prediction': self.match_label_encoder.inverse_transform([pred])[0],
            'probabilities': {
                cls: round(float(prob) * 100, 1)
                for cls, prob in zip(self.match_label_encoder.classes_, probs)
            },
            'home_team': home.iloc[0].get('team_long_name', str(home_team_id)),
            'away_team': away.iloc[0].get('team_long_name', str(away_team_id))
        }

    # ──────────── PLAYER CLUSTERING ────────────
    def train_player_clustering(self):
        perf = self.etl.gold['fact_player_performance'].copy()
        cluster_cols = ['attack_score', 'midfield_score', 'defense_score', 'physical_score',
                        'overall_rating', 'potential']
        X = perf[cluster_cols].dropna()

        self.cluster_scaler = StandardScaler()
        X_scaled = self.cluster_scaler.fit_transform(X)

        self.cluster_model = KMeans(n_clusters=5, random_state=42, n_init=10)
        labels = self.cluster_model.fit_predict(X_scaled)

        perf_clean = perf.loc[X.index].copy()
        perf_clean['cluster'] = labels

        # Label clusters based on characteristics
        cluster_names = {}
        for c in range(5):
            group = perf_clean[perf_clean['cluster'] == c]
            avg_atk = group['attack_score'].mean()
            avg_mid = group['midfield_score'].mean()
            avg_def = group['defense_score'].mean()
            avg_phy = group['physical_score'].mean()

            scores = {'Attack': avg_atk, 'Midfield': avg_mid, 'Defense': avg_def, 'Physical': avg_phy}
            dominant = max(scores, key=scores.get)
            overall = group['overall_rating'].mean()

            if overall > 75:
                cluster_names[c] = f"Elite {dominant} Players"
            elif overall > 65:
                cluster_names[c] = f"Strong {dominant} Players"
            else:
                cluster_names[c] = f"Developing {dominant} Players"

        perf_clean['cluster_name'] = perf_clean['cluster'].map(cluster_names)
        self.cluster_labels = cluster_names
        self.etl.gold['fact_player_performance'] = perf.copy()
        self.etl.gold['fact_player_performance'].loc[X.index, 'cluster'] = labels
        self.etl.gold['fact_player_performance'].loc[X.index, 'cluster_name'] = self.etl.gold['fact_player_performance'].loc[X.index, 'cluster'].map(cluster_names)

        # Cluster stats
        cluster_stats = {}
        for c, name in cluster_names.items():
            group = perf_clean[perf_clean['cluster'] == c]
            cluster_stats[name] = {
                'count': int(len(group)),
                'avg_overall': round(float(group['overall_rating'].mean()), 1),
                'avg_attack': round(float(group['attack_score'].mean()), 1),
                'avg_midfield': round(float(group['midfield_score'].mean()), 1),
                'avg_defense': round(float(group['defense_score'].mean()), 1),
                'avg_physical': round(float(group['physical_score'].mean()), 1),
                'top_players': group.nlargest(5, 'performance_score')['player_name'].tolist()
            }

        self.metrics['clustering'] = {
            'n_clusters': 5,
            'cluster_stats': cluster_stats
        }
        print(f"  [Clustering] 5 clusters identified")

    def get_cluster_data(self):
        perf = self.etl.gold['fact_player_performance'].copy()
        if 'cluster' not in perf.columns:
            return {'error': 'Clustering not trained'}

        clusters = []
        for c_id, c_name in self.cluster_labels.items():
            group = perf[perf['cluster'] == c_id]
            players = group.nlargest(20, 'performance_score')[
                ['player_name', 'overall_rating', 'performance_score', 'attack_score',
                 'midfield_score', 'defense_score', 'physical_score']
            ].to_dict('records')
            clusters.append({
                'id': int(c_id),
                'name': c_name,
                'count': int(len(group)),
                'avg_rating': round(float(group['overall_rating'].mean()), 1),
                'center': {
                    'attack': round(float(group['attack_score'].mean()), 1),
                    'midfield': round(float(group['midfield_score'].mean()), 1),
                    'defense': round(float(group['defense_score'].mean()), 1),
                    'physical': round(float(group['physical_score'].mean()), 1),
                },
                'top_players': players
            })
        return clusters
