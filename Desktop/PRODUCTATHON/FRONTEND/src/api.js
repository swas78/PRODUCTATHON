const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const SESSION_ID = 'session_' + Math.random().toString(36).slice(2);

export async function discover(message) {
  const res = await fetch(`${BASE_URL}/api/discover`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    },
    body: JSON.stringify({ message, session_id: SESSION_ID }),
  });
  if (!res.ok) throw new Error(`Discover failed: ${res.status}`);
  return res.json();
  // Returns: { response, hotels, intent, confidence }
}

export async function refine(message) {
  const res = await fetch(`${BASE_URL}/api/refine`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    },
    body: JSON.stringify({ message, session_id: SESSION_ID }),
  });
  if (!res.ok) throw new Error(`Refine failed: ${res.status}`);
  return res.json();
  // Returns: { response, hotels, intent, confidence }
}

export async function compare(hotelIdA, hotelIdB) {
  const res = await fetch(`${BASE_URL}/api/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    },
    body: JSON.stringify({ hotel_ids: [hotelIdA, hotelIdB], session_id: SESSION_ID }),
  });
  if (!res.ok) throw new Error(`Compare failed: ${res.status}`);
  return res.json();
  // Returns: { comparison }
}

export async function explain(hotelId) {
  const res = await fetch(
    `${BASE_URL}/api/explain/${hotelId}?session_id=${SESSION_ID}`,
    {
      headers: { 'ngrok-skip-browser-warning': 'true' },
    }
  );
  if (!res.ok) throw new Error(`Explain failed: ${res.status}`);
  return res.json();
  // Returns: { hotel_name, composite_score, components[] }
}