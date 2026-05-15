"use client";
import { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export const SecChart = ({ facts, metric = 'all' }) => {
  const chartData = useMemo(() => {
    if (!facts || !facts['us-gaap']) return [];
    const gaap = facts['us-gaap'];

    const revenues = gaap.Revenues || gaap.SalesRevenueNet || gaap.RevenuesNetOfInterestExpense;
    const netIncome = gaap.NetIncomeLoss;
    const assets = gaap.Assets;

    const dataMap = new Map();
    const processMetric = (m, keyName) => {
      if (!m || !m.units) return;
      const entries = m.units.USD || m.units['USD/shares'] || [];
      entries.filter(d => d.form === '10-K' && d.fy)
        .forEach(d => {
          const fy = d.fy.toString();
          if (!dataMap.has(fy)) dataMap.set(fy, { fy });
          dataMap.get(fy)[keyName] = d.val;
        });
    };

    processMetric(revenues, 'Revenue');
    processMetric(netIncome, 'NetIncome');
    processMetric(assets, 'TotalAssets');

    return Array.from(dataMap.values())
      .sort((a, b) => parseInt(a.fy) - parseInt(b.fy))
      .slice(-10);
  }, [facts]);

  if (!chartData.length) {
    return (
      <div className="empty-state">
        <p>No suitable annual GAAP data found.</p>
      </div>
    );
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return '';
    const abs = Math.abs(value);
    if (abs >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (abs >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (abs >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value.toLocaleString()}`;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload) return null;
    return (
      <div style={{
        background: '#1a2332', border: '1px solid rgba(148,163,184,0.15)',
        borderRadius: '8px', padding: '12px 16px', fontSize: '0.85rem',
      }}>
        <p style={{ fontWeight: 700, marginBottom: 6 }}>FY {label}</p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color, margin: '2px 0' }}>
            {entry.name}: {formatCurrency(entry.value)}
          </p>
        ))}
      </div>
    );
  };

  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
          <XAxis dataKey="fy" stroke="#94a3b8" fontSize={12} />
          <YAxis tickFormatter={formatCurrency} stroke="#94a3b8" fontSize={12} width={80} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: '0.85rem' }} />
          <Bar dataKey="Revenue" fill="#3b82f6" name="Revenue" radius={[4, 4, 0, 0]} />
          <Bar dataKey="NetIncome" fill="#10b981" name="Net Income" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
