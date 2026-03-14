import { useState, useEffect } from 'react';
import { api } from '../api';
import {
    RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

export default function CoachDashboard() {
    const [data, setData] = useState(null);
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [playerDetail, setPlayerDetail] = useState(null);

    useEffect(() => { api.getCoachDashboard().then(setData); }, []);

    const loadPlayer = async (id) => {
        setSelectedPlayer(id);
        const detail = await api.getPlayer(id);
        setPlayerDetail(detail);
    };

    if (!data) return <div className="loading-container"><div className="spinner" /><p>Loading coach dashboard...</p></div>;

    const radarData = playerDetail ? [
        { skill: 'Attack', value: playerDetail.attack_score || 0 },
        { skill: 'Midfield', value: playerDetail.midfield_score || 0 },
        { skill: 'Defense', value: playerDetail.defense_score || 0 },
        { skill: 'Physical', value: playerDetail.physical_score || 0 },
        { skill: 'Overall', value: playerDetail.overall_rating || 0 },
        { skill: 'Potential', value: playerDetail.potential || 0 },
    ] : [];

    return (
        <div>
            <div className="page-header">
                <h2>🧑‍🏫 Coach Dashboard</h2>
                <p>Monitor player performance, track injury risks, and manage your squad</p>
            </div>

            <div className="grid-4" style={{ marginBottom: 24 }}>
                <div className="stat-card">
                    <div className="stat-icon">👥</div>
                    <div className="stat-value">{data.summary.total_players.toLocaleString()}</div>
                    <div className="stat-label">Total Players</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-value">{data.summary.avg_performance}</div>
                    <div className="stat-label">Avg Performance</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">⭐</div>
                    <div className="stat-value">{data.summary.avg_rating}</div>
                    <div className="stat-label">Avg Rating</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">🏥</div>
                    <div className="stat-value" style={{ color: 'var(--danger)' }}>{data.summary.high_risk_count}</div>
                    <div className="stat-label">High Injury Risk</div>
                </div>
            </div>

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card">
                    <div className="card-header"><div className="card-title">🏆 Top Performers</div></div>
                    <table className="data-table">
                        <thead><tr><th>Rank</th><th>Player</th><th>Rating</th><th>Performance</th><th>Action</th></tr></thead>
                        <tbody>
                            {data.top_performers.map((p, i) => (
                                <tr key={i}>
                                    <td style={{ fontWeight: 700, color: i < 3 ? '#f59e0b' : 'var(--text-muted)' }}>#{i + 1}</td>
                                    <td style={{ fontWeight: 600 }}>{p.player_name}</td>
                                    <td><span className="badge badge-info">{p.overall_rating}</span></td>
                                    <td><span className="badge badge-success">{p.performance_score}</span></td>
                                    <td><button className="btn btn-ghost" onClick={() => loadPlayer(p.player_api_id)} style={{ padding: '4px 10px', fontSize: 11 }}>View</button></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="card">
                    <div className="card-header"><div className="card-title">🚨 Injury Risk Alerts</div></div>
                    <table className="data-table">
                        <thead><tr><th>Player</th><th>Rating</th><th>Risk</th><th>Factors</th></tr></thead>
                        <tbody>
                            {data.high_risk_players.map((p, i) => (
                                <tr key={i}>
                                    <td style={{ fontWeight: 600 }}>{p.player_name}</td>
                                    <td>{p.overall_rating}</td>
                                    <td><span className="badge badge-danger">{p.risk_probability}%</span></td>
                                    <td style={{ fontSize: 11 }}>{(p.risk_factors || []).slice(0, 2).join(', ')}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card">
                    <div className="card-header"><div className="card-title">📊 Performance Distribution</div></div>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={Object.entries(data.performance_distribution).map(([k, v]) => ({ level: k, count: v }))}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="level" stroke="#64748b" fontSize={11} />
                            <YAxis stroke="#64748b" fontSize={11} />
                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                {Object.keys(data.performance_distribution).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="card">
                    <div className="card-header"><div className="card-title">🎯 Squad Composition (Clusters)</div></div>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie data={data.squad_composition} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={90} innerRadius={40} label={({ name, count }) => `${name.split(' ').slice(0, 2).join(' ')}: ${count}`} labelLine={false}>
                                {data.squad_composition.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                            </Pie>
                            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {playerDetail && (
                <div className="card" style={{ marginBottom: 24 }}>
                    <div className="card-header">
                        <div>
                            <div className="card-title">🔍 {playerDetail.player_name}</div>
                            <div className="card-subtitle">Age: {playerDetail.age} | {playerDetail.preferred_foot} foot | {playerDetail.cluster_name || 'Unclassified'}</div>
                        </div>
                        <button className="btn btn-ghost" onClick={() => { setSelectedPlayer(null); setPlayerDetail(null); }}>✕</button>
                    </div>
                    <div className="grid-2">
                        <div>
                            <div style={{ display: 'flex', gap: 16, marginBottom: 20, flexWrap: 'wrap' }}>
                                <div className="stat-card" style={{ flex: 1, minWidth: 100 }}>
                                    <div className="stat-value" style={{ fontSize: 20 }}>{playerDetail.overall_rating}</div>
                                    <div className="stat-label">Overall</div>
                                </div>
                                <div className="stat-card" style={{ flex: 1, minWidth: 100 }}>
                                    <div className="stat-value" style={{ fontSize: 20 }}>{playerDetail.potential}</div>
                                    <div className="stat-label">Potential</div>
                                </div>
                                <div className="stat-card" style={{ flex: 1, minWidth: 100 }}>
                                    <div className="stat-value" style={{ fontSize: 20 }}>{playerDetail.performance_score}</div>
                                    <div className="stat-label">Performance</div>
                                </div>
                            </div>
                            {playerDetail.injury_risk && (
                                <div style={{ padding: 16, background: playerDetail.injury_risk.risk_level === 'High' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)', borderRadius: 12, border: `1px solid ${playerDetail.injury_risk.risk_level === 'High' ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}` }}>
                                    <div style={{ fontWeight: 700, marginBottom: 8 }}>
                                        {playerDetail.injury_risk.risk_level === 'High' ? '🔴' : '🟢'} Injury Risk: {playerDetail.injury_risk.risk_level} ({playerDetail.injury_risk.risk_probability}%)
                                    </div>
                                    {playerDetail.injury_risk.risk_factors?.length > 0 && (
                                        <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                                            {playerDetail.injury_risk.risk_factors.map((f, i) => <div key={i}>⚠️ {f}</div>)}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                        <ResponsiveContainer width="100%" height={260}>
                            <RadarChart data={radarData}>
                                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                <PolarAngleAxis dataKey="skill" stroke="#94a3b8" fontSize={11} />
                                <PolarRadiusAxis domain={[0, 100]} tick={false} />
                                <Radar dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} strokeWidth={2} />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
}
