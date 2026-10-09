import React from 'react';

export function PanelTitle({ title, caption, action, tag }) {
  return (
    <div className="panel-title">
      <div>
        <h3>{title}</h3>
        {caption && <p>{caption}</p>}
      </div>
      {action}
      {tag && <span className="model-tag">{tag}</span>}
    </div>
  );
}
