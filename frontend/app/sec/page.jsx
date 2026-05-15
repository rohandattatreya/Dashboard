"use client";
import { useState, useEffect, useCallback } from 'react';
import { SecChart } from '../../components/SecChart';
import { Search, Building2, DollarSign, BarChart3, TrendingUp, Layers } from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const COMPANIES = [
  { cik: '320193', label: 'AAPL', name: 'Apple' },
  { cik: '789019', label: 'MSFT', name: 'Microsoft' },
  { cik: '1652044', label: 'GOOGL', name: 'Alphabet' },
  { cik: '1018724', label: 'AMZN', name: 'Amazon' },
  { cik: '1318605', label: 'TSLA', name: 'Tesla' },
];

export default function SecPage() {
  const [cik, setCik] = useState('320193');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCompany = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    setCik(id);
    try {
      const res = await fetch(`${API}/api/sec/companyfacts/${id}`);
      if (!res.ok) throw new Error(`Error: ${res.statusText}`);
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchCompany('320193'); }, [fetchCompany]);

  // Extract key metrics from the latest year
  const getLatestMetrics = () => {
    if (!data?.facts?.['us-gaap']) return [];
    const gaap = data.facts['us-gaap'];
    const metrics = [];
    const extract = (fact, label, icon, fmt) => {
      if (!fact?.units) return;
      const entries = fact.units.USD || fact.units['USD/shares'] || [];
      const annual = entries.filter(d => d.form === '10-K').sort((a, b) => b.fy - a.fy);
      if (annual.length > 0) {
        const latest = annual[0];
        const prev = annual.length > 1 ? annual[1] : null;
        let changeStr = '';
        if (prev) {
          const pct = ((latest.val - prev.val) / Math.abs(prev.val) * 100);
          changeStr = `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}% YoY`;
        }
        metrics.push({ label, value: fmt(latest.val), change: changeStr, fy: latest.fy, icon,
          positive: prev ? latest.val >= prev.val : null });
      }
    };

    const fmtB = v => {
      const abs = Math.abs(v);
      if (abs >= 1e12) return `$${(v/1e12).toFixed(2)}T`;
      if (abs >= 1e9) return `$${(v/1e9).toFixed(2)}B`;
      if (abs >= 1e6) return `$${(v/1e6).toFixed(2)}M`;
      return `$${v.toLocaleString()}`;
    };
    const fmtD = v => `$${v.toFixed(2)}`;

    extract(gaap.Revenues || gaap.SalesRevenueNet, 'Revenue', <DollarSign size={18} />, fmtB);
    extract(gaap.NetIncomeLoss, 'Net Income', <TrendingUp size={18} />, fmtB);
    extract(gaap.EarningsPerShareBasic, 'EPS (Basic)', <BarChart3 size={18} />, fmtD);
    extract(gaap.Assets, 'Total Assets', <Layers size={18} />, fmtB);
    return metrics;
  };

  const keyMetrics = data ? getLatestMetrics() : [];

  return (
    <div className="fade-in">
      <header className="page-header">
        <h1 className="page-title">SEC Fundamentals</h1>
        <p className="page-subtitle">Company financial data extracted from SEC EDGAR XBRL filings</p>
      </header>

      {/* Company Selector */}
      <div className="glass-panel-static" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <Building2 size={18} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
          <input
            type="text"
            value={cik}
            onChange={e => setCik(e.target.value)}
            placeholder="Enter CIK number"
            style={{ width: 200 }}
          />
          <button className="btn" onClick={() => fetchCompany(cik)} disabled={loading}>
            {loading ? 'Loading...' : 'Fetch'}
          </button>
        </div>
        <div style={{ display: 'flex', gap: 8, marginTop: 16, flexWrap: 'wrap' }}>
          {COMPANIES.map(c => (
            <button
              key={c.cik}
              className={cik === c.cik ? 'btn' : 'btn-outline'}
              style={{ padding: '6px 14px', fontSize: '0.8rem' }}
              onClick={() => fetchCompany(c.cik)}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}
      {loading && <div className="loading-spinner"><div className="spinner" /></div>}

      {data && !loading && (
        <>
          {/* Company Header */}
          <div className="glass-panel-static" style={{ marginBottom: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>{data.entityName}</h2>
                <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>CIK: {data.cik}</p>
              </div>
              <div className="chip chip-green">10-K Annual</div>
            </div>
          </div>

          {/* Key Metrics Cards */}
          {keyMetrics.length > 0 && (
            <div className="grid-4" style={{ marginBottom: 24 }}>
              {keyMetrics.map((m, i) => (
                <div key={i} className="stat-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <div style={{ color: 'var(--accent-blue)' }}>{m.icon}</div>
                    <div className="stat-card-label" style={{ marginBottom: 0 }}>{m.label}</div>
                  </div>
                  <div className="stat-card-value" style={{ fontSize: '1.4rem' }}>{m.value}</div>
                  {m.change && (
                    <div className={`stat-card-change ${m.positive ? 'positive' : 'negative'}`}>
                      {m.change}
                    </div>
                  )}
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 4 }}>FY {m.fy}</div>
                </div>
              ))}
            </div>
          )}

          {/* Revenue / Net Income Chart */}
          <div className="chart-container">
            <div className="chart-header">
              <h2>Revenue vs Net Income (Last 10 Years)</h2>
              <p>Annual data from 10-K filings</p>
            </div>
            <div className="chart-body">
              <SecChart facts={data.facts} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
