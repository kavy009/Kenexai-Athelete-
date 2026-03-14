import { useState, useRef, useEffect } from 'react';
import { api } from '../api';

export default function AIChat() {
    const [messages, setMessages] = useState([
        {
            role: 'bot',
            data: {
                type: 'help',
                message: "👋 **Hi! I'm your AI Coaching Assistant.** Here's what I can help with:\n\n" +
                    "🔍 **Player Search**: 'Tell me about Messi'\n" +
                    "🏆 **Rankings**: 'Top 10 players by attack'\n" +
                    "⚔️ **Comparisons**: 'Compare Messi vs Ronaldo'\n" +
                    "🏥 **Injury Analysis**: 'Injury risk for Neymar'\n" +
                    "🧑‍🏫 **Coaching Plans**: 'Coaching advice for Hazard'\n" +
                    "⚽ **Match Predictions**: 'Predict Barcelona vs Real Madrid'\n" +
                    "📊 **Statistics**: 'Show me stats'",
                suggestions: ['Top 10 players', 'Show injury overview', 'Compare Messi vs Ronaldo', 'Coaching advice for Neymar']
            }
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEnd = useRef(null);

    useEffect(() => {
        messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async (text) => {
        const msg = text || input.trim();
        if (!msg || loading) return;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: msg }]);
        setLoading(true);
        try {
            const res = await api.chat(msg);
            setMessages(prev => [...prev, { role: 'bot', data: res }]);
        } catch {
            setMessages(prev => [...prev, { role: 'bot', data: { type: 'text', message: '❌ Something went wrong. Please try again.' } }]);
        }
        setLoading(false);
    };

    const renderBotMessage = (data) => {
        if (!data) return null;

        return (
            <div>
                {data.message && (
                    <div style={{ marginBottom: 12 }}>
                        {data.message.split('\n').map((line, i) => (
                            <p key={i} style={{ marginBottom: 4 }}
                                dangerouslySetInnerHTML={{
                                    __html: line
                                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                        .replace(/__(.*?)__/g, '<em>$1</em>')
                                }} />
                        ))}
                    </div>
                )}

                {data.type === 'player_profile' && data.player && (
                    <div style={{ background: 'rgba(99,102,241,0.08)', borderRadius: 12, padding: 16, marginBottom: 12 }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 12 }}>
                            {['overall_rating', 'potential', 'performance_score'].map(k => (
                                <div key={k} style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--accent-primary)' }}>{data.player[k]}</div>
                                    <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{k.replace(/_/g, ' ')}</div>
                                </div>
                            ))}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
                            {['attack_score', 'midfield_score', 'defense_score', 'physical_score'].map(k => (
                                <div key={k} style={{ textAlign: 'center', padding: 8, background: 'var(--bg-glass)', borderRadius: 8 }}>
                                    <div style={{ fontSize: 16, fontWeight: 700 }}>{data.player[k]}</div>
                                    <div style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{k.split('_')[0]}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {data.type === 'comparison' && data.comparison && (
                    <div style={{ marginBottom: 12 }}>
                        {Object.entries(data.comparison).map(([attr, vals]) => (
                            <div key={attr} className="comparison-row">
                                <div className="comparison-label">{attr.replace(/_/g, ' ')}</div>
                                <div className="comparison-bars">
                                    <div className="comp-bar p1" style={{ width: `${Math.max(vals.player1, 5)}%`, maxWidth: '48%' }}>{vals.player1}</div>
                                    <div className="comp-bar p2" style={{ width: `${Math.max(vals.player2, 5)}%`, maxWidth: '48%' }}>{vals.player2}</div>
                                </div>
                            </div>
                        ))}
                        <div style={{ display: 'flex', gap: 16, fontSize: 11, marginTop: 8 }}>
                            <span style={{ color: '#6366f1' }}>■ {data.player1?.name}</span>
                            <span style={{ color: '#f59e0b' }}>■ {data.player2?.name}</span>
                        </div>
                    </div>
                )}

                {data.type === 'coaching_plan' && (
                    <div style={{ marginBottom: 12 }}>
                        {data.recommendations?.map((r, i) => (
                            <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>{r}</div>
                        ))}
                        {data.training_plan?.length > 0 && (
                            <div style={{ marginTop: 12 }}>
                                <h4 style={{ fontSize: 13, marginBottom: 8 }}>📋 Training Plan</h4>
                                {data.training_plan.map((t, i) => (
                                    <div key={i} style={{ padding: '6px 0', fontSize: 12, color: 'var(--text-secondary)' }}>{t}</div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {data.type === 'leaderboard' && data.players && (
                    <div style={{ marginBottom: 12 }}>
                        {data.players.map((p, i) => (
                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
                                <span><span style={{ color: i < 3 ? '#f59e0b' : 'var(--text-muted)', fontWeight: 700, marginRight: 8 }}>#{i + 1}</span>{p.player_name}</span>
                                <span className="badge badge-info">{p[data.metric] || p.overall_rating}</span>
                            </div>
                        ))}
                    </div>
                )}

                {data.type === 'injury_overview' && data.high_risk_players && (
                    <div style={{ marginBottom: 12 }}>
                        {data.high_risk_players.map((p, i) => (
                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
                                <span>{p.player_name}</span>
                                <span className="badge badge-danger">Fatigue: {p.fatigue_index?.toFixed(1)}</span>
                            </div>
                        ))}
                    </div>
                )}

                {data.type === 'match_prediction' && data.prediction && (
                    <div style={{ textAlign: 'center', padding: 16, background: 'var(--bg-glass)', borderRadius: 12, marginBottom: 12 }}>
                        <div style={{ fontSize: 20, fontWeight: 800 }}>{data.prediction.prediction}</div>
                        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 12 }}>
                            {Object.entries(data.prediction.probabilities || {}).map(([r, p]) => (
                                <div key={r} style={{ padding: '6px 14px', background: 'var(--bg-card)', borderRadius: 8 }}>
                                    <div style={{ fontWeight: 700, fontSize: 16 }}>{p}%</div>
                                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{r}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {data.type === 'statistics' && data.stats && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8, marginBottom: 12 }}>
                        {Object.entries(data.stats).filter(([, v]) => typeof v !== 'object').map(([k, v]) => (
                            <div key={k} style={{ padding: 10, background: 'var(--bg-glass)', borderRadius: 8, fontSize: 12 }}>
                                <div style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{typeof v === 'number' ? v.toLocaleString() : v}</div>
                                <div style={{ color: 'var(--text-muted)', fontSize: 10, textTransform: 'uppercase' }}>{k.replace(/_/g, ' ')}</div>
                            </div>
                        ))}
                    </div>
                )}

                {data.suggestions && data.suggestions.length > 0 && (
                    <div className="chat-suggestions">
                        {data.suggestions.map((s, i) => (
                            <button key={i} className="chat-suggestion" onClick={() => sendMessage(s)}>{s}</button>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div>
            <div className="page-header">
                <h2>🤖 AI Coach Assistant</h2>
                <p>Ask about players, get coaching recommendations, predict match outcomes</p>
            </div>

            <div className="chat-container">
                <div className="chat-messages">
                    {messages.map((msg, i) => (
                        <div key={i} className={`chat-message ${msg.role}`}>
                            {msg.role === 'user' ? msg.text : renderBotMessage(msg.data)}
                        </div>
                    ))}
                    {loading && (
                        <div className="chat-message bot">
                            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                                <div className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
                                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEnd} />
                </div>

                <div className="chat-input-area">
                    <input
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask about players, teams, or coaching advice..."
                        disabled={loading}
                    />
                    <button onClick={() => sendMessage()} disabled={loading || !input.trim()}>Send</button>
                </div>
            </div>
        </div>
    );
}
