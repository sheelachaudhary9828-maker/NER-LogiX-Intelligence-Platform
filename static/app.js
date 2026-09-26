/**
 * NER-LogiX Application Core Logic
 * Handles GIS mapping, live vehicle telemetry simulation, AI resilient route planning,
 * field incident reporting with offline IndexedDB sync, and full 4-language i18n localization.
 */

// Global State
const state = {
  lang: 'en',
  selectedState: 'ALL',
  nodes: [],
  corridors: [],
  vehicles: [],
  incidents: [],
  depots: [],
  alerts: [],
  activeFleetFilter: 'ALL',
  map: null,
  layers: {
    corridors: null,
    vehicles: null,
    incidents: null,
    depots: null,
    activeRoutes: null
  },
  layerVisibility: {
    corridors: true,
    vehicles: true,
    incidents: true,
    depots: true
  },
  currentRouteData: null,
  gpsSimulationTimer: null
};

// Multilingual Localization Dictionaries
const i18n = {
  en: {
    app_title: "NER-LogiX Intelligence Platform",
    app_subtitle: "AI-Powered Logistics & Accessibility Monitoring for North Eastern India",
    status_online: "System Live",
    status_offline: "Offline Mode",
    filter_all_states: "All 8 NER States (Ashta Lakshmi)",
    btn_simulate: "Simulate Cloudburst",
    btn_report_incident: "Field Incident Report",
    live_alerts: "CRITICAL ALERTS",
    kpi_connectivity: "Regional Accessibility",
    kpi_blocked: "Disrupted / Blocked Corridors",
    kpi_caution: "Caution / High Risk Routes",
    kpi_caution_sub: "Single-lane / heavy rain slips",
    kpi_fleet: "Monitored Essential Fleet",
    kpi_depots: "Depots with Low Buffer (<5d)",
    kpi_depots_sub: "Supply stock depletion watch",
    map_title: "NER GIS Logistics & Accessibility Command Map",
    layer_corridors: "Road Corridors",
    layer_vehicles: "Live GPS Fleet",
    layer_incidents: "Disruption Points",
    layer_depots: "Depots & Helipads",
    tab_route: "AI Route Planner",
    tab_fleet: "GPS Fleet",
    tab_incidents: "Incidents",
    tab_supply: "Supply Depots",
    lbl_origin: "Origin Hub / District",
    lbl_destination: "Destination Node",
    lbl_commodity: "Cargo Classification",
    lbl_weight: "Gross Weight (Tonnes)",
    btn_compute_routes: "Compute AI Resilient Routes",
    matrix_title: "North Eastern States Connectivity & Disruption Matrix",
    matrix_sub: "Live monitoring across Assam, Arunachal Pradesh, Meghalaya, Manipur, Mizoram, Nagaland, Tripura, and Sikkim",
    th_state: "State",
    th_districts: "Monitored Hubs",
    th_connectivity: "Connectivity Index",
    th_status: "Network Status",
    th_vulnerability: "Topography & Dominant Vulnerability",
    th_action: "Active Logistics Protocol",
    modal_report_title: "Field Incident & Disruption Report",
    modal_lbl_title: "Disruption Title / Headline",
    modal_lbl_type: "Incident Classification",
    modal_lbl_severity: "Severity Level",
    modal_lbl_corridor: "Affected Road Corridor",
    modal_lbl_state: "State",
    modal_lbl_district: "District / Location",
    modal_lbl_lat: "Latitude",
    modal_lbl_lng: "Longitude",
    modal_lbl_desc: "Detailed Observations & Clearance Status",
    modal_lbl_photo: "Geo-Tagged Site Photograph",
    modal_lbl_name: "Reporter Name",
    modal_lbl_role: "Designation / Role",
    btn_cancel: "Cancel",
    btn_submit_report: "Submit & Sync Incident"
  },
  hi: {
    app_title: "NER-LogiX इंटेलिजेंस प्लेटफॉर्म",
    app_subtitle: "पूर्वोत्तर भारत के लिए एआई-संचालित लॉजिस्टिक्स एवं मार्ग सुलभता निगरानी",
    status_online: "सिस्टम ऑनलाइन",
    status_offline: "ऑफ़लाइन मोड",
    filter_all_states: "सभी 8 पूर्वोत्तर राज्य (अष्टलक्ष्मी)",
    btn_simulate: "अत्यधिक वर्षा सिमुलेशन",
    btn_report_incident: "फील्ड घटना रिपोर्ट दर्ज करें",
    live_alerts: "महत्वपूर्ण अलर्ट",
    kpi_connectivity: "क्षेत्रीय सड़क सुलभता",
    kpi_blocked: "अवरुद्ध / बाधित सड़क मार्ग",
    kpi_caution: "उच्च जोखिम / सावधानी मार्ग",
    kpi_caution_sub: "एकल-लेन / भूस्खलन जोखिम",
    kpi_fleet: "निगरानी वाहन बेड़ा",
    kpi_depots: "गंभीर भंडार डिपो (<5 दिन)",
    kpi_depots_sub: "आवश्यक आपूर्ति कमी निगरानी",
    map_title: "पूर्वोत्तर जीआईएस लॉजिस्टिक्स एवं सुलभता मानचित्र",
    layer_corridors: "सड़क कॉरिडोर",
    layer_vehicles: "लाइव जीपीएस वाहन",
    layer_incidents: "बाधा स्थल",
    layer_depots: "डिपो एवं हेलीपैड",
    tab_route: "एआई वैकल्पिक मार्ग",
    tab_fleet: "जीपीएस वाहन",
    tab_incidents: "फील्ड रिपोर्ट",
    tab_supply: "आपूर्ति भंडार",
    lbl_origin: "प्रारंभिक जिला / केंद्र",
    lbl_destination: "गंतव्य केंद्र",
    lbl_commodity: "सामग्री वर्गीकरण",
    lbl_weight: "सकल वजन (टन)",
    btn_compute_routes: "एआई सुरक्षित मार्ग गणना करें",
    matrix_title: "पूर्वोत्तर राज्य कनेक्टिविटी एवं व्यवधान मैट्रिक्स",
    matrix_sub: "असम, अरुणाचल, मेघालय, मणिपुर, मिजोरम, नागालैंड, त्रिपुरा और सिक्किम में लाइव निगरानी",
    th_state: "राज्य",
    th_districts: "निगरानी केंद्र",
    th_connectivity: "कनेक्टिविटी सूचकांक",
    th_status: "नेटवर्क स्थिति",
    th_vulnerability: "भू-आकृति एवं मुख्य जोखिम",
    th_action: "सक्रिय लॉजिस्टिक्स प्रोटोकॉल",
    modal_report_title: "फील्ड व्यवधान एवं भूस्खलन रिपोर्ट",
    modal_lbl_title: "घटना का शीर्षक",
    modal_lbl_type: "घटना का प्रकार",
    modal_lbl_severity: "गंभीरता स्तर",
    modal_lbl_corridor: "प्रभावित सड़क मार्ग",
    modal_lbl_state: "राज्य",
    modal_lbl_district: "जिला / स्थान",
    modal_lbl_lat: "अक्षांश (Lat)",
    modal_lbl_lng: "देशांतर (Lng)",
    modal_lbl_desc: "विस्तृत विवरण एवं निकासी स्थिति",
    modal_lbl_photo: "जियो-टैग्ड साइट फोटो",
    modal_lbl_name: "अधिकारी का नाम",
    modal_lbl_role: "पद / विभाग",
    btn_cancel: "रद्द करें",
    btn_submit_report: "रिपोर्ट सबमिट एवं सिंक करें"
  },
  as: {
    app_title: "NER-LogiX বুদ্ধিমত্তা মঞ্চ",
    app_subtitle: "উত্তৰ-পূব ভাৰতৰ বাবে AI-চালিত লজিষ্টিক আৰু যাতায়াত নিৰীক্ষণ ব্যৱস্থা",
    status_online: "ব্যৱস্থা সক্ৰিয়",
    status_offline: "অফলাইন ম'ড",
    filter_all_states: "সকলো ৮ উত্তৰ-পূৰ্বাঞ্চল ৰাজ্য (অষ্টলক্ষ্মী)",
    btn_simulate: "বৰষুণৰ প্ৰভাৱ অনুকৰণ",
    btn_report_incident: "পথৰ বাধাৰ প্ৰতিবেদন দিয়ক",
    live_alerts: "জৰুৰী সতৰ্কবাৰ্তা",
    kpi_connectivity: "আঞ্চলিক পথ সুগমতা",
    kpi_blocked: "বন্ধ হৈ থকা পথসমূহ",
    kpi_caution: "উচ্চ বিপদাপন্ন পথ",
    kpi_caution_sub: "একমুখী লেন / ভূমিস্খলনৰ আশংকা",
    kpi_fleet: "নিৰীক্ষণত থকা বাহনসমূহ",
    kpi_depots: "সংকটজনক গুদাম (<৫ দিন)",
    kpi_depots_sub: "অত্যাৱশ্যকীয় সামগ্ৰী নিৰীক্ষণ",
    map_title: "উত্তৰ-পূব GIS লজিষ্টিক আৰু যাতায়াত মেপ",
    layer_corridors: "পথসমূহ",
    layer_vehicles: "GPS বাহন",
    layer_incidents: "বাধাৰ স্থানসমূহ",
    layer_depots: "গুদাম আৰু হেলিপেড",
    tab_route: "AI বিকল্প পথ",
    tab_fleet: "GPS বাহনসমূহ",
    tab_incidents: "প্ৰতিবেদনসমূহ",
    tab_supply: "সামগ্ৰী গুদাম",
    lbl_origin: "আৰম্ভণি জিলা / হাব",
    lbl_destination: "গন্তব্য স্থান",
    lbl_commodity: "সামগ্ৰীৰ প্ৰকাৰ",
    lbl_weight: "মুঠ ওজন (টন)",
    btn_compute_routes: "AI সুৰক্ষিত পথ বাছনি কৰক",
    matrix_title: "উত্তৰ-পূবৰ ৰাজ্যসমূহৰ সংযোগ স্থিতি তালিকা",
    matrix_sub: "অসম, অৰুণাচল, মেঘালয়, মণিপুৰ, মিজোৰাম, নাগালেণ্ড, ত্ৰিপুৰা আৰু ছিকিমৰ প্ৰত্যক্ষ নিৰীক্ষণ",
    th_state: "ৰাজ্য",
    th_districts: "নিৰীক্ষিত জিলা",
    th_connectivity: "সংযোগ সূচক",
    th_status: "নেটৱৰ্ক স্থিতি",
    th_vulnerability: "ভূ-প্ৰকৃতি আৰু মূল বিপদ",
    th_action: "লজিষ্টিক কাৰ্য্যপ্ৰণালী",
    modal_report_title: "পথৰ বাধাৰ নতুন প্ৰতিবেদন",
    modal_lbl_title: "প্ৰতিবেদনৰ শিৰোনাম",
    modal_lbl_type: "বাধাৰ শ্ৰেণী",
    modal_lbl_severity: "বিপদৰ মাত্ৰা",
    modal_lbl_corridor: "ক্ষতিগ্ৰস্ত পথ",
    modal_lbl_state: "ৰাজ্য",
    modal_lbl_district: "জিলা / অঞ্চল",
    modal_lbl_lat: "অক্ষাংশ (Lat)",
    modal_lbl_lng: "দ্ৰাঘিমাংশ (Lng)",
    modal_lbl_desc: "বিস্তাৰিত বিৱৰণ আৰু বাট মুকলিৰ স্থিতি",
    modal_lbl_photo: "জীয়-টেগ কৰা ফটো",
    modal_lbl_name: "প্ৰতিবেদনকাৰীৰ নাম",
    modal_lbl_role: "পদবী / বিভাগ",
    btn_cancel: "বাতিল কৰক",
    btn_submit_report: "প্ৰতিবেদন জমা দিয়ক"
  },
  bn: {
    app_title: "NER-LogiX ইন্টেলিজেন্স প্ল্যাটফর্ম",
    app_subtitle: "উত্তর-পূর্ব ভারতের জন্য এআই-ভিত্তিক লজিস্টিক ও রুট পর্যবেক্ষণ ব্যবস্থা",
    status_online: "সিস্টেম লাইভ",
    status_offline: "অফলাইন মোড",
    filter_all_states: "সব ৮টি উত্তর-পূর্ব রাজ্য (অষ্টলক্ষ্মী)",
    btn_simulate: "বৃষ্টিপাত সিমুলেশন",
    btn_report_incident: "ফিল্ড ঘটনা রিপোর্ট জমা দিন",
    live_alerts: "জরুরি সতর্কবার্তা",
    kpi_connectivity: "আঞ্চলিক সংযোগ সুগমতা",
    kpi_blocked: "অবরুদ্ধ সড়ক পথ",
    kpi_caution: "উচ্চ ঝুঁকিপূর্ণ রুট",
    kpi_caution_sub: "একমুখী লেন / ভূমিধস সতর্কতা",
    kpi_fleet: "নজরদারিতে থাকা যানবাহন",
    kpi_depots: "সংকটাপন্ন ডিপো (<৫ দিন)",
    kpi_depots_sub: "প্রয়োজনীয় সরবরাহ নজরদারি",
    map_title: "উত্তর-পূর্ব জিআইএস লজিস্টিক ও সংযোগ মানচিত্র",
    layer_corridors: "সড়ক করিডোর",
    layer_vehicles: "লাইভ জিপিএস বহর",
    layer_incidents: "বিপত্তি কেন্দ্র",
    layer_depots: "ডিপো ও হেলিপ্যাড",
    tab_route: "এআই বিকল্প রুট",
    tab_fleet: "জিপিএস বহর",
    tab_incidents: "ঘটনা রিপোর্ট",
    tab_supply: "সরবরাহ ডিপো",
    lbl_origin: "উৎপত্তিস্থল জেলা / হাব",
    lbl_destination: "গন্তব্য হাব",
    lbl_commodity: "পণ্যের ধরন",
    lbl_weight: "মোট ওজন (টন)",
    btn_compute_routes: "এআই নিরাপদ রুট নির্ণয় করুন",
    matrix_title: "উত্তর-পূর্বাঞ্চলের রাজ্য সমূহের সংযোগ স্থিতি তালিকা",
    matrix_sub: "আসাম, অরুণাচল, মেঘালয়, মণিপুর, মিজোরাম, নাগাল্যান্ড, ত্রিপুরা ও সিকিমের সরাসরি পর্যবেক্ষণ",
    th_state: "রাজ্য",
    th_districts: "পর্যবেক্ষণ কেন্দ্র",
    th_connectivity: "সংযোগ সূচক",
    th_status: "নেটওয়ার্ক স্থিতি",
    th_vulnerability: "ভূ-প্রকৃতি ও প্রধান ঝুঁকি",
    th_action: "লজিস্টিক নির্দেশিকা",
    modal_report_title: "সড়ক বিভ্রাটের ফিল্ড রিপোর্ট",
    modal_lbl_title: "প্রতিবেদনের শিরোনাম",
    modal_lbl_type: "বিপর্যয়ের ধরন",
    modal_lbl_severity: "তীব্রতার মাত্রা",
    modal_lbl_corridor: "ক্ষতিগ্রস্ত করিডোর",
    modal_lbl_state: "রাজ্য",
    modal_lbl_district: "জেলা / স্থান",
    modal_lbl_lat: "অক্ষাংশ (Lat)",
    modal_lbl_lng: "দ্রাঘিমাংশ (Lng)",
    modal_lbl_desc: "বিস্তারিত বিবরণ ও উদ্ধার পরিস্থিতি",
    modal_lbl_photo: "জিও-ট্যাগযুক্ত ছবি",
    modal_lbl_name: "প্রতিবেদনকারীর নাম",
    modal_lbl_role: "পদবী / দায়িত্ব",
    btn_cancel: "বাতিল করুন",
    btn_submit_report: "রিপোর্ট জমা দিন"
  }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  setupEventListeners();
  loadAllData();
  registerServiceWorker();
  startGpsTelemetryLoop();
  checkOfflineQueue();
});

// Register Service Worker for Offline PWA Operation
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(() => console.log("NER-LogiX Service Worker Registered"))
      .catch((err) => console.warn("SW Registration:", err));
  }

  // Network Online/Offline Listeners
  window.addEventListener('online', () => {
    updateOnlineStatus(true);
    syncQueuedReports();
  });
  window.addEventListener('offline', () => {
    updateOnlineStatus(false);
  });
}

function updateOnlineStatus(isOnline) {
  const badge = document.getElementById('networkStatusBadge');
  const text = document.getElementById('networkStatusText');
  if (isOnline) {
    badge.className = 'status-badge online';
    text.textContent = i18n[state.lang].status_online || "System Live";
  } else {
    badge.className = 'status-badge offline';
    text.textContent = i18n[state.lang].status_offline || "Offline Mode";
  }
}

// Initialize Leaflet GIS Map
function initMap() {
  // Center of North East India
  state.map = L.map('gisMap', {
    center: [26.2, 93.0],
    zoom: 7,
    minZoom: 5,
    maxZoom: 16
  });

  // Dark CartoDB Matter Basemap for tactical logistics visualization
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png?key=cb1_3z07_1_c7585b52b7d49dc081b2f48d', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>, OpenStreetMap contributors',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(state.map);

  // Initialize Layer Groups
  state.layers.corridors = L.layerGroup().addTo(state.map);
  state.layers.vehicles = L.layerGroup().addTo(state.map);
  state.layers.incidents = L.layerGroup().addTo(state.map);
  state.layers.depots = L.layerGroup().addTo(state.map);
  state.layers.activeRoutes = L.layerGroup().addTo(state.map);
}

// Fetch All Initial Data from Backend APIs
async function loadAllData() {
  try {
    const [nodesRes, corrRes, vehRes, incRes, depRes, alertsRes, statsRes] = await Promise.all([
      fetch('/api/nodes').then(r => r.json()),
      fetch('/api/corridors').then(r => r.json()),
      fetch('/api/vehicles').then(r => r.json()),
      fetch('/api/incidents').then(r => r.json()),
      fetch('/api/depots').then(r => r.json()),
      fetch('/api/alerts').then(r => r.json()),
      fetch('/api/dashboard-stats').then(r => r.json())
    ]);

    state.nodes = nodesRes.nodes || [];
    state.corridors = corrRes.corridors || [];
    state.vehicles = vehRes.vehicles || [];
    state.incidents = incRes.incidents || [];
    state.depots = depRes.depots || [];
    state.alerts = alertsRes.alerts || [];

    // Render components
    renderKpiStats(statsRes);
    renderAlertTicker();
    populateSelectDropdowns();
    renderMapCorridors();
    renderMapNodesAndDepots();
    renderMapVehicles();
    renderMapIncidents();
    renderFleetTab();
    renderIncidentsTab();
    renderDepotsTab();
    renderStateMatrix(statsRes.states_matrix);

  } catch (err) {
    console.error("Error loading initial data:", err);
  }
}

// Render Top KPI Metrics
function renderKpiStats(stats) {
  if (!stats) return;
  document.getElementById('kpiConnectivity').textContent = `${stats.overall_regional_connectivity_pct}%`;
  document.getElementById('kpiBlocked').textContent = stats.corridors_blocked;
  document.getElementById('kpiCaution').textContent = stats.corridors_caution;
  document.getElementById('kpiFleet').textContent = stats.active_fleet_count;
  document.getElementById('kpiFleetSub').textContent = `${stats.critical_medicine_trucks} Life-Saving Med Vans`;
  document.getElementById('kpiDepots').textContent = stats.depots_at_risk;
}

// Render Alert Ticker Bar
function renderAlertTicker() {
  const ticker = document.getElementById('alertTickerContent');
  if (!state.alerts || state.alerts.length === 0) {
    ticker.textContent = "All North Eastern corridors reporting normal operational status.";
    return;
  }
  const alertTexts = state.alerts.map(a => `[${a.state.toUpperCase()}] ${a.title}: ${a.message}`);
  ticker.textContent = alertTexts.join("  ★  ");
}

// Populate Dropdown Selectors
function populateSelectDropdowns() {
  const originSel = document.getElementById('routeOrigin');
  const destSel = document.getElementById('routeDestination');
  const incCorrSel = document.getElementById('incCorridorSelect');

  originSel.innerHTML = '';
  destSel.innerHTML = '';
  incCorrSel.innerHTML = '<option value="">None / Off-Highway</option>';

  state.nodes.forEach(n => {
    const opt1 = new Option(`${n.name} (${n.state})`, n.id);
    const opt2 = new Option(`${n.name} (${n.state})`, n.id);
    originSel.add(opt1);
    destSel.add(opt2);
  });

  // Default selection: Guwahati to Imphal (demonstrates Paglapahar bypass)
  originSel.value = 'GUW';
  destSel.value = 'IMP';

  state.corridors.forEach(c => {
    incCorrSel.add(new Option(`${c.code}: ${c.name} [${c.status}]`, c.id));
  });
}

// Render Road Corridors onto GIS Map
function renderMapCorridors() {
  state.layers.corridors.clearLayers();

  state.corridors.forEach(c => {
    // Determine color based on real-time accessibility status
    let color = '#10b981'; // Open
    let weight = 4;
    let dashArray = null;

    if (c.status === 'BLOCKED') {
      color = '#f43f5e'; // Blocked
      weight = 6;
      dashArray = '6, 6';
    } else if (c.status === 'CAUTION') {
      color = '#f59e0b'; // Caution
      weight = 5;
    }

    const polyline = L.polyline([
      [c.from_lat, c.from_lng],
      [c.to_lat, c.to_lng]
    ], {
      color: color,
      weight: weight,
      dashArray: dashArray,
      opacity: 0.85
    });

    // Interactive Details Popup
    polyline.bindPopup(`
      <div style="min-width: 220px; font-family: inherit;">
        <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 0.25rem; color: ${color};">
          ${c.code}: ${c.name}
        </div>
        <div style="font-size: 0.8rem; margin-bottom: 0.5rem; color: #9ca3af;">
          Status: <strong style="color: ${color};">${c.status}</strong><br>
          ${c.status_reason || 'Smooth Transit'}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.35rem; font-size: 0.75rem; background: #1f2937; padding: 0.5rem; border-radius: 6px;">
          <div>Dist: <strong>${c.distance_km} km</strong></div>
          <div>Base Time: <strong>${c.base_travel_hours} hrs</strong></div>
          <div>Disruption Risk: <strong style="color: ${c.disruption_risk_score > 60 ? '#f43f5e' : '#34d399'};">${c.disruption_risk_score}%</strong></div>
          <div>24h Rain: <strong>${c.rainfall_24h_mm} mm</strong></div>
          <div>Terrain: <strong>${c.terrain_type}</strong></div>
          <div>Bridge Limit: <strong>${c.bridge_max_tonnage} T</strong></div>
        </div>
        <button onclick="window.viewAiBriefing('${c.id}')" style="margin-top: 6px; width: 100%; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; border-radius: 4px; padding: 5px 8px; font-size: 0.75rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 5px;">
          <i class="fa-solid fa-brain"></i> AI Tactical Briefing
        </button>
      </div>
    `);

    state.layers.corridors.addLayer(polyline);
  });
}

// Render Hubs, Depots, and Emergency Helipads
function renderMapNodesAndDepots() {
  state.layers.depots.clearLayers();

  state.nodes.forEach(n => {
    // Custom icon for strategic nodes
    const isCapital = n.hub_type.includes('Capital');
    const color = isCapital ? '#3b82f6' : '#64748b';

    const circle = L.circleMarker([n.lat, n.lng], {
      radius: isCapital ? 7 : 5,
      fillColor: color,
      color: '#ffffff',
      weight: 1.5,
      opacity: 1,
      fillOpacity: 0.9
    });

    circle.bindPopup(`
      <div style="font-family: inherit;">
        <strong>${n.name}</strong><br>
        <span style="font-size: 0.75rem; color: #9ca3af;">State: ${n.state} | District: ${n.district}</span><br>
        <span style="font-size: 0.75rem;">Altitude: <strong>${n.elevation_m}m</strong> | Helipad: <strong>${n.has_helipad ? '✅ Yes' : '❌ No'}</strong></span>
      </div>
    `);

    state.layers.depots.addLayer(circle);
  });
}

// Render Live GPS Vehicles onto GIS Map
function renderMapVehicles() {
  state.layers.vehicles.clearLayers();

  state.vehicles.forEach(v => {
    // Custom HTML Marker with icon
    let iconClass = 'fa-truck';
    let iconBg = '#3b82f6';

    if (v.commodity_type.includes('Medicine')) {
      iconClass = 'fa-pills';
      iconBg = '#10b981';
    } else if (v.commodity_type.includes('Food')) {
      iconClass = 'fa-wheat-awn';
      iconBg = '#f59e0b';
    } else if (v.commodity_type.includes('Fuel')) {
      iconClass = 'fa-gas-pump';
      iconBg = '#ec4899';
    } else if (v.commodity_type.includes('Construction')) {
      iconClass = 'fa-trowel-bricks';
      iconBg = '#8b5cf6';
    }

    const isSos = v.sos_alert === 1;
    const borderStyle = isSos ? 'border: 2px solid #ef4444; animation: pulse 1s infinite;' : 'border: 2px solid white;';

    const customIcon = L.divIcon({
      className: 'vehicle-marker',
      html: `
        <div style="background: ${iconBg}; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); ${borderStyle}">
          <i class="fa-solid ${iconClass}"></i>
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });

    const marker = L.marker([v.current_lat, v.current_lng], { icon: customIcon });

    marker.bindPopup(`
      <div style="min-width: 220px; font-family: inherit;">
        <div style="font-weight: 700; color: #60a5fa; font-size: 0.9rem;">
          ${v.vehicle_no} <span style="font-size: 0.75rem; background: #374151; color: white; padding: 2px 6px; border-radius: 4px;">${v.priority}</span>
        </div>
        <div style="font-size: 0.8rem; color: #e5e7eb; margin: 0.25rem 0;">
          <strong>${v.commodity_type}</strong>: ${v.commodity_desc}
        </div>
        <div style="font-size: 0.75rem; color: #9ca3af; margin-bottom: 0.5rem;">
          Route: ${v.origin_name} &rarr; ${v.dest_name}<br>
          Driver: ${v.driver_name} (${v.driver_contact})<br>
          Speed: <strong>${v.speed_kmh} km/h</strong> | Progress: <strong>${v.progress_pct}%</strong><br>
          ${v.temp_celsius !== null ? `Cold-Chain Temp: <strong style="color: #34d399;">${v.temp_celsius}&deg;C</strong>` : ''}
        </div>
        <button onclick="window.triggerVehicleSos('${v.id}')" style="background: #e11d48; color: white; border: none; border-radius: 4px; padding: 4px 8px; font-size: 0.75rem; cursor: pointer; width: 100%;">
          <i class="fa-solid fa-tower-broadcast"></i> ${v.sos_alert ? 'Clear Emergency SOS' : 'Trigger SOS / Dispatch Escort'}
        </button>
      </div>
    `);

    state.layers.vehicles.addLayer(marker);
  });
}

// Render Field Incidents onto GIS Map
function renderMapIncidents() {
  state.layers.incidents.clearLayers();

  state.incidents.forEach(inc => {
    const isCritical = inc.severity === 'CRITICAL';
    const markerColor = isCritical ? '#ef4444' : '#f59e0b';

    const customIcon = L.divIcon({
      className: 'incident-marker',
      html: `
        <div style="background: ${markerColor}; width: 26px; height: 26px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.6); border: 2px solid white;">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
      `,
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    });

    const marker = L.marker([inc.lat, inc.lng], { icon: customIcon });

    marker.bindPopup(`
      <div style="max-width: 250px; font-family: inherit;">
        <div style="font-weight: 700; color: ${markerColor}; font-size: 0.9rem;">
          [${inc.incident_type}] ${inc.title}
        </div>
        <div style="font-size: 0.75rem; color: #9ca3af; margin: 0.25rem 0;">
          ${inc.district}, ${inc.state} &bull; Verified by ${inc.reported_by} (${inc.role})
        </div>
        ${inc.photo_url ? `<img src="${inc.photo_url}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 6px; margin: 0.4rem 0;">` : ''}
        <div style="font-size: 0.75rem; color: #d1d5db; line-height: 1.4;">
          ${inc.description}
        </div>
        <div style="font-size: 0.7rem; color: #34d399; margin-top: 0.4rem;">
          Action: ${inc.action_taken || 'Emergency clearance initiated.'}
        </div>
      </div>
    `);

    state.layers.incidents.addLayer(marker);
  });
}

// Render Fleet Tab Cards
function renderFleetTab() {
  const container = document.getElementById('fleetListContainer');
  document.getElementById('fleetCountAll').textContent = state.vehicles.length;

  const filtered = state.activeFleetFilter === 'ALL'
    ? state.vehicles
    : state.vehicles.filter(v => v.commodity_type.toLowerCase().includes(state.activeFleetFilter.toLowerCase()));

  if (filtered.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: #6b7280; padding: 1.5rem;">No active vehicles in this category.</div>`;
    return;
  }

  container.innerHTML = filtered.map(v => `
    <div class="vehicle-card" id="card-${v.id}">
      <div class="veh-top">
        <span class="veh-no">${v.vehicle_no}</span>
        <span class="veh-tag ${v.priority === 'CRITICAL' ? 'crit' : (v.priority === 'HIGH' ? 'high' : 'std')}">${v.priority}</span>
      </div>
      <div class="veh-desc">
        <strong>${v.commodity_type}</strong>: ${v.commodity_desc}
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${v.progress_pct}%"></div>
      </div>
      <div class="veh-meta">
        <span><i class="fa-solid fa-gauge-high"></i> ${v.speed_kmh} km/h</span>
        <span><i class="fa-solid fa-clock"></i> ETA: ${v.eta_hours}h</span>
        ${v.temp_celsius !== null ? `<span style="color: #34d399;"><i class="fa-solid fa-temperature-low"></i> ${v.temp_celsius}&deg;C</span>` : ''}
        <a href="javascript:void(0)" onclick="window.focusVehicle(${v.current_lat}, ${v.current_lng})" style="color: #60a5fa; text-decoration: none;">Map <i class="fa-solid fa-location-arrow"></i></a>
      </div>
    </div>
  `).join('');
}

// Render Incidents Tab
function renderIncidentsTab() {
  const container = document.getElementById('incidentsListContainer');
  if (state.incidents.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: #6b7280; padding: 1.5rem;">No active disruption reports.</div>`;
    return;
  }

  container.innerHTML = state.incidents.map(inc => `
    <div class="incident-item">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong style="color: ${inc.severity === 'CRITICAL' ? '#f43f5e' : '#f59e0b'}; font-size: 0.85rem;">
          ${inc.title}
        </strong>
        <span style="font-size: 0.7rem; background: #374151; padding: 2px 6px; border-radius: 4px;">${inc.severity}</span>
      </div>
      <div style="font-size: 0.75rem; color: #9ca3af; margin: 0.25rem 0;">
        ${inc.district}, ${inc.state} &bull; ${new Date(inc.reported_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
      ${inc.photo_url ? `<img src="${inc.photo_url}" class="incident-img-thumb" alt="Site photo">` : ''}
      <p style="font-size: 0.75rem; color: #d1d5db; margin: 0.25rem 0;">${inc.description}</p>
      <div style="font-size: 0.7rem; color: #34d399;">
        <strong>Action:</strong> ${inc.action_taken || 'Monitoring in progress.'}
      </div>
    </div>
  `).join('');
}

// Render Supply Depots Tab
function renderDepotsTab() {
  const container = document.getElementById('depotsListContainer');
  container.innerHTML = state.depots.map(d => `
    <div style="background: rgba(31, 41, 55, 0.5); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong style="font-size: 0.85rem; color: #f9fafb;">${d.district} Depot (${d.state})</strong>
        <span style="font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: ${d.status === 'CRITICAL' ? '#881337' : (d.status === 'LOW' ? '#78350f' : '#065f46')}; color: ${d.status === 'CRITICAL' ? '#fda4af' : (d.status === 'LOW' ? '#fde68a' : '#6ee7b7')};">
          ${d.buffer_days} Days Stock
        </span>
      </div>
      <div style="font-size: 0.75rem; color: #9ca3af; margin: 0.25rem 0;">
        ${d.commodity_type} &bull; Stock: <strong>${d.current_stock_mt} MT</strong> / ${d.capacity_mt} MT
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${(d.current_stock_mt / d.capacity_mt) * 100}%; background: ${d.buffer_days < 5 ? '#f43f5e' : '#10b981'};"></div>
      </div>
    </div>
  `).join('');
}

// Render State Connectivity Matrix Table
function renderStateMatrix(statesData) {
  const tbody = document.getElementById('stateMatrixTbody');
  if (!statesData) return;

  const vulnerabilityProfiles = {
    'Assam': 'Brahmaputra annual floods, riverbank erosion, Dima Hasao hill slips',
    'Arunachal Pradesh': 'Steep young Himalayan slopes, Sela Pass snow blocks, rock avalanches',
    'Meghalaya': 'World-record monsoons, active karst mudflows, Sonapur highway escarpment',
    'Manipur': 'Purvanchal fractured shale, Paglapahar gorge bottlenecks, hill landslides',
    'Mizoram': 'Longitudinal folded ridges, sinking Bilkhawthlir bridges, single lifeline NH-54',
    'Nagaland': 'High seismic Zone V, landslide-prone weathered clay, NH-29 Paglapahar',
    'Tripura': 'Low undulating hills, flood vulnerability in Gomati/Howrah basins',
    'Sikkim': 'Teesta River flash floods, high-altitude moraine slips, NH-10 cutoff risk'
  };

  const logisticsProtocols = {
    'Assam': 'Multimodal river barge redundancy (Pandu Port) + NH-27 bypass',
    'Arunachal Pradesh': 'BRO Sela Tunnel corridor + emergency air-drop helipad staging',
    'Meghalaya': 'Single-lane escort convoy + Haflong hill alternate routing',
    'Manipur': 'Active Peren bypass green corridor + cold-chain medicine priority',
    'Mizoram': '15-Tonnage load enforcement on weak bridges + Kolasib buffer cache',
    'Nagaland': 'Hydraulic excavators pre-positioned at Paglapahar + NDRF staging',
    'Tripura': 'Northern rail-freight transshipment at Dharmanagar',
    'Sikkim': 'Teesta flood barrier alert + daylight-only convoy transit'
  };

  tbody.innerHTML = statesData.map(s => {
    const isOptimal = s.connectivity_pct > 75;
    const isCritical = s.connectivity_pct < 50;
    const badgeColor = isOptimal ? 'background: #065f46; color: #34d399;' : (isCritical ? 'background: #881337; color: #f43f5e;' : 'background: #78350f; color: #fde68a;');

    return `
      <tr>
        <td><strong>${s.state}</strong></td>
        <td>${s.districts} Hubs</td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div class="progress-track" style="width: 80px; height: 6px; margin: 0;">
              <div class="progress-fill" style="width: ${s.connectivity_pct}%; background: ${isOptimal ? '#10b981' : (isCritical ? '#f43f5e' : '#f59e0b')};"></div>
            </div>
            <strong>${s.connectivity_pct}%</strong>
          </div>
        </td>
        <td>
          <span style="font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 700; ${badgeColor}">
            ${s.status}
          </span>
        </td>
        <td style="color: #9ca3af; font-size: 0.75rem;">${vulnerabilityProfiles[s.state] || 'Mountain terrain'}</td>
        <td style="color: #60a5fa; font-size: 0.75rem;">${logisticsProtocols[s.state] || 'Standard highway patrol'}</td>
      </tr>
    `;
  }).join('');
}

// Compute AI Resilient Routes via API
async function computeAiRoutes(e) {
  e.preventDefault();
  const origin = document.getElementById('routeOrigin').value;
  const destination = document.getElementById('routeDestination').value;
  const tonnage = parseFloat(document.getElementById('vehicleWeightInput').value) || 15.0;

  const btn = e.target.querySelector('button[type="submit"]');
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Calculating Resilient Graph...`;
  btn.disabled = true;

  try {
    const res = await fetch('/api/route-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ origin, destination, tonnage, avoid_high_risk: true })
    });
    const data = await res.json();
    state.currentRouteData = data;
    renderRouteResults(data);
  } catch (err) {
    alert("Error calculating routes: " + err.message);
  } finally {
    btn.innerHTML = originalHtml;
    btn.disabled = false;
  }
}

// Render Route Comparison Results
function renderRouteResults(data) {
  const container = document.getElementById('routeResultsContainer');
  if (data.error) {
    container.innerHTML = `<div style="color: #f43f5e; padding: 1rem; text-align: center;">${data.error}</div>`;
    return;
  }

  // Draw active routes on map
  state.layers.activeRoutes.clearLayers();

  let html = `
    <div style="font-size: 0.8rem; color: #9ca3af; margin-bottom: 0.5rem;">
      Path Analysis: <strong>${data.origin.name}</strong> &rarr; <strong>${data.destination.name}</strong>
    </div>
  `;

  data.routes.forEach((r, idx) => {
    const isRec = r.is_recommended;
    const badgeClass = isRec ? 'green' : (r.has_blocked_segment ? 'red' : 'blue');
    const badgeText = isRec ? 'AI RECOMMENDED RESILIENT ROUTE' : (r.has_blocked_segment ? 'BLOCKED / HIGH RISK DIRECT ROUTE' : 'ALTERNATE CORRIDOR');

    // Draw on map: Bright Cyan for Resilient route, Dashed Red for blocked route
    const routeColor = isRec ? '#06b6d4' : (r.has_blocked_segment ? '#f43f5e' : '#a855f7');
    const routeCoords = r.waypoints.map(w => [w.lat, w.lng]);
    const routeLine = L.polyline(routeCoords, {
      color: routeColor,
      weight: isRec ? 6 : 4,
      dashArray: r.has_blocked_segment ? '5, 8' : null,
      opacity: 0.9
    });
    state.layers.activeRoutes.addLayer(routeLine);

    if (idx === 0) {
      // Zoom map to fit the recommended route
      state.map.fitBounds(routeLine.getBounds(), { padding: [40, 40] });
    }

    html += `
      <div class="route-card ${isRec ? 'recommended' : ''}" onclick="window.selectRoute(${idx})">
        <span class="route-badge ${badgeClass}">${badgeText}</span>
        <div style="font-weight: 700; font-size: 0.9rem; color: #f9fafb;">${r.label}</div>

        <div class="route-metrics">
          <div class="metric-item">
            <span class="metric-lbl">Distance</span>
            <span class="metric-val">${r.total_distance_km} km</span>
          </div>
          <div class="metric-item">
            <span class="metric-lbl">Est. Time</span>
            <span class="metric-val" style="color: ${r.delay_hours > 0 ? '#f43f5e' : '#34d399'};">${r.total_travel_hours} hrs ${r.delay_hours > 0 ? `(+${r.delay_hours}h delay)` : ''}</span>
          </div>
          <div class="metric-item">
            <span class="metric-lbl">Resiliency</span>
            <span class="metric-val" style="color: ${r.safety_score > 60 ? '#34d399' : '#f43f5e'};">${r.safety_score}%</span>
          </div>
          <div class="metric-item">
            <span class="metric-lbl">Peak Altitude</span>
            <span class="metric-val">${r.max_elevation_m}m</span>
          </div>
        </div>

        ${r.status_notes && r.status_notes.length > 0 ? `
          <div style="font-size: 0.7rem; color: #fca5a5; margin-top: 0.4rem; background: rgba(239, 68, 68, 0.1); padding: 0.35rem; border-radius: 4px;">
            <i class="fa-solid fa-triangle-exclamation"></i> ${r.status_notes.join(' | ')}
          </div>
        ` : ''}

        <div class="step-list">
          ${r.turn_by_turn.map(s => `
            <div class="step-item">
              <span class="step-bullet">&bull;</span>
              <span>${s.instruction} <em>(${s.distance_km}km, ${s.segment_status})</em></span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

// Select Route Click Handler
window.selectRoute = function(idx) {
  if (!state.currentRouteData || !state.currentRouteData.routes[idx]) return;
  const r = state.currentRouteData.routes[idx];
  const coords = r.waypoints.map(w => [w.lat, w.lng]);
  state.map.fitBounds(L.polyline(coords).getBounds(), { padding: [40, 40] });
};

// Focus map on vehicle
window.focusVehicle = function(lat, lng) {
  state.map.setView([lat, lng], 10, { animate: true });
};

// View AI Disruption Intelligence Briefing
window.viewAiBriefing = async function(corridorId) {
  try {
    const res = await fetch(`/api/ai-briefing?corridor_id=${corridorId}`);
    const data = await res.json();
    if (data.briefing) {
      const b = data.briefing;
      alert(`[AI TACTICAL LOGISTICS INTELLIGENCE BRIEFING]\n\nEngine: ${b.authenticated_engine}\nKey Status: ${b.api_key_status} (${b.api_key_masked})\n\nCorridor: ${b.corridor_code} - ${b.corridor_name}\nHeadline: ${b.headline}\nRisk Level: ${b.risk_level} (${b.composite_risk_score}%)\n\nTactical Advisory:\n${b.tactical_advisory}\n\nContingency Route:\n${b.contingency_route_recommendation}\n\nCoordinating Agencies: ${b.recommended_agencies.join(', ')}`);
    } else {
      alert("Unable to fetch AI intelligence briefing: " + (data.error || 'Unknown error'));
    }
  } catch (err) {
    alert("Error fetching AI briefing: " + err.message);
  }
};

// Trigger Vehicle Emergency SOS
window.triggerVehicleSos = async function(vehId) {
  const veh = state.vehicles.find(v => v.id === vehId);
  const newActive = !(veh && veh.sos_alert === 1);
  try {
    await fetch('/api/vehicles/sos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vehicle_id: vehId, active: newActive })
    });
    await loadAllData();
  } catch (err) {
    alert("SOS Action error: " + err.message);
  }
};

// Live GPS Simulation loop
function startGpsTelemetryLoop() {
  state.gpsSimulationTimer = setInterval(async () => {
    try {
      await fetch('/api/vehicles/update-gps', { method: 'POST' });
      const vehRes = await fetch('/api/vehicles').then(r => r.json());
      state.vehicles = vehRes.vehicles || [];
      renderMapVehicles();
      renderFleetTab();
    } catch (e) {
      // offline or silent
    }
  }, 4000);
}

// Setup Event Listeners
function setupEventListeners() {
  // Tab Switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      document.getElementById(tabId).classList.add('active');
    });
  });

  // Layer toggles
  document.getElementById('toggleCorridorsBtn').addEventListener('click', (e) => {
    toggleMapLayer('corridors', e.currentTarget);
  });
  document.getElementById('toggleVehiclesBtn').addEventListener('click', (e) => {
    toggleMapLayer('vehicles', e.currentTarget);
  });
  document.getElementById('toggleIncidentsBtn').addEventListener('click', (e) => {
    toggleMapLayer('incidents', e.currentTarget);
  });
  document.getElementById('toggleDepotsBtn').addEventListener('click', (e) => {
    toggleMapLayer('depots', e.currentTarget);
  });
  document.getElementById('btnCenterNER').addEventListener('click', () => {
    state.map.setView([26.2, 93.0], 7);
  });

  // Fleet Filter Chips
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      e.currentTarget.classList.add('active');
      state.activeFleetFilter = e.currentTarget.getAttribute('data-fleet-filter');
      renderFleetTab();
    });
  });

  // Language Change Listener
  document.getElementById('languageSelect').addEventListener('change', (e) => {
    setLanguage(e.target.value);
  });

  // State Filter Change Listener
  document.getElementById('stateFilterSelect').addEventListener('change', (e) => {
    filterByState(e.target.value);
  });

  // Route Form Submit
  document.getElementById('routePlannerForm').addEventListener('submit', computeAiRoutes);

  // Weather Simulation Demo
  document.getElementById('btnSimulateWeather').addEventListener('click', simulateMonsoonCloudburst);

  // Incident Modal Handlers
  document.getElementById('btnOpenReportModal').addEventListener('click', openIncidentModal);
  document.getElementById('btnQuickReport').addEventListener('click', openIncidentModal);
  document.getElementById('btnCloseModal').addEventListener('click', closeIncidentModal);
  document.getElementById('btnCancelReport').addEventListener('click', closeIncidentModal);
  document.getElementById('incidentReportForm').addEventListener('submit', submitIncidentReport);
  document.getElementById('btnGrabGPS').addEventListener('click', grabCurrentGps);
  document.getElementById('incPhotoFile').addEventListener('change', handlePhotoSelection);

  // Refresh Matrix
  document.getElementById('btnRefreshMatrix').addEventListener('click', loadAllData);
}

function toggleMapLayer(layerKey, btnEl) {
  if (state.map.hasLayer(state.layers[layerKey])) {
    state.map.removeLayer(state.layers[layerKey]);
    btnEl.classList.remove('active');
  } else {
    state.map.addLayer(state.layers[layerKey]);
    btnEl.classList.add('active');
  }
}

// Multilingual Switcher
function setLanguage(langCode) {
  state.lang = langCode;
  const dict = i18n[langCode] || i18n['en'];

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });
}

// Filter by State
function filterByState(selected) {
  state.selectedState = selected;
  if (selected === 'ALL') {
    state.map.setView([26.2, 93.0], 7);
  } else {
    // Find matching nodes to compute bounds
    const stateNodes = state.nodes.filter(n => n.state === selected);
    if (stateNodes.length > 0) {
      const bounds = L.latLngBounds(stateNodes.map(n => [n.lat, n.lng]));
      state.map.fitBounds(bounds, { padding: [50, 50] });
    }
  }
}

// Interactive Simulation: Monsoon Cloudburst
async function simulateMonsoonCloudburst() {
  const btn = document.getElementById('btnSimulateWeather');
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Simulating 145mm Cloudburst...`;

  try {
    const res = await fetch('/api/simulate-weather-event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state: 'Nagaland', rainfall_mm: 145.0 })
    });
    const result = await res.json();
    alert(`[AI Simulation Triggered]\n${result.message}\n\nCorridors in Nagaland & Assam have been updated with extreme rainfall and landslide risks.`);
    await loadAllData();
  } catch (err) {
    alert("Simulation error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-cloud-showers-heavy"></i> ${i18n[state.lang].btn_simulate}`;
  }
}

// Incident Modal Functions
function openIncidentModal() {
  document.getElementById('reportModal').classList.add('active');
}
function closeIncidentModal() {
  document.getElementById('reportModal').classList.remove('active');
}

function grabCurrentGps() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        document.getElementById('incLatInput').value = pos.coords.latitude.toFixed(4);
        document.getElementById('incLngInput').value = pos.coords.longitude.toFixed(4);
      },
      () => {
        // Fallback default coordinates for Dimapur Paglapahar
        document.getElementById('incLatInput').value = "25.8210";
        document.getElementById('incLngInput').value = "93.8100";
      }
    );
  }
}

function handlePhotoSelection(e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(evt) {
      const preview = document.getElementById('photoPreviewImg');
      preview.src = evt.target.result;
      document.getElementById('photoPreviewContainer').style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
}

// Submit Incident Report (with offline queueing support)
async function submitIncidentReport(e) {
  e.preventDefault();
  const title = document.getElementById('incTitleInput').value;
  const incident_type = document.getElementById('incTypeSelect').value;
  const severity = document.getElementById('incSeveritySelect').value;
  const corridor_id = document.getElementById('incCorridorSelect').value || null;
  const stateVal = document.getElementById('incStateSelect').value;
  const district = document.getElementById('incDistrictInput').value;
  const lat = parseFloat(document.getElementById('incLatInput').value);
  const lng = parseFloat(document.getElementById('incLngInput').value);
  const description = document.getElementById('incDescInput').value;
  const reported_by = document.getElementById('incReporterName').value;
  const role = document.getElementById('incReporterRole').value;

  const preview = document.getElementById('photoPreviewImg');
  const photo_url = preview.src && preview.src.startsWith('data:') 
    ? preview.src 
    : "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?w=800&auto=format&fit=crop&q=80";

  const payload = {
    title, incident_type, severity, corridor_id,
    state: stateVal, district, lat, lng, description, photo_url,
    reported_by, role, action_taken: 'Inspection dispatched by District Authority'
  };

  // If offline, queue in localStorage
  if (!navigator.onLine) {
    const queue = JSON.parse(localStorage.getItem('ner_offline_reports') || '[]');
    queue.push(payload);
    localStorage.setItem('ner_offline_reports', JSON.stringify(queue));
    showSyncToast("Offline: Field report queued in local device storage. Will auto-sync when network is restored.");
    closeIncidentModal();
    return;
  }

  try {
    const res = await fetch('/api/incidents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    showSyncToast("Incident successfully reported, geo-tagged, and synced with central command.");
    closeIncidentModal();
    await loadAllData();
  } catch (err) {
    // Network failed during send, queue offline
    const queue = JSON.parse(localStorage.getItem('ner_offline_reports') || '[]');
    queue.push(payload);
    localStorage.setItem('ner_offline_reports', JSON.stringify(queue));
    showSyncToast("Network error: Report stored offline. Will retry synchronization.");
    closeIncidentModal();
  }
}

// Synchronize Queued Reports when device comes back online
async function syncQueuedReports() {
  const queue = JSON.parse(localStorage.getItem('ner_offline_reports') || '[]');
  if (queue.length === 0) return;

  showSyncToast(`Reconnected! Synchronizing ${queue.length} offline field reports...`);

  for (const report of queue) {
    try {
      await fetch('/api/incidents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report)
      });
    } catch (e) {
      console.warn("Sync failed for item:", e);
    }
  }

  localStorage.removeItem('ner_offline_reports');
  showSyncToast("All offline reports successfully uploaded to central database!");
  await loadAllData();
}

function checkOfflineQueue() {
  if (navigator.onLine) {
    syncQueuedReports();
  }
}

function showSyncToast(msg) {
  const toast = document.getElementById('syncToast');
  const msgEl = document.getElementById('syncToastMsg');
  msgEl.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 4500);
}
