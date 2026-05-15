"use client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

export const YieldCurveChart = ({ maturities }) => {
  if (!maturities || !maturities.length) {
    return <div className="empty-state"><p>No yield curve data available.</p></div>;
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;
    return (
      <div style={{
        background: '#1a2332', border: '1px solid rgba(148,163,184,0.15)',
        borderRadius: '8px', padding: '12px 16px', fontSize: '0.85rem',
      }}>
        <p style={{ fontWeight: 700, marginBottom: 4 }}>{label}</p>
        <p style={{ color: '#22d3ee' }}>Yield: {payload[0].value}%</p>
      </div>
    );
  };

  return (
    <div style={{ width: '100%', height: 350 }}>
      <ResponsiveContainer>
        <LineChart data={maturities} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <defs>
            <linearGradient id="yieldGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#22d3ee" />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
          <XAxis dataKey="label" stroke="#94a3b8" fontSize={12} />
          <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={12}
            tickFormatter={(v) => `${v}%`} />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="rate"
            stroke="url(#yieldGradient)"
            strokeWidth={3}
            dot={{ r: 5, fill: '#22d3ee', stroke: '#0a0e17', strokeWidth: 2 }}
            activeDot={{ r: 7, fill: '#22d3ee', stroke: '#0a0e17', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
