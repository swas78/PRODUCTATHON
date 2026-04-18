import { useEffect, useState } from 'react';
import './ConfidenceBar.css';

export default function ConfidenceBar({ confidence }) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 200);
    return () => clearTimeout(timer);
  }, []);

  if (!confidence) return null;

  const { score, level, label, message } = confidence;

  const barColor = level === 'high'
    ? 'var(--color-success)'
    : level === 'medium'
    ? '#EAB308'
    : 'var(--color-error)';

  return (
    <div className={`confidence ${animated ? 'confidence--visible' : ''} confidence--${level}`} id="confidence-bar">
      <div className="confidence__header">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.5"/>
          <path d="M8 5.5v3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          <circle cx="8" cy="11" r="0.75" fill="currentColor"/>
        </svg>
        <span className="confidence__label">How well I understood your request</span>
        <span className="confidence__score" style={{ color: barColor }}>{score}%</span>
      </div>

      <div className="confidence__track">
        <div
          className="confidence__fill"
          style={{
            width: animated ? `${score}%` : '0%',
            background: `linear-gradient(90deg, ${barColor}, ${barColor}dd)`,
            boxShadow: animated ? `0 0 12px ${barColor}40` : 'none'
          }}
        />
      </div>

      <div className="confidence__footer">
        <span
          className="confidence__status"
          style={{ color: barColor }}
        >
          {label}
        </span>
        {message && (
          <p className="confidence__message">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M6 1C3.24 1 1 3.24 1 6s2.24 5 5 5 5-2.24 5-5S8.76 1 6 1z" stroke="currentColor" strokeWidth="1"/>
              <path d="M6 4v2.5" stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
              <circle cx="6" cy="8.5" r="0.5" fill="currentColor"/>
            </svg>
            {message}
          </p>
        )}
      </div>
    </div>
  );
}
