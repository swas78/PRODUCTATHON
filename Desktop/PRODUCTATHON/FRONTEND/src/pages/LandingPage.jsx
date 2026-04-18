import { useNavigate } from 'react-router-dom';
import { useEffect, useRef, useState, useCallback } from 'react';
import './LandingPage.css';

const QUERIES = [
  '"Quiet hotel in Manali for writing..."',
  '"Work trip in Delhi with fast Wi-Fi..."',
  '"Romantic beach getaway under ₹8000..."',
  '"Family hotel with pool near Jaipur..."',
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [intro, setIntro] = useState(true);
  const [ready, setReady] = useState(false);
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  const [typed, setTyped] = useState('');
  const [qi, setQi] = useState(0);
  const [counts, setCounts] = useState({ hotels: 0, acc: 0, speed: 0, cities: 0 });
  const [counting, setCounting] = useState(false);
  const [vis, setVis] = useState({});

  const refs = {
    stats: useRef(null),
    how: useRef(null),
    features: useRef(null),
    trust: useRef(null),
    dest: useRef(null),
    cta: useRef(null),
  };

  // Intro timer
  useEffect(() => {
    const t = setTimeout(() => { setIntro(false); setTimeout(() => setReady(true), 80); }, 2800);
    return () => clearTimeout(t);
  }, []);

  // Mouse
  useEffect(() => {
    const fn = (e) => {
      setMouse({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      });
    };
    window.addEventListener('mousemove', fn);
    return () => window.removeEventListener('mousemove', fn);
  }, []);

  // Typing
  useEffect(() => {
    if (!ready) return;
    const q = QUERIES[qi];
    let c = 0;
    setTyped('');
    const iv = setInterval(() => {
      c++;
      setTyped(q.slice(0, c));
      if (c >= q.length) { clearInterval(iv); setTimeout(() => setQi(p => (p + 1) % QUERIES.length), 2200); }
    }, 45);
    return () => clearInterval(iv);
  }, [ready, qi]);

  // Counters
  useEffect(() => {
    if (!counting) return;
    const end = { hotels: 10000, acc: 98, speed: 3, cities: 50 };
    let f = 0;
    const iv = setInterval(() => {
      f++;
      const t = Math.min(f / 50, 1);
      const e = 1 - Math.pow(1 - t, 3);
      setCounts({ hotels: Math.round(end.hotels * e), acc: Math.round(end.acc * e), speed: +(end.speed * e).toFixed(1), cities: Math.round(end.cities * e) });
      if (f >= 50) clearInterval(iv);
    }, 30);
    return () => clearInterval(iv);
  }, [counting]);

  // Scroll observer
  const observe = useCallback((node, key) => {
    if (!node) return;
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        setVis(p => ({ ...p, [key]: true }));
        if (key === 'stats') setCounting(true);
        obs.disconnect();
      }
    }, { threshold: 0.15 });
    obs.observe(node);
  }, []);

  useEffect(() => {
    if (intro) return;
    Object.entries(refs).forEach(([k, r]) => r.current && observe(r.current, k));
  }, [intro, observe]);

  /* =========== INTRO =========== */
  if (intro) {
    return (
      <div className="IS-intro">
        <div className="IS-intro__sky">
          {[1,2,3,4,5].map(i => <div key={i} className={`IS-intro__cloud IS-intro__cloud--${i}`} />)}
          <div className="IS-intro__plane">✈️</div>
          <div className="IS-intro__contrail" />
        </div>
        <div className="IS-intro__center">
          <div className="IS-intro__icon">
            <svg viewBox="0 0 64 64" width="26" height="26" fill="none">
              <path d="M4 34l24-6 4-16 4 16 24 6-24 6-4 16-4-16z" fill="#fff"/>
              <circle cx="32" cy="34" r="3" fill="#0f172a"/>
            </svg>
          </div>
          <h1 className="IS-intro__name">IntentStay</h1>
          <p className="IS-intro__tag">AI Hotel Discovery</p>
          <div className="IS-intro__loader"><div className="IS-intro__loader-bar" /></div>
        </div>
      </div>
    );
  }

  /* =========== MAIN PAGE =========== */
  return (
    <div className="IS">
      {/* BG Decorations */}
      <div className="IS__bg" aria-hidden="true">
        <div className="IS__bg-grad" />
        <div className="IS__bg-orb IS__bg-orb--1" style={{ transform: `translate(${mouse.x * 18}px,${mouse.y * 18}px)` }} />
        <div className="IS__bg-orb IS__bg-orb--2" style={{ transform: `translate(${mouse.x * -14}px,${mouse.y * -14}px)` }} />
        {[...Array(14)].map((_, i) => <div key={i} className={`IS__bg-dot IS__bg-dot--${i + 1}`} />)}
      </div>

      {/* NAV */}
      <nav className={`IS__nav ${ready ? 'IS__nav--in' : ''}`}>
        <div className="IS__nav-left">
          <div className="IS__logo">
            <svg viewBox="0 0 64 64" width="18" height="18" fill="none">
              <path d="M4 34l24-6 4-16 4 16 24 6-24 6-4 16-4-16z" fill="#fff"/>
              <circle cx="32" cy="34" r="3" fill="#0f172a"/>
            </svg>
          </div>
          <span className="IS__brand">IntentStay</span>
        </div>
        <div className="IS__nav-right">
          <a className="IS__link" onClick={() => refs.how.current?.scrollIntoView({ behavior: 'smooth' })}>How it works</a>
          <a className="IS__link" onClick={() => refs.features.current?.scrollIntoView({ behavior: 'smooth' })}>Features</a>
          <a className="IS__link" onClick={() => refs.trust.current?.scrollIntoView({ behavior: 'smooth' })}>Trust</a>
          <button className="IS__nav-cta" onClick={() => navigate('/discover')}>Get Started</button>
        </div>
      </nav>

      {/* ════════ HERO ════════ */}
      <section className="IS__hero">
        <div className="IS__hero-wrap">
          {/* Left */}
          <div className={`IS__hero-text ${ready ? 'IS__hero-text--in' : ''}`}>
            <div className="IS__chip">
              <span className="IS__chip-dot" />
              AI-Powered Discovery
              <span className="IS__chip-badge">NEW</span>
            </div>

            <h1 className="IS__h1">
              Find your perfect hotel<br/>
              <span className="IS__h1-em">in one sentence</span>
            </h1>

            <p className="IS__p">
              No filters, no endless scrolling. Just describe your ideal stay — our AI finds
              the best match with human-like reasoning.
            </p>

            <div className="IS__search">
              <svg className="IS__search-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
                <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="2"/>
                <path d="M14 14l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <span className="IS__search-txt">{typed}<span className="IS__blink" /></span>
              <button className="IS__search-go" onClick={() => navigate('/discover')}>→</button>
            </div>

            <div className="IS__cta-group">
              <button className="IS__cta-main" onClick={() => navigate('/discover')} id="hero-cta">
                Start Exploring
                <svg width="16" height="16" viewBox="0 0 18 18" fill="none"><path d="M3.75 9h10.5M10.5 4.5L15 9l-4.5 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </button>
              <span className="IS__cta-note">Free · No signup · Instant results</span>
            </div>
          </div>

          {/* Right — 3D Card */}
          <div
            className={`IS__hero-card ${ready ? 'IS__hero-card--in' : ''}`}
            style={{ transform: `perspective(900px) rotateY(${mouse.x * -2.5}deg) rotateX(${mouse.y * 1.5}deg)` }}
          >
            <div className="IS__preview">
              <div className="IS__preview-top">
                <div className="IS__preview-shimmer" />
                <span className="IS__preview-match">⭐ 98% Match</span>
              </div>
              <div className="IS__preview-body">
                <h3>The Oberoi, New Delhi</h3>
                <p className="IS__preview-loc">📍 New Delhi, India</p>
                <div className="IS__preview-tags">
                  <span>🌐 Fast Wi-Fi</span><span>🏊 Pool</span><span>🍽️ Dining</span>
                </div>
                <div className="IS__preview-foot">
                  <strong>₹8,500<small>/night</small></strong>
                  <span className="IS__preview-rec">✨ AI Pick</span>
                </div>
              </div>
              <div className="IS__pop IS__pop--1">🔍 Intent Parsed</div>
              <div className="IS__pop IS__pop--2">✅ 5/5 Criteria</div>
              <div className="IS__pop IS__pop--3">💬 "Perfect fit"</div>
            </div>
          </div>
        </div>

        {/* Floating trust */}
        <div className={`IS__badges ${ready ? 'IS__badges--in' : ''}`}>
          <div className="IS__badge IS__badge--a" style={{ transform: `translate(${mouse.x * -6}px,${mouse.y * -6}px)` }}>
            <span className="IS__badge-bar" style={{ background: '#10b981' }} />🛡️ Verified Reviews
          </div>
          <div className="IS__badge IS__badge--b" style={{ transform: `translate(${mouse.x * 8}px,${mouse.y * 5}px)` }}>
            <span className="IS__badge-bar" style={{ background: '#f59e0b' }} />⚡ &lt;3s Results
          </div>
          <div className="IS__badge IS__badge--c" style={{ transform: `translate(${mouse.x * -5}px,${mouse.y * 8}px)` }}>
            <span className="IS__badge-bar" style={{ background: '#6366f1' }} />🎯 98% Accuracy
          </div>
        </div>
      </section>

      {/* ════════ STATS ════════ */}
      <section ref={refs.stats} className={`IS__stats ${vis.stats ? 'IS--vis' : ''}`}>
        {[
          { v: `${counts.hotels.toLocaleString()}+`, l: 'Hotels Indexed', i: '🏨' },
          { v: `${counts.acc}%`, l: 'Match Accuracy', i: '🎯' },
          { v: `<${counts.speed}s`, l: 'Avg Response', i: '⚡' },
          { v: `${counts.cities}+`, l: 'Cities Covered', i: '🌍' },
        ].map((s, i) => (
          <div key={i} className="IS__stat" style={{ transitionDelay: `${i * 80}ms` }}>
            <span className="IS__stat-i">{s.i}</span>
            <span className="IS__stat-v">{s.v}</span>
            <span className="IS__stat-l">{s.l}</span>
          </div>
        ))}
      </section>

      {/* ════════ HOW IT WORKS ════════ */}
      <section ref={refs.how} className={`IS__how ${vis.how ? 'IS--vis' : ''}`}>
        <div className="IS__section-inner">
          <span className="IS__tag">Simple Process</span>
          <h2 className="IS__h2">How IntentStay Works</h2>
          <p className="IS__h2-sub">Three steps to your ideal hotel — no forms, just conversation.</p>
          <div className="IS__steps">
            {[
              { n: '01', t: 'Describe Your Trip', d: 'Tell us in your own words — budget, vibe, amenities, anything.', ico: '💬', clr: '#f59e0b' },
              { n: '02', t: 'AI Finds Matches', d: 'Our engine scores 10,000+ hotels against your intent using NLP.', ico: '🧠', clr: '#6366f1' },
              { n: '03', t: 'Book with Confidence', d: 'See transparent scores, real reviews, and why each was chosen.', ico: '✅', clr: '#10b981' },
            ].map((s, i) => (
              <div key={i} className="IS__step" style={{ transitionDelay: `${i * 120}ms` }}>
                <span className="IS__step-n" style={{ background: s.clr }}>{s.n}</span>
                <span className="IS__step-ico">{s.ico}</span>
                <h3>{s.t}</h3>
                <p>{s.d}</p>
                {i < 2 && <div className="IS__step-arrow">→</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════════ FEATURES ════════ */}
      <section ref={refs.features} className={`IS__feats ${vis.features ? 'IS--vis' : ''}`}>
        <div className="IS__section-inner">
          <span className="IS__tag">Powerful Features</span>
          <h2 className="IS__h2">Why Travelers Choose IntentStay</h2>
          <div className="IS__feat-grid">
            {[
              { ico: '🗣️', t: 'Natural Language', d: 'Say it like youd tell a friend. No complex filters needed.', c: '#f59e0b' },
              { ico: '📊', t: 'AI Match Scoring', d: 'Every hotel scored against your exact requirements.', c: '#6366f1' },
              { ico: '⚖️', t: 'Side-by-Side Compare', d: 'Compare two hotels on every metric instantly.', c: '#10b981' },
              { ico: '💡', t: 'Explained Reasoning', d: 'Know why each hotel was recommended, in detail.', c: '#ec4899' },
              { ico: '🔄', t: 'Live Refinements', d: 'Add constraints, re-rank results in real time.', c: '#8b5cf6' },
              { ico: '🛡️', t: 'Trust & Transparency', d: 'Verified reviews, no hidden fees, price match.', c: '#0ea5e9' },
            ].map((f, i) => (
              <div key={i} className="IS__feat" style={{ transitionDelay: `${i * 70}ms`, '--fc': f.c }}>
                <div className="IS__feat-ico"><span>{f.ico}</span></div>
                <h3>{f.t}</h3>
                <p>{f.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════════ TRUST ════════ */}
      <section ref={refs.trust} className={`IS__trust ${vis.trust ? 'IS--vis' : ''}`}>
        <div className="IS__section-inner">
          <span className="IS__tag">Built Different</span>
          <h2 className="IS__h2">AI You Can Actually Trust</h2>
          <p className="IS__h2-sub">Every recommendation is backed by transparent scoring and real data.</p>
          <div className="IS__trust-grid">
            {[
              { m: '98%', l: 'Amenity Precision', d: 'When we say "has a pool," it has one — cross-validated against sources.', c: '#10b981' },
              { m: '0%', l: 'Hallucination Rate', d: 'Zero fabricated features. Our guard catches any ungrounded claims.', c: '#6366f1' },
              { m: '100%', l: 'Constraint Respect', d: 'Say "under ₹5000" and every single result respects it.', c: '#f59e0b' },
            ].map((t, i) => (
              <div key={i} className="IS__trust-card" style={{ transitionDelay: `${i * 100}ms`, '--tc': t.c }}>
                <span className="IS__trust-m">{t.m}</span>
                <span className="IS__trust-l">{t.l}</span>
                <p>{t.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════════ DESTINATIONS ════════ */}
      <section ref={refs.dest} className={`IS__dest ${vis.dest ? 'IS--vis' : ''}`}>
        <div className="IS__section-inner">
          <span className="IS__tag">Explore</span>
          <h2 className="IS__h2">Popular Destinations</h2>
          <div className="IS__dest-grid">
            {[
              { city: 'Delhi', n: '1,200+ hotels', e: '🏛️' },
              { city: 'Mumbai', n: '980+ hotels', e: '🌊' },
              { city: 'Bangalore', n: '750+ hotels', e: '💻' },
              { city: 'Goa', n: '600+ hotels', e: '🏖️' },
              { city: 'Jaipur', n: '450+ hotels', e: '🏰' },
              { city: 'Manali', n: '320+ hotels', e: '🏔️' },
            ].map((d, i) => (
              <div key={i} className="IS__dest-item" style={{ transitionDelay: `${i * 60}ms` }} onClick={() => navigate('/discover')}>
                <span className="IS__dest-e">{d.e}</span>
                <div><h4>{d.city}</h4><span>{d.n}</span></div>
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="IS__dest-arr"><path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════════ FINAL CTA ════════ */}
      <section ref={refs.cta} className={`IS__final ${vis.cta ? 'IS--vis' : ''}`}>
        <div className="IS__section-inner">
          <div className="IS__final-box">
            <div className="IS__final-glow" />
            <h2>Ready to find your perfect stay?</h2>
            <p>Join thousands of travelers using smarter hotel search.</p>
            <button className="IS__final-btn" onClick={() => navigate('/discover')}>
              Start Your Search
              <svg width="16" height="16" viewBox="0 0 18 18" fill="none"><path d="M3.75 9h10.5M10.5 4.5L15 9l-4.5 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </button>
            <div className="IS__final-pills"><span>🛡️ No signup</span><span>⚡ Instant</span><span>💰 Free</span></div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="IS__footer">
        <div className="IS__section-inner IS__footer-row">
          <div className="IS__footer-brand">
            <div className="IS__logo IS__logo--sm">
              <svg viewBox="0 0 64 64" width="14" height="14" fill="none"><path d="M4 34l24-6 4-16 4 16 24 6-24 6-4 16-4-16z" fill="#fff"/></svg>
            </div>
            <span>IntentStay</span>
          </div>
          <p>© 2026 IntentStay · AI-powered hotel discovery</p>
        </div>
      </footer>
    </div>
  );
}
