"use client";
import { useState, useEffect } from 'react';
import { YieldCurveChart } from '../../components/YieldCurveChart';
import { Landmark, TrendingDown, Gavel, Globe } from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function TreasuryPage() {
  const [activeTab, setActiveTab] = useState('yield');
  const [yieldData, setYieldData] = useState(null);
  const [debtData, setDebtData] = useState(null);
  const [auctionData, setAuctionData] = useState(null);
  const [fxData, setFxData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [yc, debt, auctions, fx] = await Promise.all([
          fetch(`${API}/api/treasury/yield-curve/latest`).then(r => r.json()),
          fetch(`${API}/api/treasury/debt`).then(r => r.json()),
          fetch(`${API}/api/treasury/auctions`).then(r => r.json()),
          fetch(`${API}/api/treasury/exchange-rates`).then(r => r.json()),
        ]);
        setYieldData(yc);
        setDebtData(debt);
        setAuctionData(auctions);
        setFxData(fx);
      } catch (e) {
        console.error(e);
      }
      setLoading(false);
    };
    fetchAll();
  }, []);

  const tabs = [
    { id: 'yield', label: 'Yield Curve', icon: <TrendingDown size={16} /> },
    { id: 'debt', label: 'U.S. Debt', icon: <Landmark size={16} /> },
    { id: 'auctions', label: 'Auctions', icon: <Gavel size={16} /> },
    { id: 'fx', label: 'Exchange Rates', icon: <Globe size={16} /> },
  ];

  if (loading) {
    return (
      <div className="fade-in">
        <header className="page-header">
          <h1 className="page-title">Treasury Direct</h1>
        </header>
        <div className="loading-spinner"><div className="spinner" /></div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <header className="page-header">
        <h1 className="page-title">Treasury Direct</h1>
        <p className="page-subtitle">U.S. Treasury yield curves, debt data, auction results, and exchange rates</p>
      </header>

      {/* Tabs */}
      <div className="tabs">
        {tabs.map(t => (
          <button
            key={t.id}
            className={`tab ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}
            style={{ display: 'flex', alignItems: 'center', gap: 6 }}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Yield Curve Tab */}
      {activeTab === 'yield' && yieldData && (
        <>
          <div className="chart-container" style={{ marginBottom: 24 }}>
            <div className="chart-header">
              <h2>U.S. Treasury Yield Curve</h2>
              <p>As of {yieldData.date} — Constant Maturity Rates</p>
            </div>
            <div className="chart-body">
              <YieldCurveChart maturities={yieldData.maturities} />
            </div>
          </div>

          {/* Yield Table */}
          <div className="glass-panel-static">
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>Rate Summary</h3>
            <div className="grid-6">
              {yieldData.maturities.map((m, i) => (
                <div key={i} className="stat-card" style={{ padding: 16 }}>
                  <div className="stat-card-label">{m.label}</div>
                  <div className="stat-card-value" style={{ fontSize: '1.25rem' }}>{m.rate}%</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Debt Tab */}
      {activeTab === 'debt' && debtData && (
        <div className="glass-panel-static">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>Debt to the Penny</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Debt Held by Public</th>
                  <th>Intragovernmental</th>
                  <th>Total Public Debt</th>
                </tr>
              </thead>
              <tbody>
                {debtData.data?.slice(0, 20).map((row, i) => (
                  <tr key={i}>
                    <td>{row.record_date}</td>
                    <td style={{ fontVariantNumeric: 'tabular-nums' }}>{row.debt_held_public_amt}</td>
                    <td style={{ fontVariantNumeric: 'tabular-nums' }}>{row.intragov_hold_amt}</td>
                    <td style={{ fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{row.tot_pub_debt_out_amt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Auctions Tab */}
      {activeTab === 'auctions' && auctionData && (
        <div className="glass-panel-static">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>Recent Treasury Auctions</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Term</th>
                  <th>High Yield</th>
                  <th>Offering</th>
                  <th>Bid-to-Cover</th>
                </tr>
              </thead>
              <tbody>
                {auctionData.data?.map((row, i) => (
                  <tr key={i}>
                    <td>{row.record_date}</td>
                    <td>
                      <span className="chip chip-blue">{row.security_type}</span>
                    </td>
                    <td>{row.security_term}</td>
                    <td style={{ fontWeight: 600 }}>{row.high_yield}</td>
                    <td>{row.offering_amt}</td>
                    <td>{row.bid_to_cover_ratio}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* FX Tab */}
      {activeTab === 'fx' && fxData && (
        <div className="glass-panel-static">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>Treasury Exchange Rates (USD)</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Country</th>
                  <th>Currency</th>
                  <th>Exchange Rate</th>
                </tr>
              </thead>
              <tbody>
                {fxData.data?.slice(0, 30).map((row, i) => (
                  <tr key={i}>
                    <td>{row.record_date}</td>
                    <td>{row.country}</td>
                    <td>
                      <span className="chip chip-blue">{row.currency}</span>
                    </td>
                    <td style={{ fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{row.exchange_rate}</td>
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
