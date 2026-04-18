// Mock hotel data for IntentStay
export const hotels = [
  {
    id: 1,
    name: "The Oberoi, New Delhi",
    price: 8500,
    currency: "₹",
    location: "Dr. Zakir Hussain Marg, New Delhi",
    distance: "2.3 km from city center",
    rating: 4.8,
    reviews: 2847,
    matchScore: 96,
    image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
    images: [
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
      "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80",
      "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80"
    ],
    aiExplanation: "This hotel is ideal for your work trip due to reliable high-speed Wi-Fi, dedicated business center, and quiet executive rooms that help you stay productive.",
    aiExplanationLong: "The Oberoi New Delhi stands out as the perfect choice for your business trip. The hotel offers dedicated high-speed fiber-optic internet throughout, ensuring seamless video calls and uploads. Executive rooms on higher floors provide sound-insulated environments, and the 24/7 business center with private meeting rooms means you'll never miss a beat. The concierge team is experienced with corporate guests and can arrange transport, printing, and same-day laundry — everything a business traveler needs.",
    amenities: ["Free High-Speed Wi-Fi", "Business Center", "Spa & Wellness", "Fine Dining", "Airport Shuttle", "Concierge", "Fitness Center", "Room Service 24/7"],
    matchReasons: [
      { label: "Fast Wi-Fi", matched: true },
      { label: "Quiet Rooms", matched: true },
      { label: "Business Center", matched: true },
      { label: "Central Location", matched: true },
      { label: "Budget Friendly", matched: false }
    ],
    highlights: [
      "Award-winning spa with traditional treatments",
      "Rooftop restaurant with panoramic city views",
      "Personal butler service for premium rooms",
      "Sound-insulated executive floor"
    ],
    guestReviews: [
      { name: "Rajesh K.", text: "Exceptional service and the Wi-Fi was blazing fast. Perfect for my 3-day conference trip.", rating: 5 },
      { name: "Sarah M.", text: "The rooms are immaculate and incredibly quiet. Best sleep I've had at any hotel.", rating: 5 },
      { name: "Aman P.", text: "Business center is top-notch. Had all my printing and meeting needs covered.", rating: 4 }
    ],
    guestVerdict: "Business travelers consistently praise the blazing-fast Wi-Fi and sound-insulated executive rooms.",
    wifiQuality: "Excellent",
    quietness: "Excellent",
    comparisonData: { wifi: 95, quietness: 92, service: 96, location: 88, value: 60 }
  },
  {
    id: 2,
    name: "ITC Maurya",
    price: 7200,
    currency: "₹",
    location: "Sardar Patel Marg, New Delhi",
    distance: "4.1 km from city center",
    rating: 4.7,
    reviews: 3201,
    matchScore: 92,
    image: "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80",
    images: [
      "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80",
      "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&q=80",
      "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&q=80"
    ],
    aiExplanation: "A strong match for productivity — the Towers wing offers dedicated workspace desks, complimentary business lounge access, and exceptionally quiet corridors.",
    aiExplanationLong: "ITC Maurya's legendary Towers wing is designed with the modern business traveler in mind. Each room features an ergonomic work desk with international power outlets, high-speed wired and wireless internet, and blackout curtains for undisturbed rest. The exclusive Towers Lounge offers complimentary refreshments, meeting spaces, and a dedicated concierge. The hotel's Bukhara restaurant is world-famous, making client dinners effortless. Located in the diplomatic enclave, the surroundings are serene yet well-connected.",
    amenities: ["Free Wi-Fi", "Towers Business Lounge", "Bukhara Restaurant", "Pool", "Spa", "Airport Transfer", "Laundry", "Meeting Rooms"],
    matchReasons: [
      { label: "Fast Wi-Fi", matched: true },
      { label: "Quiet Rooms", matched: true },
      { label: "Business Lounge", matched: true },
      { label: "Central Location", matched: false },
      { label: "Budget Friendly", matched: true }
    ],
    highlights: [
      "Home to the legendary Bukhara restaurant",
      "Towers Lounge with complimentary refreshments",
      "Ergonomic workspace in every room",
      "Located in peaceful diplomatic enclave"
    ],
    guestReviews: [
      { name: "Priya S.", text: "The Towers wing is absolutely worth it. Felt like having a private office in a luxury hotel.", rating: 5 },
      { name: "David L.", text: "Bukhara alone makes this hotel worth staying at. The food is unforgettable.", rating: 5 },
      { name: "Neha G.", text: "Very comfortable rooms, excellent Wi-Fi. Would recommend for any business traveler.", rating: 4 }
    ],
    guestVerdict: "Corporate guests love the Towers wing workspace and the world-famous Bukhara dining experience.",
    wifiQuality: "Very Good",
    quietness: "Excellent",
    comparisonData: { wifi: 88, quietness: 94, service: 90, location: 72, value: 75 }
  },
  {
    id: 3,
    name: "Lemon Tree Premier",
    price: 3800,
    currency: "₹",
    location: "Aerocity, New Delhi",
    distance: "1.5 km from airport",
    rating: 4.3,
    reviews: 1856,
    matchScore: 88,
    image: "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
    images: [
      "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
      "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80",
      "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&q=80"
    ],
    aiExplanation: "Budget-friendly without compromises — strong Wi-Fi, modern rooms, and right next to the airport for easy commutes. Great value for money.",
    aiExplanationLong: "Lemon Tree Premier Aerocity offers the best value proposition in this list. With modern, well-appointed rooms featuring reliable Wi-Fi and work desks, it covers all business essentials at nearly half the price of luxury alternatives. Its Aerocity location means you're minutes from the airport and connected to the metro for quick city access. The hotel's vibrant atmosphere, rooftop pool, and cheerful service add a refreshing touch to business travel without the corporate stuffiness.",
    amenities: ["Free Wi-Fi", "Rooftop Pool", "Restaurant", "Gym", "Metro Access", "Airport Shuttle", "Meeting Room", "Laundry"],
    matchReasons: [
      { label: "Fast Wi-Fi", matched: true },
      { label: "Quiet Rooms", matched: false },
      { label: "Near Airport", matched: true },
      { label: "Metro Access", matched: true },
      { label: "Budget Friendly", matched: true }
    ],
    highlights: [
      "Excellent value for money",
      "Walking distance to Aerocity metro",
      "Rooftop pool with city views",
      "Modern, cheerful interiors"
    ],
    guestReviews: [
      { name: "Vikram T.", text: "Best value in Delhi. Room was clean, Wi-Fi worked great, and the location is super convenient.", rating: 4 },
      { name: "Lisa W.", text: "Perfect for a short business trip. No frills but everything you need.", rating: 4 },
      { name: "Arjun D.", text: "The rooftop pool was a nice surprise. Good breakfast buffet too.", rating: 4 }
    ],
    guestVerdict: "Budget travelers highlight the unbeatable airport proximity and reliable Wi-Fi at this price point.",
    wifiQuality: "Good",
    quietness: "Average",
    comparisonData: { wifi: 78, quietness: 55, service: 75, location: 85, value: 95 }
  },
  {
    id: 4,
    name: "The Leela Palace",
    price: 12000,
    currency: "₹",
    location: "Chanakyapuri, New Delhi",
    distance: "5.2 km from city center",
    rating: 4.9,
    reviews: 4102,
    matchScore: 85,
    image: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
    images: [
      "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
      "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
      "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&q=80"
    ],
    aiExplanation: "Premium luxury with unmatched service — though over budget, the dedicated butler service and world-class amenities make it worth considering.",
    aiExplanationLong: "The Leela Palace represents the pinnacle of luxury hospitality in Delhi. While it exceeds your stated budget, its inclusion is justified by the extraordinary level of service and facility. Each room comes with a personal butler, the business facilities are world-class, and the attention to detail is unparalleled. If you have important client meetings or need to impress, this is the hotel that sets the standard. The Qube restaurant and Le Cirque offer exceptional dining without stepping outside.",
    amenities: ["Butler Service", "Free Wi-Fi", "Luxury Spa", "Fine Dining", "Pool", "Business Center", "Limousine Service", "Concierge"],
    matchReasons: [
      { label: "Fast Wi-Fi", matched: true },
      { label: "Quiet Rooms", matched: true },
      { label: "Premium Service", matched: true },
      { label: "Central Location", matched: false },
      { label: "Budget Friendly", matched: false }
    ],
    highlights: [
      "Personal butler for every room",
      "Award-winning Le Cirque restaurant",
      "Palatial architecture and interiors",
      "Limousine airport transfer included"
    ],
    guestReviews: [
      { name: "Meera R.", text: "An absolute dream. The butler service is genuine — they remember your preferences from previous stays.", rating: 5 },
      { name: "James B.", text: "Without a doubt the finest hotel I've stayed in across Asia. Worth every penny.", rating: 5 },
      { name: "Ankit M.", text: "The attention to detail is staggering. From the welcome drink to the turndown service.", rating: 5 }
    ],
    guestVerdict: "Luxury seekers unanimously rate the personal butler service and palatial interiors as best-in-class.",
    wifiQuality: "Excellent",
    quietness: "Excellent",
    comparisonData: { wifi: 90, quietness: 96, service: 99, location: 65, value: 45 }
  },
  {
    id: 5,
    name: "Radisson Blu Plaza",
    price: 5500,
    currency: "₹",
    location: "Mahipalpur, New Delhi",
    distance: "3.8 km from airport",
    rating: 4.4,
    reviews: 2103,
    matchScore: 82,
    image: "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80",
    images: [
      "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80",
      "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&q=80",
      "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?w=800&q=80"
    ],
    aiExplanation: "Solid mid-range option balancing comfort with budget — reliable connectivity, comfortable rooms, and well-located near both airport and business districts.",
    aiExplanationLong: "Radisson Blu Plaza offers a balanced proposition for the practical business traveler. The rooms are spacious and well-maintained with consistent Wi-Fi, the breakfast buffet is extensive, and the location provides easy access to both the airport and Gurgaon business district. The hotel's meeting facilities are well-equipped for small to mid-size gatherings, and the staff is attentive without being intrusive. It strikes the right balance between comfort and cost-effectiveness.",
    amenities: ["Free Wi-Fi", "Pool", "Restaurant", "Bar", "Gym", "Meeting Rooms", "Airport Transfer", "Spa"],
    matchReasons: [
      { label: "Fast Wi-Fi", matched: true },
      { label: "Quiet Rooms", matched: true },
      { label: "Near Airport", matched: true },
      { label: "Meeting Rooms", matched: true },
      { label: "Budget Friendly", matched: true }
    ],
    highlights: [
      "Spacious rooms with work desks",
      "Extensive breakfast buffet",
      "Easy access to Gurgaon business district",
      "Well-equipped meeting facilities"
    ],
    guestReviews: [
      { name: "Rohan K.", text: "Reliable and comfortable. Everything works as expected. Good for regular business trips.", rating: 4 },
      { name: "Emily C.", text: "Nice pool area and the gym is well-equipped. Room was clean and spacious.", rating: 4 },
      { name: "Siddharth J.", text: "Good value for a Radisson property. The staff goes above and beyond.", rating: 4 }
    ],
    guestVerdict: "Repeat visitors appreciate the consistent quality, spacious rooms, and excellent value for money.",
    wifiQuality: "Good",
    quietness: "Very Good",
    comparisonData: { wifi: 82, quietness: 80, service: 78, location: 80, value: 88 }
  }
];

// Intent matching logic (simulated AI)
export function matchHotels(query, allHotels = hotels) {
  const q = query.toLowerCase();
  let results = [...allHotels];

  // Simple keyword-based scoring adjustments
  const budgetMatch = q.match(/(?:under|below|less than|budget|cheap)\s*(?:₹|rs\.?|inr)?\s*(\d+)/i);
  const maxBudget = budgetMatch ? parseInt(budgetMatch[1]) : null;

  if (maxBudget) {
    results = results.map(h => ({
      ...h,
      matchScore: h.price <= maxBudget ? Math.min(h.matchScore + 5, 99) : Math.max(h.matchScore - 15, 50)
    }));
  }

  // Boost for keywords
  const keywords = {
    wifi: ["wifi", "wi-fi", "internet", "connectivity"],
    luxury: ["luxury", "premium", "5 star", "five star", "upscale"],
    budget: ["cheap", "budget", "affordable", "value", "economic"],
    work: ["work", "business", "corporate", "office", "productive"],
    family: ["family", "kids", "children", "pool"],
    airport: ["airport", "fly", "flight"],
    central: ["center", "central", "downtown", "city center"],
    quiet: ["quiet", "peaceful", "silent", "calm"]
  };

  results = results.map(hotel => {
    let scoreBoost = 0;
    Object.entries(keywords).forEach(([category, words]) => {
      if (words.some(w => q.includes(w))) {
        const hasAmenity = hotel.matchReasons.some(r => 
          r.matched && r.label.toLowerCase().includes(category)
        );
        if (hasAmenity) scoreBoost += 3;
      }
    });
    return { ...hotel, matchScore: Math.min(hotel.matchScore + scoreBoost, 99) };
  });

  // Sort by match score
  results.sort((a, b) => b.matchScore - a.matchScore);

  // Apply budget filter (move over-budget to end but keep them)
  if (maxBudget) {
    const inBudget = results.filter(h => h.price <= maxBudget);
    const overBudget = results.filter(h => h.price > maxBudget);
    results = [...inBudget, ...overBudget];
  }

  return results.slice(0, 5);
}

// Compute how confident the AI is in understanding the query
export function getConfidenceScore(query) {
  const q = query.toLowerCase();
  let score = 50; // base
  let detectedIntents = [];

  // Location signals
  if (/delhi|mumbai|bangalore|chennai|kolkata|goa|jaipur|hyderabad/i.test(q)) {
    score += 15;
    detectedIntents.push("location");
  }

  // Budget signals
  if (/under|below|less than|budget|cheap|₹|rs|affordable|\d{3,}/i.test(q)) {
    score += 12;
    detectedIntents.push("budget");
  }

  // Purpose signals
  if (/work|business|family|vacation|honeymoon|wedding|conference|meeting|trip/i.test(q)) {
    score += 12;
    detectedIntents.push("purpose");
  }

  // Amenity signals
  if (/wifi|wi-fi|pool|gym|spa|restaurant|parking|breakfast/i.test(q)) {
    score += 8;
    detectedIntents.push("amenity");
  }

  // Quality signals
  if (/quiet|luxury|premium|clean|modern|comfortable|safe/i.test(q)) {
    score += 8;
    detectedIntents.push("quality");
  }

  // Word count bonus (longer queries = more context)
  const wordCount = q.split(/\s+/).length;
  if (wordCount >= 5) score += 5;
  if (wordCount >= 8) score += 5;

  score = Math.min(score, 98);

  let level, label, message;
  if (score >= 80) {
    level = "high";
    label = "Strong understanding";
    message = null;
  } else if (score >= 55) {
    level = "medium";
    label = "Partial understanding";
    message = "Try adding more details like location, budget, or trip purpose for better results.";
  } else {
    level = "low";
    label = "Limited understanding";
    message = "I might be missing something — could you be more specific about your destination or requirements?";
  }

  return { score, level, label, message, detectedIntents };
}

// Generate refinement chip suggestions based on query
export function getRefinementChips(query) {
  const q = query.toLowerCase();
  const chips = [];

  if (!q.includes('pool')) chips.push({ label: "Add pool", icon: "🏊" });
  if (!q.match(/under|below|less|budget|cheap/)) chips.push({ label: "Reduce budget 20%", icon: "💰" });
  if (!q.match(/center|central|downtown/)) chips.push({ label: "Closer to city center", icon: "📍" });
  if (!q.match(/quiet|peaceful/)) chips.push({ label: "Prefer quiet rooms", icon: "🤫" });
  if (!q.match(/breakfast/)) chips.push({ label: "Include breakfast", icon: "🍳" });
  if (!q.match(/wifi|wi-fi/)) chips.push({ label: "Need fast Wi-Fi", icon: "📶" });

  return chips.slice(0, 4);
}

// Generate comparison data for two hotels
export function compareHotels(hotel1, hotel2) {
  const categories = [
    { key: "wifi", label: "Wi-Fi Quality", icon: "📶" },
    { key: "quietness", label: "Quietness", icon: "🤫" },
    { key: "service", label: "Service Quality", icon: "⭐" },
    { key: "location", label: "Location Score", icon: "📍" },
    { key: "value", label: "Value for Money", icon: "💰" }
  ];

  return categories.map(cat => {
    const v1 = hotel1.comparisonData[cat.key];
    const v2 = hotel2.comparisonData[cat.key];
    let winner = null;
    if (v1 > v2 + 5) winner = 1;
    else if (v2 > v1 + 5) winner = 2;
    return { ...cat, value1: v1, value2: v2, winner };
  });
}
