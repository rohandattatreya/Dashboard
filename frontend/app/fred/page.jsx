"use client";
import { useState, useEffect, useCallback } from 'react';
import { LightweightChart } from '../../components/LightweightChart';
import { Search, TrendingUp, Clock, Info } from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const POPULAR = [
  { id: 'GDP', label: 'GDP' },
  { id: 'UNRATE', label: 'Unemployment' },
  { id: 'CPIAUCSL', label: 'CPI' },
  { id: 'DFF', label: 'Fed Funds' },
  { id: 'DGS10', label: '10Y Treasury' },
  { id: 'SP500', label: 'S&P 500' },
  { id: 'VIXCLS', label: 'VIX' },
  { id: 'M2SL', label: 'M2 Supply' },
];

export default function FredPage() {
  const [seriesId, setSeriesId] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);

  const fetchSeries = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    setSeriesId(id);
    try {
      const res = await fetch(`${API}/api/fred/series/${id}`);
      if (!res.ok) throw new Error(`Failed to fetch series: ${res.statusText}`);
      const json = await res.json();
      if (json.data) {
        json.chartData = json.data.map(d => ({
          time: d.date,
          value: parseFloat(d.value),
        }));
      }
      setData(json);
      setSearchResults([]);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  }, []);

  const handleSearch = useCallback(async (q) => {
    if (!q.trim()) { setSearchResults([]); return; }
    setSearching(true);
    try {
      const res = await fetch(`${API}/api/fred/search?q=${encodeURIComponent(q)}`);
      const json = await res.json();
      setSearchResults(json.results || []);
    } catch (e) {
      console.error(e);
    }
    setSearching(false);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => handleSearch(searchQuery), 300);
    return () => clearTimeout(timer);
  }, [searchQuery, handleSearch]);

  // Load GDP on mount
  useEffect(() => { fetchSeries('GDP'); }, [fetchSeries]);

  const latestValue = data?.chartData?.length ? data.chartData[data.chartData.length - 1] : null;

  return (
    <div className="fade-in">
      <header className="page-header">
        <h1 className="page-title">FRED Macroeconomic Data</h1>
        <p className="page-subtitle">Explore macroeconomic time-series from the Federal Reserve Economic Data</p>
      </header>

      {/* Search Bar */}
      <div className="glass-panel-static" style={{ marginBottom: 24 }}>
        <div style={{ position: 'relative' }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <Search size={18} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search indicators (e.g., GDP, unemployment, CPI...)"
              style={{ flex: 1, minWidth: 0 }}
            />
          </div>

          {/* Search Results Dropdown */}
          {searchResults.length > 0 && (
            <div style={{
              position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 50,
              background: 'var(--bg-secondary)', border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)', marginTop: 8, maxHeight: 300, overflowY: 'auto',
              boxShadow: '0 16px 48px rgba(0,0,0,0.5)',
            }}>
              {searchResults.map((r, i) => (
                <div
                  key={i}
                  className="search-result"
                  onClick={() => { fetchSeries(r.id); setSearchQuery(''); }}
                >
                  <div className="search-result-id">{r.id}</div>
                  <div className="search-result-title">{r.title}</div>
                  <div className="search-result-meta">{r.frequency} · {r.units}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Popular Tags */}
        <div style={{ display: 'flex', gap: 8, marginTop: 16, flexWrap: 'wrap' }}>
          {POPULAR.map(p => (
            <button
              key={p.id}
              className={seriesId === p.id ? 'btn' : 'btn-outline'}
              style={{ padding: '6px 14px', fontSize: '0.8rem' }}
              onClick={() => fetchSeries(p.id)}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {loading && (
        <div className="loading-spinner"><div className="spinner" /></div>
      )}

      {/* Chart + Data */}
      {data && !loading && (
        <>
          {/* Chart */}
          <div className="chart-container" style={{ marginBottom: 24 }}>
            <div className="chart-header">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2>{data.metadata?.title || seriesId}</h2>
                  <p>{data.metadata?.frequency} · {data.metadata?.units}</p>
                </div>
                {latestValue && (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                      {latestValue.value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      Latest: {latestValue.time}
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="chart-body">
              <LightweightChart data={data.chartData} height={420} />
            </div>
          </div>

          {/* Metadata Panel */}
          <div className="glass-panel-static">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <Info size={18} style={{ color: 'var(--accent-blue)' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Series Information</h3>
            </div>
            <div className="grid-3">
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4 }}>Series ID</div>
                <div style={{ fontWeight: 600 }}>{data.metadata?.id || seriesId}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4 }}>Frequency</div>
                <div style={{ fontWeight: 600 }}>{data.metadata?.frequency}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4 }}>Seasonal Adjustment</div>
                <div style={{ fontWeight: 600 }}>{data.metadata?.seasonal_adjustment}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4 }}>Observation Start</div>
                <div style={{ fontWeight: 600 }}>{data.metadata?.observation_start}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4 }}>Observation End</div>
                <div style={{ fontWeight: 600 }}>{data.metadata?.observation_end}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4 }}>Data Points</div>
                <div style={{ fontWeight: 600 }}>{data.data?.length?.toLocaleString()}</div>
              </div>
            </div>
            {data.metadata?.notes && (
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: 16, lineHeight: 1.7 }}>
                {data.metadata.notes}
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
