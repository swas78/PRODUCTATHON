import { useState } from 'react';
import './HotelCard.css';

export default function HotelCard({ hotel, index, onViewDetails, isSelected, onToggleCompare }) {
  const [expanded, setExpanded] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  return (
    <div
      className={`hotel-card skeu-card ${isSelected ? 'hotel-card--selected' : ''}`}
      style={{ animationDelay: `${index * 100}ms` }}
      id={`hotel-card-${hotel.id}`}
    >
      {/* Image Section */}
      <div className="hotel-card__image-wrapper">
        {!imageLoaded && <div className="skeleton hotel-card__image-skeleton" />}
        <img
          src={hotel.images?.[0] || hotel.image || `https://source.unsplash.com/400x280/?hotel`}
          alt={hotel.name}
          className={`hotel-card__image ${imageLoaded ? 'hotel-card__image--loaded' : ''}`}
          onLoad={() => setImageLoaded(true)}
        />
        <div className="hotel-card__image-overlay" />
        <div className="badge-match hotel-card__badge">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M8.5 2.5L3.75 7.25 1.5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          {hotel.matchScore}% match
        </div>

        {/* Comparison Checkbox */}
        {onToggleCompare && (
          <label className={`hotel-card__compare-check ${isSelected ? 'hotel-card__compare-check--active' : ''}`} id={`compare-check-${hotel.id}`}>
            <input
              type="checkbox"
              checked={isSelected || false}
              onChange={() => onToggleCompare(hotel.id)}
            />
            <div className="hotel-card__compare-box">
              {isSelected && (
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M10 3L4.5 8.5 2 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
            <span>Compare</span>
          </label>
        )}
      </div>

      {/* Content Section */}
      <div className="hotel-card__body">
        <div className="hotel-card__top-row">
          <div className="hotel-card__info">
            <h3 className="hotel-card__name">{hotel.name}</h3>
            <p className="hotel-card__location">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M6 1C3.791 1 2 2.791 2 5c0 3 4 6 4 6s4-3 4-6c0-2.209-1.791-4-4-4z" stroke="currentColor" strokeWidth="1"/>
                <circle cx="6" cy="5" r="1.5" stroke="currentColor" strokeWidth="1"/>
              </svg>
              {hotel.distance}
            </p>
          </div>
          <div className="hotel-card__price">
            <span className="hotel-card__price-value">{hotel.currency || '₹'}{(hotel.price || 0).toLocaleString()}</span>
            <span className="hotel-card__price-unit">/night</span>
          </div>
        </div>

        {/* Rating */}
        <div className="hotel-card__rating">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1l1.76 3.58 3.94.57-2.85 2.78.67 3.94L7 10.04l-3.52 1.85.67-3.94L1.3 5.15l3.94-.57L7 1z" fill="#F59E0B"/>
          </svg>
          <span className="hotel-card__rating-value">{hotel.rating}</span>
          <span className="hotel-card__rating-count">({(hotel.reviews || 0).toLocaleString()})</span>
        </div>

        {/* AI Explanation */}
        <div className="hotel-card__ai-box">
          <div className="hotel-card__ai-header">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1l1.2 2.4 2.6.4-1.9 1.8.5 2.6L7 7.2 4.6 8.2l.5-2.6L3.2 3.8l2.6-.4L7 1z" fill="currentColor"/>
            </svg>
            <span>AI Insight</span>
          </div>
          <p className="hotel-card__ai-text">{hotel.aiExplanation}</p>
        </div>

        {/* Guest Verdict (Feature 3) */}
        {hotel.guestVerdict && (
          <div className="hotel-card__verdict">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M13 9.667a1.333 1.333 0 01-1.333 1.333H4.333L1 14V2.333A1.333 1.333 0 012.333 1h9.334A1.333 1.333 0 0113 2.333v7.334z" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <p>{hotel.guestVerdict}</p>
          </div>
        )}

        {/* Actions */}
        <div className="hotel-card__actions">
          <button
            className="btn-primary hotel-card__view-btn"
            onClick={onViewDetails}
            id={`hotel-view-${hotel.id}`}
          >
            View Details
          </button>
          <button
            className={`btn-secondary hotel-card__why-btn ${expanded ? 'hotel-card__why-btn--active' : ''}`}
            onClick={() => setExpanded(!expanded)}
            id={`hotel-why-${hotel.id}`}
          >
            {expanded ? 'Hide' : 'Why this?'}
          </button>
        </div>

        {/* Expandable Why Section */}
        <div className={`hotel-card__expand ${expanded ? 'hotel-card__expand--open' : ''}`}>
          <div className="hotel-card__expand-inner">
            <h4 className="hotel-card__expand-title">Why This Hotel</h4>
            <div className="hotel-card__reasons">
              {(hotel.highlights?.length ? hotel.highlights : hotel.amenities || []).slice(0, 5).map((item, i) => (
                <div
                  key={i}
                  className="hotel-card__reason hotel-card__reason--matched"
                >
                  <div className="hotel-card__reason-icon">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path d="M11.667 3.5L5.25 9.917 2.333 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <span>{typeof item === 'string' ? item : item.label}</span>
                  <span className="hotel-card__reason-status">Matched</span>
                </div>
              ))}
            </div>

            {/* Score Bar */}
            <div className="hotel-card__score-section">
              <div className="hotel-card__score-label">
                <span>Overall Score</span>
                <span className="hotel-card__score-value">{hotel.matchScore}%</span>
              </div>
              <div className="hotel-card__score-track">
                <div
                  className="hotel-card__score-fill"
                  style={{ width: expanded ? `${hotel.matchScore}%` : '0%' }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
