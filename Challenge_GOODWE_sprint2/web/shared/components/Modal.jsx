import React, { useEffect, useRef } from 'react';
import { Icon } from './Icon.jsx';

const FOCUSABLE =
  'button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]';

export function Modal({ title, busy, onClose, children }) {
  const element = useRef(null);
  const state = useRef({ busy, onClose });
  state.current = { busy, onClose };
  useEffect(() => {
    const previous = document.activeElement;
    element.current.querySelector('input, textarea, select, button')?.focus();
    function handleKey(event) {
      if (event.key === 'Escape' && !state.current.busy) state.current.onClose();
      if (event.key !== 'Tab') return;
      const fields = [...element.current.querySelectorAll(FOCUSABLE)];
      const next = event.shiftKey ? fields.at(-1) : fields[0];
      const boundary = event.shiftKey ? fields[0] : fields.at(-1);
      if (document.activeElement === boundary) {
        event.preventDefault();
        next?.focus();
      }
    }
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('keydown', handleKey);
      if (previous?.isConnected) previous.focus();
    };
  }, []);

  return (
    <div
      className="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget && !busy) onClose();
      }}
    >
      <section ref={element} className="modal" role="dialog" aria-modal="true" aria-label={title}>
        <button
          className="modal-close"
          aria-label="Fechar janela"
          disabled={busy}
          onClick={onClose}
        >
          <Icon type="close" />
        </button>
        {children}
      </section>
    </div>
  );
}
