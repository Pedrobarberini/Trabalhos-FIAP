import React from 'react';
import { Icon } from './Icon.jsx';
export function Stat({ label, value, suffix, icon, note, alert }) {
  return (
    <div className={`stat ${alert ? 'stat-alert' : ''}`}>
      <div className="stat-top">
        <span>{label}</span>
        <Icon type={icon} size={19} />
      </div>
      <div className="stat-value">
        {value} <small>{suffix}</small>
      </div>
      <div className="stat-note">{note}</div>
    </div>
  );
}
