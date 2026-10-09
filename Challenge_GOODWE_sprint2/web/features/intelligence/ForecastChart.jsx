import React from 'react';
import { number } from '../../shared/format.mjs';
import { Icon } from '../../shared/components/Icon.jsx';
export function Forecast({ value, error }) {
  if (!value)
    return <div className="empty">{error || 'Calculando previsão com o histórico validado…'}</div>;
  const max = Math.max(value.capacity_kw, ...value.hours.map((h) => h.expected_kw), 1);
  const points = value.hours
    .map((h, i) => `${35 + i * 24},${170 - (h.expected_kw / max) * 135}`)
    .join(' ');
  return (
    <>
      <div className="chart-meta">
        <span>
          <i className="dot green" /> Demanda prevista
        </span>
        <span>
          <i className="dot pale" /> Capacidade: {number(value.capacity_kw)} kW
        </span>
        <span className="peak">
          Pico às {value.peak_hour}h · {number(value.peak_kw)} kW
        </span>
      </div>
      <svg
        className="chart"
        viewBox="0 0 622 208"
        role="img"
        aria-label={`Previsão para ${value.date}. Pico de ${value.peak_kw} kW às ${value.peak_hour} horas.`}
      >
        <defs>
          <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#bedc74" stopOpacity=".55" />
            <stop offset="100%" stopColor="#bedc74" stopOpacity=".04" />
          </linearGradient>
        </defs>
        {[0, 0.5, 1].map((f) => (
          <g key={f}>
            <line
              x1="32"
              x2="602"
              y1={170 - f * 135}
              y2={170 - f * 135}
              stroke="#e8ebe2"
              strokeDasharray={f === 1 ? '5 5' : ''}
            />
            <text x="0" y={174 - f * 135}>
              {number(max * f)}
            </text>
          </g>
        ))}
        <polygon points={`35,170 ${points} 587,170`} fill="url(#area)" />
        <polyline
          points={points}
          fill="none"
          stroke="#49774a"
          strokeWidth="3"
          strokeLinejoin="round"
        />
        {value.hours.map((h, i) => (
          <circle
            key={i}
            cx={35 + i * 24}
            cy={170 - (h.expected_kw / max) * 135}
            r="3"
            fill="#49774a"
          >
            <title>
              {h.hour}h: {number(h.expected_kw)} kW
            </title>
          </circle>
        ))}
        {[0, 6, 12, 18, 23].map((h) => (
          <text key={h} x={35 + h * 24} y="198" textAnchor="middle">
            {String(h).padStart(2, '0')}:00
          </text>
        ))}
      </svg>
      <div className="chart-note">
        <Icon type="intelligence" size={17} />
        <span>{value.recommendation}</span>
      </div>
    </>
  );
}
