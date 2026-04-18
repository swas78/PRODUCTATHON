import { useEffect, useState } from 'react';
import './ComparisonModal.css';

export default function ComparisonModal({ hotel1, hotel2, comparisonText, comparisonLoading, onClose }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true));
  }, []);

  const handleClose = () => {
    setVisible(false);
    setTimeout(onClose, 300);
  };

  // Build comparison rows from mapped hotel data
  const buildRows = () => {
    if (!hotel1 || !hotel2) return [];
    return [
      {
        key: 'match',
        label: 'Match Score',
        icon: '🎯',
        value1: hotel1.matchScore || 0,
        value2: hotel2.matchScore || 0,
      },
      {
        key: 'rating',
        label: 'Guest Rating',
        icon: '⭐',
        value1: Math.round((hotel1.rating || 0) * 10),
        value2: Math.round((hotel2.rating || 0) * 10),
      },
      {
        key: 'price',
        label: 'Price / night',
        icon: '💰',
        // Invert price so lower = better
        value1: hotel2.price > hotel1.price ? 85 : 55,
        value2: hotel1.price > hotel2.price ? 85 : 55,
      },
      {
        key: 'amenities',
        label: 'Amenities',
        icon: '🛎️',
        value1: Math.min(100, (hotel1.amenities?.length || 0) * 15),
        value2: Math.min(100, (hotel2.amenities?.length || 0) * 15),
      },
      {
        key: 'reviews',
        label: 'Review Count',
        icon: '💬',
        value1: Math.min(100, Math.round((hotel1.reviews || 0) / 20)),
        value2: Math.min(100, Math.round((hotel2.reviews || 0) / 20)),
      },
    ].map(row => ({
      ...row,
      winner: row.value1 > row.value2 ? 1 : row.value2 > row.value1 ? 2 : null,
    }));
  };

  const rows = buildRows();

  const getAIVerdict = () => {
    if (comparisonText) return comparisonText;
    const score1 = rows.reduce((s, r) => s + (r.winner === 1 ? 1 : 0), 0);
    const score2 = rows.reduce((s, r) => s + (r.winner === 2 ? 1 : 0), 0);
    if (score1 > score2) {
      return `${hotel1?.name} edges ahead overall. It wins on more metrics — but ${hotel2?.name} may suit you better if price is the priority.`;
    } else if (score2 > score1) {
      return `${hotel2?.name} edges ahead overall. It wins on more metrics — but ${hotel1?.name} may suit you better if price is the priority.`;
    }
    return `Both hotels are evenly matched. Your choice should depend on which amenities matter most for your trip.`;
  };

  if (!hotel1 || !hotel2) return null;

  const img1 = hotel1.images?.[0] || `https://source.unsplash.com/200x140/?hotel`;
  const img2 = hotel2.images?.[0] || `https://source.unsplash.com/200x140/?hotel,room`;
  const price1 = (hotel1.price || 0).toLocaleString();
  const price2 = (hotel2.price || 0).toLocaleString();

  return (
    <div className={`compare-overlay ${visible ? 'compare-overlay--visible' : ''}`} onClick={handleClose}>
      <div className={`compare-modal ${visible ? 'compare-modal--visible' : ''}`} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="compare-modal__header">
          <h2 className="compare-modal__title">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <path d="M8 3H4a2 2 0 00-2 2v14a2 2 0 002 2h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M14 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M11 1v20" stroke="currentColor" strokeWidth="1.5" strokeDasharray="3 3"/>
            </svg>
            Hotel Comparison
          </h2>
          <button className="compare-modal__close" onClick={handleClose} id="compare-close-btn">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4.5 4.5l9 9M13.5 4.5l-9 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        {/* Hotel Headers */}
        <div className="compare-modal__hotels">
          <div className="compare-modal__hotel-header">
            <img src={img1} alt={hotel1.name} className="compare-modal__hotel-img" />
            <h3>{hotel1.name}</h3>
            <span className="compare-modal__hotel-price">₹{price1}/night</span>
            <div className="badge-match">{hotel1.matchScore || 0}% match</div>
          </div>
          <div className="compare-modal__vs">VS</div>
          <div className="compare-modal__hotel-header">
            <img src={img2} alt={hotel2.name} className="compare-modal__hotel-img" />
            <h3>{hotel2.name}</h3>
            <span className="compare-modal__hotel-price">₹{price2}/night</span>
            <div className="badge-match">{hotel2.matchScore || 0}% match</div>
          </div>
        </div>

        {/* Comparison Rows */}
        <div className="compare-modal__metrics">
          {rows.map((cat, i) => (
            <div key={cat.key} className="compare-modal__row" style={{ animationDelay: `${i * 80}ms` }}>
              <div className={`compare-modal__cell ${cat.winner === 1 ? 'compare-modal__cell--winner' : cat.winner === null ? 'compare-modal__cell--tie' : ''}`}>
                <div className="compare-modal__bar-wrapper">
                  <div className="compare-modal__bar" style={{ width: `${cat.value1}%` }} />
                </div>
                <span className="compare-modal__cell-value">{cat.value1}</span>
              </div>
              <div className="compare-modal__row-label">
                <span className="compare-modal__row-icon">{cat.icon}</span>
                <span>{cat.label}</span>
              </div>
              <div className={`compare-modal__cell compare-modal__cell--right ${cat.winner === 2 ? 'compare-modal__cell--winner' : cat.winner === null ? 'compare-modal__cell--tie' : ''}`}>
                <span className="compare-modal__cell-value">{cat.value2}</span>
                <div className="compare-modal__bar-wrapper">
                  <div className="compare-modal__bar" style={{ width: `${cat.value2}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* AI Verdict */}
        <div className="compare-modal__verdict">
          <div className="compare-modal__verdict-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 1l1.5 3 3.5.5-2.5 2.5.5 3.5L8 9l-3 1.5.5-3.5L3 4.5l3.5-.5L8 1z" fill="currentColor"/>
            </svg>
            <span>AI Verdict</span>
          </div>
          {comparisonLoading ? (
            <p style={{ opacity: 0.6 }}>Analysing hotels...</p>
          ) : (
            <p>{getAIVerdict()}</p>
          )}
        </div>

        {/* Amenities */}
        <div className="compare-modal__amenities">
          <h4>Amenities</h4>
          <div className="compare-modal__amenity-grid">
            <div className="compare-modal__amenity-col">
              {(hotel1.amenities || []).map((a, i) => (
                <span key={i} className={`compare-modal__amenity-chip ${(hotel2.amenities || []).includes(a) ? '' : 'compare-modal__amenity-chip--unique'}`}>
                  {(hotel2.amenities || []).includes(a) ? '' : '✦ '}{a}
                </span>
              ))}
            </div>
            <div className="compare-modal__amenity-col">
              {(hotel2.amenities || []).map((a, i) => (
                <span key={i} className={`compare-modal__amenity-chip ${(hotel1.amenities || []).includes(a) ? '' : 'compare-modal__amenity-chip--unique'}`}>
                  {(hotel1.amenities || []).includes(a) ? '' : '✦ '}{a}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
