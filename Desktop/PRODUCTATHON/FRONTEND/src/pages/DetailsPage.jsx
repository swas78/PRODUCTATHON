import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { explain } from '../api';
import './DetailsPage.css';

export default function DetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const query = location.state?.query || '';

  // Hotel data passed via navigation state from ResultsPage
  const hotelFromState = location.state?.hotel || null;
  const [hotel, setHotel] = useState(hotelFromState);
  const [breakdown, setBreakdown] = useState(null);
  const [breakdownOpen, setBreakdownOpen] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [activeImage, setActiveImage] = useState(0);
  const [isSticky, setIsSticky] = useState(false);
  const headerRef = useRef(null);

  useEffect(() => {
    setLoaded(true);
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    const handleScroll = () => setIsSticky(window.scrollY > 300);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Fetch logic breakdown from backend
  const loadBreakdown = async () => {
    if (breakdown) { setBreakdownOpen(o => !o); return; }
    try {
      const data = await explain(parseInt(id));
      setBreakdown(data);
      setBreakdownOpen(true);
    } catch (e) {
      console.error('Explain failed:', e);
    }
  };

  if (!hotel) {
    return (
      <div className="details__not-found">
        <h2>Hotel not found</h2>
        <p style={{ color: 'var(--text-dim)', marginTop: 8 }}>
          Please go back and select a hotel from the results.
        </p>
        <button className="btn-primary" onClick={() => navigate('/results')} style={{ marginTop: 20 }}>
          Back to Results
        </button>
      </div>
    );
  }

  const images = hotel.images?.length
    ? hotel.images
    : [`https://source.unsplash.com/800x500/?hotel,${encodeURIComponent(hotel.location || 'india')}`];

  return (
    <div className="details">
      {/* Sticky Header */}
      <header className={`details__sticky-header ${isSticky ? 'details__sticky-header--visible' : ''}`}>
        <div className="details__sticky-inner container">
          <button className="details__sticky-back" onClick={() => navigate(-1)}>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M11 13.5l-4.5-4.5L11 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <div className="details__sticky-info">
            <span className="details__sticky-name">{hotel.name}</span>
            <span className="details__sticky-price">₹{(hotel.price || hotel.price_per_night || 0).toLocaleString()}/night</span>
          </div>
          <button className="btn-primary details__sticky-book" id="sticky-book-btn">
            Book Now
          </button>
        </div>
      </header>

      {/* Hero */}
      <div className={`details__hero ${loaded ? 'details__hero--visible' : ''}`} ref={headerRef}>
        <button className="details__back-btn" onClick={() => navigate(-1)} id="details-back-btn">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12.5 15l-5-5 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        <div className="details__image-container">
          <img src={images[activeImage]} alt={hotel.name} className="details__hero-image" />
          <div className="details__image-overlay" />
        </div>
        <div className="details__image-dots">
          {images.map((_, i) => (
            <button
              key={i}
              className={`details__image-dot ${activeImage === i ? 'details__image-dot--active' : ''}`}
              onClick={() => setActiveImage(i)}
            />
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="details__content container-narrow">
        <div className={`details__info-card ${loaded ? 'details__info-card--visible' : ''}`}>
          <div className="details__info-top">
            <div className="details__info-main">
              {hotel.matchScore > 0 && (
                <div className="badge-match details__match-badge">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M10 3L4.5 8.5 2 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {hotel.matchScore}% match
                </div>
              )}
              <h1 className="details__hotel-name">{hotel.name}</h1>
              <p className="details__hotel-location">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M7 1.167C4.424 1.167 2.333 3.257 2.333 5.833 2.333 9.333 7 12.833 7 12.833s4.667-3.5 4.667-7c0-2.577-2.09-4.667-4.667-4.667z" stroke="currentColor" strokeWidth="1.2"/>
                  <circle cx="7" cy="5.833" r="1.75" stroke="currentColor" strokeWidth="1.2"/>
                </svg>
                {hotel.location}
              </p>
            </div>
            <div className="details__price-block">
              <span className="details__price-amount">₹{(hotel.price || hotel.price_per_night || 0).toLocaleString()}</span>
              <span className="details__price-unit">/ night</span>
            </div>
          </div>
          <div className="details__rating-row">
            <div className="details__rating">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 1.333l1.854 3.76 4.146.604-3 2.923.708 4.127L8 10.64l-3.708 1.95.708-4.127-3-2.923 4.146-.604L8 1.333z" fill="#F59E0B"/>
              </svg>
              <span className="details__rating-value">{hotel.rating}</span>
              <span className="details__rating-count">({(hotel.reviews || 0).toLocaleString()} reviews)</span>
            </div>
          </div>
        </div>

        {/* AI Explanation */}
        {hotel.aiExplanationLong && (
          <section className={`details__section ${loaded ? 'details__section--visible' : ''}`} style={{animationDelay: '0.3s'}}>
            <h2 className="details__section-title">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                <circle cx="11" cy="11" r="9" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M11 7v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              Why it fits your trip
            </h2>
            <div className="details__ai-explanation">
              <div className="details__ai-icon">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M9 1.5l1.5 3 3.5.5-2.5 2.5.5 3.5L9 9.5 6 11l.5-3.5L4 5l3.5-.5L9 1.5z" fill="currentColor"/>
                </svg>
              </div>
              <p>{hotel.aiExplanationLong}</p>
            </div>
          </section>
        )}

        {/* Logic Breakdown (Why This Hotel) */}
        <section className={`details__section ${loaded ? 'details__section--visible' : ''}`} style={{animationDelay: '0.4s'}}>
          <h2 className="details__section-title">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <rect x="3" y="3" width="16" height="16" rx="3" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M7 11h8M7 7h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Score Breakdown
          </h2>
          <button
            className="details__logic-toggle"
            onClick={loadBreakdown}
            style={{
              background: 'none', border: '1px solid var(--border)',
              borderRadius: 10, padding: '10px 16px', color: 'var(--text-dim)',
              cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', gap: 8
            }}
          >
            {breakdownOpen ? '▼' : '▶'} Why was this hotel selected?
          </button>

          {breakdownOpen && breakdown && (
            <div className="details__breakdown" style={{ marginTop: 16 }}>
              <div style={{ fontWeight: 700, marginBottom: 12, fontSize: 15 }}>
                Overall match: {Math.round((breakdown.composite_score || 0) * 100)}%
              </div>
              {(breakdown.components || []).map((comp, i) => (
                <div key={i} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 }}>
                    <span style={{ width: 180, fontSize: 13, color: 'var(--text-dim)', flexShrink: 0 }}>
                      {comp.name.replace(/_/g, ' ')} ({comp.weight_percent}%)
                    </span>
                    <div style={{ flex: 1, background: 'var(--surface2)', borderRadius: 4, height: 6 }}>
                      <div style={{
                        width: `${Math.round(comp.score * 100)}%`,
                        height: 6, borderRadius: 4,
                        background: comp.score >= 0.8 ? '#00d4aa' : comp.score >= 0.5 ? '#6c63ff' : '#ef476f'
                      }} />
                    </div>
                    <span style={{ width: 36, textAlign: 'right', fontSize: 12, fontWeight: 700 }}>
                      {Math.round(comp.score * 100)}%
                    </span>
                  </div>
                  <p style={{ fontSize: 12, color: 'var(--text-dim)', marginLeft: 192 }}>{comp.detail}</p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Amenities */}
        <section className={`details__section ${loaded ? 'details__section--visible' : ''}`} style={{animationDelay: '0.6s'}}>
          <h2 className="details__section-title">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <rect x="3" y="3" width="16" height="16" rx="3" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M3 8h16" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M8 8v11" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            Amenities
          </h2>
          <div className="details__amenities">
            {(hotel.amenities || []).map((a, i) => (
              <span key={i} className="details__amenity-chip">{a}</span>
            ))}
          </div>
        </section>

        {/* Guest Highlights */}
        {(hotel.highlights || []).length > 0 && (
          <section className={`details__section ${loaded ? 'details__section--visible' : ''}`} style={{animationDelay: '0.75s'}}>
            <h2 className="details__section-title">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" strokeWidth="1.5" transform="scale(0.92)"/>
              </svg>
              What guests say
            </h2>
            <div className="details__reviews">
              {(hotel.guestReviews || hotel.highlights.map((h, i) => ({
                name: ['Priya S.', 'Rahul M.', 'Anjali K.'][i] || 'Guest',
                rating: 4,
                text: h
              }))).map((r, i) => (
                <div key={i} className="details__review-card">
                  <div className="details__review-header">
                    <div className="details__review-avatar">{r.name.charAt(0)}</div>
                    <div>
                      <span className="details__review-name">{r.name}</span>
                      <div className="details__review-stars">
                        {Array.from({ length: r.rating }).map((_, j) => (
                          <svg key={j} width="12" height="12" viewBox="0 0 12 12" fill="none">
                            <path d="M6 1l1.39 2.82 3.11.45-2.25 2.19.53 3.09L6 8.09l-2.78 1.46.53-3.09L1.5 4.27l3.11-.45L6 1z" fill="#F59E0B"/>
                          </svg>
                        ))}
                      </div>
                    </div>
                  </div>
                  <p className="details__review-text">"{r.text}"</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Book CTA */}
        <div className={`details__cta-section ${loaded ? 'details__cta-section--visible' : ''}`}>
          <button className="btn-primary details__book-btn" id="details-book-btn">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M17.5 12.5v4.167a1.667 1.667 0 01-1.667 1.666H4.167A1.667 1.667 0 012.5 16.667V12.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Book Now — ₹{(hotel.price || hotel.price_per_night || 0).toLocaleString()}/night
          </button>
        </div>
      </div>
    </div>
  );
}