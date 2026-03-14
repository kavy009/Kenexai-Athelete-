import { useState, useEffect } from 'react';
import { api } from '../api';
import {
    RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
    ResponsiveContainer
} from 'recharts';

export default function Players() {
    const [players, setPlayers] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [sortBy, setSortBy] = useState('performance_score');
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [playerDetail, setPlayerDetail] = useState(null);

    const loadPlayers = async () => {
        const res = await api.getPlayers({ page, search, sort_by: sortBy, per_page: 30 });
        setPlayers(res.players || []);
        setTotal(res.total || 0);
    };

    useEffect(() => { loadPlayers(); }, [page, sortBy]);

    const doSearch = () => { setPage(1); loadPlayers(); };

    const viewPlayer = async (id) => {
        setSelectedPlayer(id);
        const detail = await api.getPlayer(id);
        setPlayerDetail(detail);
    };

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
                <h2>👥 Player Database</h2>
                <p>Search, filter, and analyze {total.toLocaleString()} players</p>
            </div>

            <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                <div className="search-bar" style={{ flex: 1, marginBottom: 0 }}>
                    <span>🔍</span>
                    <input
                        placeholder="Search players by name..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && doSearch()}
                    />
                </div>
                <div className="select-wrap">
                    <select value={sortBy} onChange={e => { setSortBy(e.target.value); setPage(1); }}>
                        <option value="performance_score">Performance Score</option>
                        <option value="overall_rating">Overall Rating</option>
                        <option value="potential">Potential</option>
                        <option value="attack_score">Attack</option>
                        <option value="midfield_score">Midfield</option>
                        <option value="defense_score">Defense</option>
                        <option value="physical_score">Physical</option>
                        <option value="age">Age</option>
                    </select>
                </div>
                <button className="btn btn-primary" onClick={doSearch}>Search</button>
            </div>

            {playerDetail && (
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="card-header">
                        <div>
                            <div className="card-title">🔍 {playerDetail.player_name}</div>
                            <div className="card-subtitle">
                                Age: {playerDetail.age?.toFixed(0)} | Height: {playerDetail.height}cm | Weight: {playerDetail.weight}lbs |
                                {playerDetail.preferred_foot} foot | {playerDetail.cluster_name || ''}
                            </div>
                        </div>
                        <button className="btn btn-ghost" onClick={() => { setSelectedPlayer(null); setPlayerDetail(null); }}>✕ Close</button>
                    </div>
                    <div className="grid-2">
                        <div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 16 }}>
                                {[['overall_rating', 'Overall'], ['potential', 'Potential'], ['performance_score', 'Performance']].map(([k, l]) => (
                                    <div key={k} className="stat-card" style={{ padding: 16 }}>
                                        <div className="stat-value" style={{ fontSize: 24 }}>{playerDetail[k]}</div>
                                        <div className="stat-label">{l}</div>
                                    </div>
                                ))}
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginBottom: 16 }}>
                                {[['attack_score', 'ATK'], ['midfield_score', 'MID'], ['defense_score', 'DEF'], ['physical_score', 'PHY']].map(([k, l]) => (
                                    <div key={k} style={{ textAlign: 'center', padding: 10, background: 'var(--bg-glass)', borderRadius: 8 }}>
                                        <div style={{ fontSize: 18, fontWeight: 700 }}>{playerDetail[k]?.toFixed(0)}</div>
                                        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{l}</div>
                                    </div>
                                ))}
                            </div>
                            {playerDetail.injury_risk && (
                                <div style={{ padding: 14, background: playerDetail.injury_risk.risk_level === 'High' ? 'rgba(239,68,68,0.08)' : 'rgba(16,185,129,0.08)', borderRadius: 10, border: `1px solid ${playerDetail.injury_risk.risk_level === 'High' ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)'}` }}>
                                    <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
                                        {playerDetail.injury_risk.risk_level === 'High' ? '🔴' : '🟢'} Injury Risk: {playerDetail.injury_risk.risk_level} ({playerDetail.injury_risk.risk_probability}%)
                                    </div>
                                    {playerDetail.injury_risk.risk_factors?.map((f, i) => (
                                        <div key={i} style={{ fontSize: 12, color: 'var(--text-secondary)' }}>⚠️ {f}</div>
                                    ))}
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
                    {playerDetail.skills && (
                        <div style={{ marginTop: 16 }}>
                            <div className="card-title" style={{ marginBottom: 12 }}>Detailed Skills</div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 6 }}>
                                {Object.entries(playerDetail.skills).filter(([, v]) => v != null).map(([k, v]) => (
                                    <div key={k} style={{ textAlign: 'center', padding: 6, background: 'var(--bg-glass)', borderRadius: 6 }}>
                                        <div style={{ fontSize: 14, fontWeight: 700, color: v > 75 ? 'var(--success)' : v > 60 ? 'var(--accent-primary)' : v > 45 ? 'var(--warning)' : 'var(--danger)' }}>{v}</div>
                                        <div style={{ fontSize: 8, color: 'var(--text-muted)', textTransform: 'uppercase', lineHeight: 1.2 }}>{k.replace(/_/g, ' ')}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            <div className="card">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>#</th><th>Name</th><th>Age</th><th>Foot</th><th>Rating</th>
                            <th>Potential</th><th>Performance</th><th>ATK</th><th>MID</th>
                            <th>DEF</th><th>PHY</th><th>Cluster</th><th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {players.map((p, i) => (
                            <tr key={p.player_api_id}>
                                <td style={{ color: 'var(--text-muted)' }}>{(page - 1) * 30 + i + 1}</td>
                                <td style={{ fontWeight: 600 }}>{p.player_name}</td>
                                <td>{typeof p.age === 'number' ? p.age.toFixed(0) : p.age}</td>
                                <td>{p.preferred_foot}</td>
                                <td><span className="badge badge-info">{p.overall_rating}</span></td>
                                <td><span className="badge badge-purple">{p.potential}</span></td>
                                <td><span className={`badge ${p.performance_score > 70 ? 'badge-success' : p.performance_score > 55 ? 'badge-warning' : 'badge-danger'}`}>{p.performance_score}</span></td>
                                <td>{typeof p.attack_score === 'number' ? p.attack_score.toFixed(0) : ''}</td>
                                <td>{typeof p.midfield_score === 'number' ? p.midfield_score.toFixed(0) : ''}</td>
                                <td>{typeof p.defense_score === 'number' ? p.defense_score.toFixed(0) : ''}</td>
                                <td>{typeof p.physical_score === 'number' ? p.physical_score.toFixed(0) : ''}</td>
                                <td style={{ fontSize: 11 }}>{p.cluster_name || ''}</td>
                                <td><button className="btn btn-ghost" style={{ padding: '3px 8px', fontSize: 11 }} onClick={() => viewPlayer(p.player_api_id)}>View</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                <div className="pagination">
                    <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
                    <span>Page {page} of {Math.ceil(total / 30)}</span>
                    <button disabled={page >= Math.ceil(total / 30)} onClick={() => setPage(p => p + 1)}>Next →</button>
                </div>
            </div>
        </div>
    );
}
