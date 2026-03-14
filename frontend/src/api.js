const API_BASE = 'http://localhost:5000/api';

async function fetchJSON(url) {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getDataQuality: () => fetchJSON('/data-quality'),
  getEDA: () => fetchJSON('/eda'),
  getPlayers: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return fetchJSON(`/players?${q}`);
  },
  getPlayer: (id) => fetchJSON(`/players/${id}`),
  getPlayerInjuryRisk: (id) => fetchJSON(`/players/${id}/injury-risk`),
  getTeams: (search = '') => fetchJSON(`/teams?search=${search}`),
  getLeagues: () => fetchJSON('/leagues'),
  getPlayerClusters: () => fetchJSON('/player-clusters'),
  getMatchPrediction: (homeId, awayId) =>
    fetchJSON(`/match-prediction?home_team_id=${homeId}&away_team_id=${awayId}`),
  getMLMetrics: () => fetchJSON('/ml-metrics'),
  getCoachDashboard: () => fetchJSON('/dashboard/coach'),
  getScoutDashboard: () => fetchJSON('/dashboard/scout'),
  getAnalystDashboard: () => fetchJSON('/dashboard/analyst'),
  chat: async (message) => {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return res.json();
  }
};
