import { useState, useEffect } from 'react';
import { api } from '../api';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    LineChart, Line, PieChart, Pie, Cell, Legend
} from 'recharts';

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6366f1', '#8b5cf6', '#3b82f6'];

export default function AnalystDashboard() {
    const [data, setData] = useState(null);
    const [predicting, setPredicting] = useState(false);
    const [teams, setTeams] = useState([]);
    const [homeTeam, setHomeTeam] = useState('');
    const [awayTeam, setAwayTeam] = useState('');
    const [prediction, setPrediction] = useState(null);

    useEffect(() => {
        api.getAnalystDashboard().then(setData);
        api.getTeams().then(setTeams);
    }, []);

    const predictMatch = async () => {
        if (!homeTeam || !awayTeam || homeTeam === awayTeam) return;
        setPredicting(true);
        const result = await api.getMatchPrediction(homeTeam, awayTeam);
        setPrediction(result);
        setPredicting(false);
    };

    if (!data) return <div className="loading-container"><div className="spinner" /><p>Loading analyst dashboard...</p></div>;

    const resultData = Object.entries(data.result_distribution || {}).map(([k, v]) => ({ name: k, value: v }));

    return (
        <div>
            <div className="page-header">
                <h2>📈 Match Analyst Dashboard</h2>
                <p>Deep-dive into match analytics, predictions, and historical trends</p>
            </div>

            <div className="grid-4" style={{ marginBottom: 24 }}>
                <div className="stat-card">
                    <div className="stat-icon">⚽</div>
                    <div className="stat-value">{data.summary.total_matches.toLocaleString()}</div>
                    <div className="stat-label">Total Matches</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">🥅</div>
                    <div className="stat-value">{data.summary.total_goals.toLocaleString()}</div>
                    <div className="stat-label">Total Goals</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-value">{data.summary.avg_goals_per_match}</div>
                    <div className="stat-label">Avg Goals/Match</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">🏟️</div>
                    <div className="stat-value">{data.summary.teams}</div>
                    <div className="stat-label">Teams</div>
                </div>
            </div>

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card">
                    <div className="card-header"><div className="card-title">📅 Goals by Season</div></div>
                    <ResponsiveContainer width="100%" height={280}>
                        <LineChart data={data.goals_by_season}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="season" stroke="#64748b" fontSize={10} />
                            <YAxis stroke="#64748b" fontSize={11} />
                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                            <Line type="monotone" dataKey="avg_goals" stroke="#6366f1" strokeWidth={2} dot={{ fill: '#6366f1', r: 4 }} name="Avg Goals" />
                            <Line type="monotone" dataKey="avg_home_goals" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 3 }} name="Avg Home" />
                            <Line type="monotone" dataKey="avg_away_goals" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b', r: 3 }} name="Avg Away" />
                            <Legend />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                <div className="card">
                    <div className="card-header"><div className="card-title">📊 Match Result Distribution</div></div>
                    <ResponsiveContainer width="100%" height={280}>
                        <PieChart>
                            <Pie data={resultData} cx="50%" cy="50%" outerRadius={100} innerRadius={50} dataKey="value" label={({ name, value }) => `${name}: ${value.toLocaleString()}`}>
                                {resultData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                            </Pie>
                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card">
                    <div className="card-header"><div className="card-title">🏆 Top Scoring Teams</div></div>
                    <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={data.top_scoring_teams} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis type="number" stroke="#64748b" fontSize={11} />
                            <YAxis type="category" dataKey="team_long_name" stroke="#64748b" fontSize={10} width={140} />
                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                            <Bar dataKey="goals" fill="#6366f1" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="card">
                    <div className="card-header"><div className="card-title">🤖 ML Model Performance</div></div>
                    {data.ml_performance && (
                        <div>
                            {Object.entries(data.ml_performance).map(([model, metrics]) => (
                                <div key={model} style={{ marginBottom: 20, padding: 16, background: 'var(--bg-glass)', borderRadius: 12, border: '1px solid var(--border)' }}>
                                    <div style={{ fontWeight: 700, marginBottom: 8, textTransform: 'capitalize' }}>
                                        {model.replace('_', ' ')}
                                    </div>
                                    {metrics.accuracy !== undefined && (
                                        <div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 13 }}>
                                                <span>Accuracy</span>
                                                <span style={{ fontWeight: 700, color: metrics.accuracy > 0.8 ? 'var(--success)' : 'var(--warning)' }}>
                                                    {(metrics.accuracy * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                            <div className="progress-bar">
                                                <div className="progress-fill" style={{ width: `${metrics.accuracy * 100}%` }} />
                                            </div>
                                        </div>
                                    )}
                                    {metrics.feature_importance && (
                                        <div style={{ marginTop: 12 }}>
                                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>Top Features</div>
                                            {Object.entries(metrics.feature_importance).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([f, v]) => (
                                                <div key={f} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                                                    <span style={{ fontSize: 11, width: 140 }}>{f.replace(/_/g, ' ')}</span>
                                                    <div className="progress-bar" style={{ flex: 1, height: 4 }}>
                                                        <div className="progress-fill" style={{ width: `${v * 100 * 3}%` }} />
                                                    </div>
                                                    <span style={{ fontSize: 11, fontWeight: 600 }}>{(v * 100).toFixed(1)}%</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <div className="card">
                <div className="card-header"><div className="card-title">⚽ Match Outcome Predictor</div></div>
                <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', marginBottom: 20 }}>
                    <div className="select-wrap" style={{ flex: 1 }}>
                        <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>Home Team</label>
                        <select value={homeTeam} onChange={e => setHomeTeam(e.target.value)} style={{ width: '100%' }}>
                            <option value="">Select home team...</option>
                            {teams.map(t => <option key={t.team_api_id} value={t.team_api_id}>{t.team_long_name}</option>)}
                        </select>
                    </div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-muted)', paddingBottom: 8 }}>VS</div>
                    <div className="select-wrap" style={{ flex: 1 }}>
                        <label style={{ display: 'block', fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>Away Team</label>
                        <select value={awayTeam} onChange={e => setAwayTeam(e.target.value)} style={{ width: '100%' }}>
                            <option value="">Select away team...</option>
                            {teams.map(t => <option key={t.team_api_id} value={t.team_api_id}>{t.team_long_name}</option>)}
                        </select>
                    </div>
                    <button className="btn btn-primary" onClick={predictMatch} disabled={predicting || !homeTeam || !awayTeam}>
                        {predicting ? '...' : '🔮 Predict'}
                    </button>
                </div>
                {prediction && !prediction.error && (
                    <div style={{ padding: 20, background: 'var(--bg-glass)', borderRadius: 12, border: '1px solid var(--border)' }}>
                        <div style={{ textAlign: 'center', marginBottom: 16 }}>
                            <div style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 4 }}>Predicted Result</div>
                            <div style={{ fontSize: 24, fontWeight: 800, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                                {prediction.prediction}
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                            {Object.entries(prediction.probabilities || {}).map(([result, prob]) => (
                                <div key={result} style={{ textAlign: 'center', padding: '8px 20px', background: 'var(--bg-card)', borderRadius: 10, border: '1px solid var(--border)' }}>
                                    <div style={{ fontSize: 20, fontWeight: 800, color: result === prediction.prediction ? 'var(--accent-primary)' : 'var(--text-secondary)' }}>{prob}%</div>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{result}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                {prediction?.error && <div style={{ color: 'var(--danger)', fontSize: 13 }}>Error: {prediction.error}</div>}
            </div>
        </div>
    );
}
