"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { TrendingUp, Building2, Landmark, ArrowUpRight } from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/overview`)
      .then(r => r.json())
      .then(d => { setMetrics(d.metrics || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const features = [
    {
      href: '/fred',
      icon: <TrendingUp size={24} />,
      iconClass: 'blue',
      title: 'FRED Macroeconomic Data',
      desc: 'Explore GDP, unemployment, CPI, interest rates, money supply and 17+ key macro indicators with interactive time-series charts.',
    },
    {
      href: '/sec',
      icon: <Building2 size={24} />,
      iconClass: 'green',
      title: 'SEC EDGAR Fundamentals',
      desc: 'Analyze company fundamentals — revenue, net income, EPS, and total assets from 10-K XBRL filings for AAPL, MSFT, GOOGL, AMZN, TSLA.',
    },
    {
      href: '/treasury',
      icon: <Landmark size={24} />,
      iconClass: 'purple',
      title: 'Treasury Direct',
      desc: 'Visualize the yield curve, track U.S. debt levels, view recent auction results, and monitor exchange rates.',
    },
  ];

  return (
    <div className="fade-in">
      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Macro & Fundamental<br /><span>Financial Dashboard</span>
          </h1>
          <p className="hero-desc">
            A unified platform for exploring macroeconomic indicators from FRED,
            fundamental company data from SEC EDGAR, and U.S. Treasury securities data — all in one place.
          </p>
        </div>
      </section>

      {/* Metrics Grid */}
      <section style={{ marginBottom: 40 }}>
        <div className="section-header">
          <h2 className="section-title">Key Indicators</h2>
          <span className="chip chip-blue">Live Overview</span>
        </div>
        <div className="grid-6">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="stat-card loading-pulse" style={{ height: 110 }} />
              ))
            : metrics.map((m, i) => (
                <div key={i} className="stat-card" style={{ animationDelay: `${i * 0.05}s` }}>
                  <div className="stat-card-label">{m.label}</div>
                  <div className="stat-card-value">{m.value}</div>
                  <div className={`stat-card-change ${m.positive === true ? 'positive' : m.positive === false ? 'negative' : 'neutral'}`}>
                    {m.change}
                  </div>
                </div>
              ))
          }
        </div>
      </section>

      {/* Feature Cards */}
      <section>
        <div className="section-header">
          <h2 className="section-title">Data Sources</h2>
        </div>
        <div className="grid-3">
          {features.map((f, i) => (
            <Link key={i} href={f.href}>
              <div className="feature-card" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className={`feature-card-icon ${f.iconClass}`}>{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
                <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 4, color: 'var(--accent-blue)', fontSize: '0.85rem', fontWeight: 600 }}>
                  Explore <ArrowUpRight size={14} />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
