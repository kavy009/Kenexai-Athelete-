import { useState, useEffect } from 'react';
import { api } from '../api';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
    AreaChart, Area
} from 'recharts';

const COLORS = ['#4f6ef7', '#6c5ce7', '#22c55e', '#f59e0b', '#ef4444', '#3b82f6', '#a78bfa'];
const getChartTheme = () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        tooltip: { background: isDark ? '#1c1e2a' : '#ffffff', border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e2e5ed', borderRadius: 8, color: isDark ? '#f0f1f5' : '#1a1d26' },
        grid: isDark ? 'rgba(255,255,255,0.06)' : '#e8eaef',
        axis: isDark ? '#6b7084' : '#8b91a5',
        polar: isDark ? 'rgba(255,255,255,0.08)' : '#e8eaef',
    };
};

export default function DataQuality() {
    const [quality, setQuality] = useState(null);
    const [eda, setEDA] = useState(null);
    const [tab, setTab] = useState('quality');

    useEffect(() => {
        api.getDataQuality().then(setQuality);
        api.getEDA().then(setEDA);
    }, []);

    if (!quality || !eda) return <div className="loading-container"><div className="spinner" /><p>Loading data quality metrics...</p></div>;

    const tables = Object.entries(quality).filter(([k]) => k !== 'outliers');
    const totalRows = tables.reduce((s, [, v]) => s + v.rows, 0);
    const avgCompleteness = (tables.reduce((s, [, v]) => s + v.completeness, 0) / tables.length).toFixed(1);
    const ct = getChartTheme();

    return (
        <div>
            <div className="page-header">
                <h2>📊 Data Quality & EDA</h2>
                <p>Comprehensive data profiling, quality metrics, and exploratory analysis</p>
            </div>

            <div className="grid-4" style={{ marginBottom: 24 }}>
                <div className="stat-card">
                    <div className="stat-icon">📋</div>
                    <div className="stat-value">{tables.length}</div>
                    <div className="stat-label">Tables</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">📝</div>
                    <div className="stat-value">{totalRows.toLocaleString()}</div>
                    <div className="stat-label">Total Records</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">✅</div>
                    <div className="stat-value">{avgCompleteness}%</div>
                    <div className="stat-label">Avg Completeness</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">⚽</div>
                    <div className="stat-value">{eda.summary_stats?.total_players?.toLocaleString()}</div>
                    <div className="stat-label">Players</div>
                </div>
            </div>

            <div className="tabs">
                <button className={`tab ${tab === 'quality' ? 'active' : ''}`} onClick={() => setTab('quality')}>Data Quality</button>
                <button className={`tab ${tab === 'distributions' ? 'active' : ''}`} onClick={() => setTab('distributions')}>Distributions</button>
                <button className={`tab ${tab === 'correlations' ? 'active' : ''}`} onClick={() => setTab('correlations')}>Correlations</button>
                <button className={`tab ${tab === 'outliers' ? 'active' : ''}`} onClick={() => setTab('outliers')}>Outliers</button>
            </div>

            {tab === 'quality' && (
                <div>
                    <div className="grid-2" style={{ marginBottom: 24 }}>
                        {tables.map(([name, data]) => (
                            <div className="card" key={name}>
                                <div className="card-header">
                                    <div>
                                        <div className="card-title">{name}</div>
                                        <div className="card-subtitle">{data.rows.toLocaleString()} rows × {data.columns} columns</div>
                                    </div>
                                    <span className={`badge ${data.completeness > 95 ? 'badge-success' : data.completeness > 80 ? 'badge-warning' : 'badge-danger'}`}>
                                        {data.completeness}%
                                    </span>
                                </div>
                                <div className="progress-bar" style={{ marginBottom: 12 }}>
                                    <div className="progress-fill" style={{ width: `${data.completeness}%` }} />
                                </div>
                                <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                                    <span>Missing: {data.missing_cells.toLocaleString()}</span>
                                    <span>Duplicates: {data.duplicates}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="card">
                        <div className="card-header"><div className="card-title">Column-Level Quality</div></div>
                        <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr><th>Table</th><th>Column</th><th>Type</th><th>Unique</th><th>Missing</th><th>Completeness</th></tr>
                                </thead>
                                <tbody>
                                    {tables.slice(0, 4).map(([name, data]) =>
                                        Object.entries(data.column_quality).slice(0, 8).map(([col, q]) => (
                                            <tr key={`${name}-${col}`}>
                                                <td><span className="badge badge-purple">{name}</span></td>
                                                <td>{col}</td>
                                                <td style={{ fontFamily: 'monospace', fontSize: 11 }}>{q.dtype}</td>
                                                <td>{q.unique}</td>
                                                <td>{q.missing}</td>
                                                <td>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                                        <div className="progress-bar" style={{ flex: 1, height: 4 }}>
                                                            <div className="progress-fill" style={{ width: `${q.completeness}%` }} />
                                                        </div>
                                                        <span style={{ fontSize: 11 }}>{q.completeness}%</span>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {tab === 'distributions' && (
                <div className="grid-2">
                    <div className="card">
                        <div className="card-header"><div className="card-title">Overall Rating Distribution</div></div>
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={Object.entries(eda.rating_distribution || {}).map(([k, v]) => ({ rating: k, count: v }))}>
                                <CartesianGrid strokeDasharray="3 3" stroke={ct.grid} />
                                <XAxis dataKey="rating" stroke={ct.axis} fontSize={11} />
                                <YAxis stroke={ct.axis} fontSize={11} />
                                <Tooltip contentStyle={ct.tooltip} />
                                <Bar dataKey="count" fill="#4f6ef7" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="card">
                        <div className="card-header"><div className="card-title">Preferred Foot</div></div>
                        <ResponsiveContainer width="100%" height={280}>
                            <PieChart>
                                <Pie data={Object.entries(eda.preferred_foot || {}).map(([k, v]) => ({ name: k, value: v }))} cx="50%" cy="50%" outerRadius={100} innerRadius={50} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                                    {Object.keys(eda.preferred_foot || {}).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip contentStyle={ct.tooltip} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="card">
                        <div className="card-header"><div className="card-title">Goals per Match by Season</div></div>
                        <ResponsiveContainer width="100%" height={280}>
                            <AreaChart data={Object.entries(eda.match_stats?.goals_by_season || {}).map(([k, v]) => ({ season: k, avg: v }))}>
                                <CartesianGrid strokeDasharray="3 3" stroke={ct.grid} />
                                <XAxis dataKey="season" stroke={ct.axis} fontSize={10} />
                                <YAxis stroke={ct.axis} fontSize={11} />
                                <Tooltip contentStyle={ct.tooltip} />
                                <defs>
                                    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#4f6ef7" stopOpacity={0.3} />
                                        <stop offset="100%" stopColor="#4f6ef7" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <Area type="monotone" dataKey="avg" stroke="#4f6ef7" fill="url(#areaGrad)" strokeWidth={2} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="card">
                        <div className="card-header"><div className="card-title">Match Results</div></div>
                        <ResponsiveContainer width="100%" height={280}>
                            <PieChart>
                                <Pie data={[
                                    { name: 'Home Win', value: eda.match_stats?.home_win_pct || 0 },
                                    { name: 'Draw', value: eda.match_stats?.draw_pct || 0 },
                                    { name: 'Away Win', value: eda.match_stats?.away_win_pct || 0 }
                                ]} cx="50%" cy="50%" outerRadius={100} innerRadius={50} dataKey="value" label={({ name, value }) => `${name}: ${value}%`}>
                                    <Cell fill="#10b981" /><Cell fill="#f59e0b" /><Cell fill="#ef4444" />
                                </Pie>
                                <Tooltip contentStyle={ct.tooltip} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {tab === 'correlations' && eda.correlation_matrix && (
                <div className="card">
                    <div className="card-header"><div className="card-title">Correlation Matrix</div></div>
                    <div style={{ overflowX: 'auto' }}>
                        <table className="data-table">
                            <thead>
                                <tr><th></th>{eda.correlation_matrix.columns.map(c => <th key={c} style={{ fontSize: 10 }}>{c.replace('_', ' ')}</th>)}</tr>
                            </thead>
                            <tbody>
                                {eda.correlation_matrix.columns.map((row, i) => (
                                    <tr key={row}>
                                        <td style={{ fontWeight: 600, fontSize: 11 }}>{row.replace('_', ' ')}</td>
                                        {eda.correlation_matrix.values[i].map((v, j) => (
                                            <td key={j} style={{
                                                background: `rgba(${v > 0 ? '99, 102, 241' : '239, 68, 68'}, ${Math.abs(v) * 0.4})`,
                                                textAlign: 'center', fontSize: 11, fontWeight: 600
                                            }}>{v.toFixed(2)}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {tab === 'outliers' && quality.outliers && (
                <div className="card">
                    <div className="card-header"><div className="card-title">Outlier Analysis (IQR Method)</div></div>
                    <div style={{ maxHeight: 500, overflowY: 'auto' }}>
                        <table className="data-table">
                            <thead><tr><th>Attribute</th><th>Lower Bound</th><th>Upper Bound</th><th>Outliers Detected</th></tr></thead>
                            <tbody>
                                {Object.entries(quality.outliers).slice(0, 25).map(([col, info]) => (
                                    <tr key={col}>
                                        <td>{col.replace('_', ' ')}</td>
                                        <td>{info.lower}</td>
                                        <td>{info.upper}</td>
                                        <td><span className={`badge ${info.outliers > 100 ? 'badge-danger' : info.outliers > 0 ? 'badge-warning' : 'badge-success'}`}>{info.outliers}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
