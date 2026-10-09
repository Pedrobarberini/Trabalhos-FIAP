import React from 'react';

export function Icon({ type = 'bolt', size = 20 }) {
  const paths = {
    bolt: 'm13 2-9 12h7l-1 8 10-12h-7l1-8Z',
    overview: 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z',
    sessions: 'M7 3v4m10-4v4M4 10h16M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1Zm3 9h3m3 0h2m-8 3h3',
    invoices: 'M6 3h12v19l-3-2-3 2-3-2-3 2V3Zm3 5h6m-6 4h6m-6 4h3',
    intelligence: 'm12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z',
    resident: 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Zm-13 14v-2a9 9 0 0 1 18 0v2',
    arrow: 'M5 12h14m-5-5 5 5-5 5',
    plus: 'M12 5v14M5 12h14',
    check: 'm5 12 4 4L19 6',
    close: 'm6 6 12 12M6 18 18 6',
    download: 'M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4',
    clock: 'M12 8v4l3 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z',
    alert: 'm12 3 10 18H2L12 3Zm0 6v5m0 3v1',
    charger:
      'M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M3 21h14M8 6h4v5H8zM15 10h3v7a2 2 0 0 0 4 0V7l-3-3',
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[type] || paths.bolt} />
    </svg>
  );
}
