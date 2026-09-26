"""
NER-LogiX Database Management & Seed Data Provider
Handles SQLite initialization, schema creation, and seeding of North Eastern Region logistics data.
"""

import sqlite3
import json
import os
import math
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'ner_logistics.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Nodes table (Districts, Hubs, Border Points)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        elevation_m INTEGER NOT NULL,
        hub_type TEXT NOT NULL,
        has_helipad INTEGER DEFAULT 0,
        critical_depot INTEGER DEFAULT 0
    )
    ''')

    # 2. Corridors table (Road links between nodes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS corridors (
        id TEXT PRIMARY KEY,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        from_node TEXT NOT NULL,
        to_node TEXT NOT NULL,
        distance_km REAL NOT NULL,
        base_travel_hours REAL NOT NULL,
        terrain_type TEXT NOT NULL,
        road_class TEXT NOT NULL,
        status TEXT NOT NULL,
        status_reason TEXT,
        slope_angle_deg REAL DEFAULT 15.0,
        soil_type TEXT DEFAULT 'Clayey Loam / Shale',
        landslide_hazard_zone TEXT DEFAULT 'High',
        flood_susceptibility TEXT DEFAULT 'Low',
        rainfall_24h_mm REAL DEFAULT 0.0,
        disruption_risk_score REAL DEFAULT 20.0,
        bridge_max_tonnage REAL DEFAULT 40.0,
        FOREIGN KEY(from_node) REFERENCES nodes(id),
        FOREIGN KEY(to_node) REFERENCES nodes(id)
    )
    ''')

    # 3. Vehicles table (Real-time GPS Tracking Fleet)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id TEXT PRIMARY KEY,
        vehicle_no TEXT NOT NULL,
        commodity_type TEXT NOT NULL,
        commodity_desc TEXT NOT NULL,
        origin_id TEXT NOT NULL,
        dest_id TEXT NOT NULL,
        current_lat REAL NOT NULL,
        current_lng REAL NOT NULL,
        speed_kmh REAL NOT NULL,
        heading_deg REAL NOT NULL,
        progress_pct REAL NOT NULL,
        temp_celsius REAL,
        cargo_weight_tonnes REAL NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        driver_name TEXT NOT NULL,
        driver_contact TEXT NOT NULL,
        eta_hours REAL NOT NULL,
        sos_alert INTEGER DEFAULT 0,
        last_updated TEXT NOT NULL
    )
    ''')

    # 4. Incidents & Field Reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        corridor_id TEXT,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        description TEXT NOT NULL,
        photo_url TEXT,
        reported_by TEXT NOT NULL,
        role TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        action_taken TEXT,
        reported_at TEXT NOT NULL
    )
    ''')

    # 5. Supply Depots & District Warehouses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS supply_depots (
        id TEXT PRIMARY KEY,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        commodity_type TEXT NOT NULL,
        capacity_mt REAL NOT NULL,
        current_stock_mt REAL NOT NULL,
        daily_burn_rate_mt REAL NOT NULL,
        buffer_days REAL NOT NULL,
        status TEXT NOT NULL,
        last_refreshed TEXT NOT NULL
    )
    ''')

    # 6. Real-time Alerts feed
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        severity TEXT NOT NULL,
        category TEXT NOT NULL,
        corridor_id TEXT,
        state TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )
    ''')

    conn.commit()
    conn.close()

def seed_data_if_empty():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM nodes")
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        return

    # Seed Nodes (North Eastern States key hubs & districts)
    nodes_data = [
        # Assam
        ("GUW", "Guwahati Logistics Gateway", "Assam", "Kamrup Metropolitan", 26.1445, 91.7362, 55, "Primary Logistics Hub", 1, 1),
        ("SIL", "Silchar Transit Depot", "Assam", "Cachar", 24.8333, 92.7789, 25, "Barak Valley Hub", 1, 1),
        ("HAF", "Haflong Hill Station", "Assam", "Dima Hasao", 25.1764, 93.0238, 680, "Mountain Transit Post", 0, 0),
        ("TEZ", "Tezpur Depot", "Assam", "Sonitpur", 26.6528, 92.7926, 48, "Strategic Brahmaputra Node", 1, 1),
        ("DIB", "Dibrugarh Supply Terminal", "Assam", "Dibrugarh", 27.4728, 94.9120, 108, "Upper Assam Central Hub", 1, 1),
        ("JOR", "Jorhat Air & Rail Depot", "Assam", "Jorhat", 26.7509, 94.2037, 116, "Central Assam Hub", 1, 1),
        ("BON", "Bongaigaon Transshipment Hub", "Assam", "Bongaigaon", 26.5020, 90.5532, 62, "Western Corridor Entry", 0, 1),
        
        # Meghalaya
        ("SHL", "Shillong Capital Depots", "Meghalaya", "East Khasi Hills", 25.5788, 91.8933, 1525, "State Capital Hub", 1, 1),
        ("JOW", "Jowai Transit Node", "Meghalaya", "West Jaintia Hills", 25.4526, 92.2034, 1380, "Highland Corridor Node", 0, 0),
        ("CHER", "Cherrapunji (Sohra) Outpost", "Meghalaya", "East Khasi Hills", 25.2702, 91.7323, 1430, "Extreme Rainfall Zone", 1, 0),
        ("TUR", "Tura Garo Hills Depot", "Meghalaya", "West Garo Hills", 25.5144, 90.2023, 349, "Western Meghalaya Hub", 1, 0),
        
        # Arunachal Pradesh
        ("ITA", "Itanagar Distribution Center", "Arunachal Pradesh", "Papum Pare", 27.0844, 93.6053, 320, "State Capital Hub", 1, 1),
        ("BOM", "Bomdila Pass Station", "Arunachal Pradesh", "West Kameng", 27.2644, 92.4178, 2415, "High Mountain Station", 1, 0),
        ("TAW", "Tawang Strategic Outpost", "Arunachal Pradesh", "Tawang", 27.5861, 91.8677, 3048, "Border Strategic Post", 1, 1),
        ("PAS", "Pasighat Siang Depot", "Arunachal Pradesh", "East Siang", 28.0664, 95.3268, 155, "River Valley Hub", 1, 0),
        ("ZIR", "Ziro Valley Station", "Arunachal Pradesh", "Lower Subansiri", 27.5950, 93.8315, 1572, "Remote Mountain Valley", 0, 0),
        
        # Nagaland
        ("DIM", "Dimapur Logistics Junction", "Nagaland", "Dimapur", 25.9090, 93.7271, 145, "Nagaland Railhead & Hub", 1, 1),
        ("KOH", "Kohima Hill Capital", "Nagaland", "Kohima", 25.6751, 94.1086, 1444, "State Capital Hub", 1, 1),
        ("MOK", "Mokokchung Central Depot", "Nagaland", "Mokokchung", 26.3255, 94.5160, 1325, "Central Hills Node", 0, 0),
        
        # Manipur
        ("IMP", "Imphal State Logistics Hub", "Manipur", "Imphal West", 24.8170, 93.9368, 786, "State Capital Hub", 1, 1),
        ("SEN", "Senapati Mountain Pass", "Manipur", "Senapati", 25.2676, 94.0188, 1100, "High Vulnerability Corridor", 0, 0),
        ("CHU", "Churachandpur Southern Depot", "Manipur", "Churachandpur", 24.3333, 93.6833, 914, "South Manipur Hub", 1, 0),
        ("MOR", "Moreh International Border Post", "Manipur", "Tengnoupal", 24.2500, 94.3000, 228, "Border Trade Terminal", 0, 1),
        
        # Mizoram
        ("AIZ", "Aizawl Capital Logistics Hub", "Mizoram", "Aizawl", 23.7271, 92.7176, 1132, "State Capital Hub", 1, 1),
        ("KOL", "Kolasib Transit Point", "Mizoram", "Kolasib", 24.2256, 92.6784, 600, "Northern Entry Gateway", 0, 0),
        ("LUN", "Lunglei Southern Hub", "Mizoram", "Lunglei", 22.8878, 92.7351, 1222, "Remote Southern District", 1, 0),
        
        # Tripura
        ("AGA", "Agartala Central Logistics Terminal", "Tripura", "West Tripura", 23.8315, 91.2868, 16, "State Capital Hub", 1, 1),
        ("DHA", "Dharmanagar Northern Rail Depot", "Tripura", "North Tripura", 24.3756, 92.1644, 21, "Rail Transshipment Hub", 0, 1),
        ("UDA", "Udaipur Southern Depot", "Tripura", "Gomati", 23.5333, 91.4833, 24, "South Tripura Node", 0, 0),
        
        # Sikkim
        ("GAN", "Gangtok Mountain Hub", "Sikkim", "East Sikkim", 27.3389, 88.6065, 1650, "State Capital Hub", 1, 1),
        ("MAN", "Mangan High-Altitude Depot", "Sikkim", "North Sikkim", 27.5094, 88.5303, 1310, "High Landslide Vulnerability", 1, 0),
        ("SILG", "Siliguri Gateway Corridors", "West Bengal", "Siliguri", 26.7271, 88.3953, 122, "Chicken's Neck Gateway", 1, 1)
    ]

    cursor.executemany('''
    INSERT INTO nodes (id, name, state, district, lat, lng, elevation_m, hub_type, has_helipad, critical_depot)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', nodes_data)

    # Seed Road Corridors
    corridors_data = [
        # (id, code, name, from, to, km, hrs, terrain, road_class, status, reason, slope, soil, hazard, flood, rain_24h, risk_score, max_tonnage)
        ("CORR-01", "NH-27-W", "Siliguri to Bongaigaon (East-West Highway)", "SILG", "BON", 160.0, 3.5, "Plains / Dooars", "National Highway (4-Lane)", "OPEN", "Normal Flow", 3.0, "Alluvial", "Low", "Moderate", 14.2, 18.0, 50.0),
        ("CORR-02", "NH-27-C", "Bongaigaon to Guwahati Express Link", "BON", "GUW", 175.0, 3.8, "Plains / Brahmaputra Valley", "National Highway (4-Lane)", "OPEN", "Smooth Traffic", 2.0, "Alluvial", "Low", "Low", 8.0, 12.0, 50.0),
        ("CORR-03", "NH-6-N", "Guwahati to Shillong Expressway", "GUW", "SHL", 98.0, 2.5, "Rugged Hills / Plateaus", "National Highway (4-Lane)", "OPEN", "Foggy in patches, road clear", 18.0, "Shale / Metamorphic", "Medium", "Low", 38.5, 34.0, 40.0),
        ("CORR-04", "NH-6-S", "Shillong to Jowai Ridge Highway", "SHL", "JOW", 64.0, 2.0, "Steep Hills / Mining Belts", "National Highway (2-Lane)", "OPEN", "Normal Movement", 22.0, "Sandstone / Clay", "High", "Low", 55.0, 42.0, 35.0),
        ("CORR-05", "NH-6-SE", "Jowai to Silchar via Sonapur Tunnel", "JOW", "SIL", 132.0, 5.5, "High-Risk Mountain Escarpment", "National Highway (2-Lane)", "CAUTION", "Heavy mudflow near Sonapur Tunnel; single-lane convoy active", 38.0, "Unconsolidated Shale", "Critical", "High", 112.4, 78.5, 25.0),
        ("CORR-06", "NH-27-E", "Guwahati to Tezpur Corridor", "GUW", "TEZ", 178.0, 4.0, "Riverine Plain / Foothills", "National Highway (2-Lane)", "OPEN", "Normal Flow", 4.0, "Alluvial", "Low", "Moderate", 18.0, 22.0, 45.0),
        ("CORR-07", "NH-15", "Tezpur to Itanagar Capital Link", "TEZ", "ITA", 155.0, 4.2, "Sub-Himalayan Foothills", "National Highway (2-Lane)", "OPEN", "Pothole maintenance near border", 12.0, "Sedimentary Gravel", "Medium", "Moderate", 42.0, 38.0, 35.0),
        ("CORR-08", "BCT-01", "Tezpur to Bomdila Border Road", "TEZ", "BOM", 152.0, 5.0, "Steep Alpine Ascent", "BRO Border Highway", "OPEN", "Clear but high slope caution", 32.0, "Hard Granite & Gneiss", "High", "Low", 28.0, 45.0, 30.0),
        ("CORR-09", "BCT-02", "Bomdila to Tawang (via Sela Tunnel)", "BOM", "TAW", 175.0, 6.5, "Extreme Alpine / Sela Pass", "BRO Strategic Highway", "CAUTION", "Snow slush & freezing drizzle at 13,000ft", 42.0, "Glacial Till / Scree", "Critical", "Low", 65.0, 68.0, 20.0),
        ("CORR-10", "NH-29-N", "Guwahati to Dimapur Link (via Nagaon)", "GUW", "DIM", 270.0, 6.0, "Valley to Foothills", "National Highway (4-Lane/2-Lane)", "OPEN", "Normal Commercial Traffic", 8.0, "Alluvial / Loam", "Low", "Low", 15.0, 16.0, 45.0),
        ("CORR-11", "NH-29-S", "Dimapur to Kohima Lifeline (Paglapahar)", "DIM", "KOH", 74.0, 3.2, "Steep Fractured Gorge", "National Highway (2-Lane)", "BLOCKED", "Major rockfall & landslide at Paglapahar Km 42. BRO clearing underway.", 44.0, "Weathered Disintegrated Shale", "Critical", "High", 128.0, 94.0, 25.0),
        ("CORR-12", "NH-2-S", "Kohima to Senapati Mountain Link", "KOH", "SEN", 52.0, 2.0, "High Mountain Ridge", "National Highway (2-Lane)", "CAUTION", "Debris accumulation, slow movement", 28.0, "Clayey Sediments", "High", "Low", 70.0, 62.0, 30.0),
        ("CORR-13", "NH-2-M", "Senapati to Imphal Valley Link", "SEN", "IMP", 62.0, 2.0, "Valley Descent", "National Highway (2-Lane)", "OPEN", "Normal Flow", 14.0, "Alluvial Loam", "Medium", "Low", 22.0, 30.0, 40.0),
        ("CORR-14", "NH-102", "Imphal to Moreh Border Highway", "IMP", "MOR", 110.0, 3.5, "Hills & Southern Plain", "National Highway (2-Lane)", "OPEN", "Normal Trade Traffic", 16.0, "Loam / Sandstone", "Medium", "Low", 25.0, 32.0, 35.0),
        ("CORR-15", "NH-54-N", "Silchar to Kolasib Northern Ridge", "SIL", "KOL", 90.0, 3.8, "Steep Bamboo Hills", "National Highway (2-Lane)", "CAUTION", "Sinking zone at Bilkhawthlir, 15T limit", 34.0, "Silt & Weathered Clay", "High", "High", 84.0, 72.0, 15.0),
        ("CORR-16", "NH-54-S", "Kolasib to Aizawl Capital Lifeline", "KOL", "AIZ", 85.0, 3.5, "Narrow Ridge Crests", "National Highway (2-Lane)", "OPEN", "Clear with minor road settlement", 29.0, "Shale & Sandstone", "High", "Low", 46.0, 48.0, 25.0),
        ("CORR-17", "NH-8-T", "Silchar to Dharmanagar Link", "SIL", "DHA", 88.0, 2.8, "Valley / Undulating Low Hills", "National Highway (2-Lane)", "OPEN", "Normal Heavy Vehicle Movement", 10.0, "Alluvial Loam", "Low", "Low", 19.0, 20.0, 40.0),
        ("CORR-18", "NH-8-S", "Dharmanagar to Agartala Express Link", "DHA", "AGA", 175.0, 4.5, "Undulating Plain / Low Hills", "National Highway (2-Lane)", "OPEN", "Operational", 8.0, "Clayey Loam", "Low", "Low", 14.0, 18.0, 45.0),
        ("CORR-19", "NH-10-SK", "Siliguri to Gangtok (Teesta Gorge)", "SILG", "GAN", 114.0, 4.8, "Very Steep River Gorge", "National Highway (2-Lane)", "CAUTION", "Swelling Teesta river erosion at 29th Mile, traffic diverted to single lane", 46.0, "Gneissic Schist / Active Slip", "Critical", "Critical", 145.0, 89.0, 20.0),
        ("CORR-20", "NH-27-ALT", "Haflong Hill Alternate (Guwahati-Silchar bypass)", "GUW", "HAF", 310.0, 8.5, "Dima Hasao Hill Ranges", "State / Inter-district Road", "OPEN", "Operational backup for NH-6 blockages", 26.0, "Metamorphic / Shale", "Medium", "Medium", 35.0, 44.0, 30.0),
        ("CORR-21", "HAF-SIL", "Haflong to Silchar Descent", "HAF", "SIL", 102.0, 3.2, "Barail Range Descent", "National Highway (2-Lane)", "OPEN", "Smooth, essential relief route", 20.0, "Shale / Loam", "Medium", "Low", 30.0, 36.0, 35.0),
        ("CORR-22", "NH-2-ALT", "Dimapur to Imphal via Peren (Kohima Bypass)", "DIM", "IMP", 215.0, 7.5, "Western Hills Alternate", "State Hill Road", "OPEN", "ACTIVE EMERGENCY BYPASS around Paglapahar block", 30.0, "Sedimentary", "High", "Low", 40.0, 52.0, 25.0),
        ("CORR-23", "NH-715", "Tezpur to Jorhat & Dibrugarh Corridor", "TEZ", "DIB", 240.0, 5.0, "Brahmaputra South Bank Plain", "National Highway (4-Lane)", "OPEN", "Unimpeded movement", 3.0, "Alluvial", "Low", "Low", 12.0, 15.0, 50.0)
    ]

    cursor.executemany('''
    INSERT INTO corridors (id, code, name, from_node, to_node, distance_km, base_travel_hours, terrain_type, road_class, status, status_reason, slope_angle_deg, soil_type, landslide_hazard_zone, flood_susceptibility, rainfall_24h_mm, disruption_risk_score, bridge_max_tonnage)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', corridors_data)

    # Seed Real-Time Vehicle Fleet (GPS tracking essential commodities)
    vehicles_data = [
        # Critical Cold-Chain Medicines & Vaccines
        ("VEH-MED-01", "AS-01-GC-4482", "Medicines & Vaccines", "Pediatric Vaccines & Life-saving Insulin (Cold Chain)", "GUW", "IMP", 25.6890, 93.9210, 36.0, 142.0, 68.0, 3.8, 4.5, "CRITICAL", "EN_ROUTE", "Biren Goswami", "+91-98640-12891", 4.2, 0, datetime.now().isoformat()),
        ("VEH-MED-02", "AS-01-KC-8891", "Medicines & Vaccines", "Oncology Drugs & Emergency IV Fluids", "GUW", "SIL", 25.4210, 92.1850, 28.0, 130.0, 52.0, 4.1, 5.2, "CRITICAL", "EN_ROUTE_DELAYED", "Dipankar Barua", "+91-94350-48219", 3.8, 0, datetime.now().isoformat()),
        ("VEH-MED-03", "SK-01-A-1102", "Medicines & Vaccines", "High Altitude Oxygen Concentrators & Trauma Kits", "SILG", "GAN", 27.0512, 88.5120, 22.0, 38.0, 45.0, 2.5, 3.0, "CRITICAL", "SLOW_PROGRESS", "Tenzing Norbu", "+91-97330-89112", 2.9, 0, datetime.now().isoformat()),

        # Food Supplies & PDS Grains
        ("VEH-PDS-01", "NL-07-B-3319", "Food & PDS Supplies", "Rice & Wheat Grains for Remote PDS Depots", "DIM", "KOH", 25.8210, 93.8100, 0.0, 155.0, 35.0, None, 18.0, "HIGH", "HALTED_BY_BLOCKAGE", "Khriesaneilie Angami", "+91-94360-77210", 8.5, 1, datetime.now().isoformat()),
        ("VEH-PDS-02", "MZ-01-D-9012", "Food & PDS Supplies", "FCI Fortified Rice Convoys", "SIL", "AIZ", 24.3210, 92.6840, 31.0, 182.0, 42.0, None, 16.5, "HIGH", "EN_ROUTE", "Lalmuanpuia Ralte", "+91-98620-33411", 4.0, 0, datetime.now().isoformat()),
        ("VEH-PDS-03", "AS-12-BC-6234", "Food & PDS Supplies", "Baby Food & Essential Pulses (Dal)", "GUW", "TAW", 27.2140, 92.4890, 24.0, 315.0, 58.0, None, 12.0, "HIGH", "EN_ROUTE", "Pema Khandu Dorjee", "+91-94362-90184", 5.2, 0, datetime.now().isoformat()),

        # Construction & Infrastructure Materials
        ("VEH-CON-01", "AS-01-EE-7721", "Construction Materials", "Pre-stressed Concrete Girders for Border Bridges", "GUW", "ITA", 26.8520, 93.2010, 42.0, 65.0, 72.0, None, 28.0, "STANDARD", "EN_ROUTE", "Mukesh Sharma", "+91-98540-77291", 2.1, 0, datetime.now().isoformat()),
        ("VEH-CON-02", "TR-01-K-5541", "Construction Materials", "Steel TMT Rebars for Flood Protection Dykes", "DHA", "AGA", 24.1200, 91.8200, 48.0, 210.0, 48.0, None, 24.0, "STANDARD", "EN_ROUTE", "Biplab Debnath", "+91-94361-22901", 2.3, 0, datetime.now().isoformat()),

        # Agricultural Produce & Perishables
        ("VEH-AGR-01", "MN-01-AA-4412", "Agricultural Produce", "Organic King Chilli & Black Rice (Chak-hao) Export", "IMP", "GUW", 25.1200, 93.5500, 38.0, 310.0, 32.0, 14.0, 8.0, "HIGH", "DIVERTED_TO_BYPASS", "Thangminlen Haokip", "+91-96120-44910", 9.1, 0, datetime.now().isoformat()),
        ("VEH-AGR-02", "AS-06-C-9918", "Agricultural Produce", "Fresh Assam CTC Tea Leaves for Processing Hubs", "JOR", "GUW", 26.4210, 92.8910, 52.0, 260.0, 60.0, 18.0, 10.5, "STANDARD", "EN_ROUTE", "Ratan Bora", "+91-98642-11029", 2.8, 0, datetime.now().isoformat()),

        # Fuel & POL Tankers
        ("VEH-POL-01", "AS-01-TT-2024", "Fuel & Petroleum (POL)", "High-Speed Diesel for Border Post Generators", "DIB", "PAS", 27.7810, 95.1200, 44.0, 40.0, 64.0, None, 20.0, "CRITICAL", "EN_ROUTE", "Jitendra Saikia", "+91-94351-88902", 1.8, 0, datetime.now().isoformat()),
        ("VEH-POL-02", "AS-01-TT-3189", "Fuel & Petroleum (POL)", "Aviation Turbine Fuel (ATF) for Emergency Rescue Choppers", "GUW", "SHL", 25.8120, 91.8200, 35.0, 160.0, 80.0, None, 18.0, "CRITICAL", "EN_ROUTE", "Pranab Kalita", "+91-98641-55209", 0.6, 0, datetime.now().isoformat())
    ]

    cursor.executemany('''
    INSERT INTO vehicles (id, vehicle_no, commodity_type, commodity_desc, origin_id, dest_id, current_lat, current_lng, speed_kmh, heading_deg, progress_pct, temp_celsius, cargo_weight_tonnes, priority, status, driver_name, driver_contact, eta_hours, sos_alert, last_updated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', vehicles_data)

    # Seed Verified Incidents & Field Reports
    incidents_data = [
        ("INC-01", "Massive Rockfall & Road Subsidence at Paglapahar", "Landslide", "CRITICAL", "CORR-11", "Dimapur", "Nagaland", 25.8210, 93.8100, "Approximately 600 metric tonnes of boulders slipped onto NH-29 following 128mm continuous rainfall. BRO 15 BRTF deployed with 4 hydraulic excavators. Road impassable for heavy commercial trucks.", "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?w=800&auto=format&fit=crop&q=80", "Maj. R. K. Thapa", "BRO Task Force Commander", "VERIFIED", "Traffic halted. Diverting light convoys via Peren bypass route.", (datetime.now() - timedelta(hours=3)).isoformat()),
        ("INC-02", "Severe Mudflow Accumulation at Sonapur Tunnel Exit", "Mudflow", "HIGH", "CORR-05", "East Jaintia Hills", "Meghalaya", 25.1120, 92.3500, "Continuous downhill slurry and mud washing down over 120m stretch of NH-6. Single lane passage created under guidance of Meghalaya PWD and police.", "https://images.unsplash.com/photo-1547683905-f686c993aae5?w=800&auto=format&fit=crop&q=80", "Sanbor Shullai", "PWD Executive Engineer", "VERIFIED", "One-way alternating convoy system in place. 2-3 hours delay expected.", (datetime.now() - timedelta(hours=5)).isoformat()),
        ("INC-03", "Teesta River Scouring at 29th Mile", "River Inundation", "HIGH", "CORR-19", "Kalimpong / East Sikkim Border", "Sikkim", 27.0210, 88.4890, "Teesta river water level reached danger mark (214.5m). Erosion of toe-wall has made the road narrow. Restricting multi-axle freight carriers.", "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=800&auto=format&fit=crop&q=80", "Tshering Lepcha", "SDRF Officer", "VERIFIED", "Piloting essential medicine vans with emergency beacon.", (datetime.now() - timedelta(hours=8)).isoformat()),
        ("INC-04", "Structural Hairline Cracks on Submersible Bridge", "Bridge Damage", "MEDIUM", "CORR-15", "Kolasib", "Mizoram", 24.2800, 92.6800, "Flash floods weakened abutment wall on Bilkhawthlir bridge. Heavy vehicles >15T prohibited pending reinforcement testing.", "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=800&auto=format&fit=crop&q=80", "Lalbiakvela", "District Transport Officer", "VERIFIED", "Signboards erected, police outpost checking vehicle weighments.", (datetime.now() - timedelta(hours=14)).isoformat())
    ]

    cursor.executemany('''
    INSERT INTO incidents (id, title, incident_type, severity, corridor_id, district, state, lat, lng, description, photo_url, reported_by, role, verification_status, action_taken, reported_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', incidents_data)

    # Seed Supply Depots & District Buffers
    depots_data = [
        ("DEP-IMP-01", "Imphal West", "Manipur", 24.8170, 93.9368, "Food & PDS Grains", 15000.0, 3200.0, 650.0, 4.9, "LOW", datetime.now().isoformat()),
        ("DEP-IMP-02", "Imphal West", "Manipur", 24.8170, 93.9368, "Life-Saving Medicines", 500.0, 95.0, 32.0, 3.0, "CRITICAL", datetime.now().isoformat()),
        ("DEP-KOH-01", "Kohima", "Nagaland", 25.6751, 94.1086, "Food & PDS Grains", 8000.0, 4100.0, 240.0, 17.1, "NORMAL", datetime.now().isoformat()),
        ("DEP-KOH-02", "Kohima", "Nagaland", 25.6751, 94.1086, "POL / Diesel Reserve", 2000.0, 620.0, 110.0, 5.6, "LOW", datetime.now().isoformat()),
        ("DEP-AIZ-01", "Aizawl", "Mizoram", 23.7271, 92.7176, "Food & PDS Grains", 12000.0, 3800.0, 380.0, 10.0, "NORMAL", datetime.now().isoformat()),
        ("DEP-AIZ-02", "Aizawl", "Mizoram", 23.7271, 92.7176, "Life-Saving Medicines", 400.0, 82.0, 18.0, 4.5, "LOW", datetime.now().isoformat()),
        ("DEP-TAW-01", "Tawang", "Arunachal Pradesh", 27.5861, 91.8677, "High-Altitude Winter Reserves", 6000.0, 1400.0, 120.0, 11.6, "NORMAL", datetime.now().isoformat()),
        ("DEP-GAN-01", "East Sikkim", "Sikkim", 27.3389, 88.6065, "PDS Cereals & Flour", 9000.0, 2400.0, 290.0, 8.2, "NORMAL", datetime.now().isoformat()),
        ("DEP-SIL-01", "Cachar", "Assam", 24.8333, 92.7789, "Transit Buffer Warehouse", 25000.0, 18200.0, 950.0, 19.1, "NORMAL", datetime.now().isoformat())
    ]

    cursor.executemany('''
    INSERT INTO supply_depots (id, district, state, lat, lng, commodity_type, capacity_mt, current_stock_mt, daily_burn_rate_mt, buffer_days, status, last_refreshed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', depots_data)

    # Seed Automated Alerts
    alerts_data = [
        ("ALT-01", "EMERGENCY: NH-29 Blocked at Paglapahar", "CRITICAL", "Road Blockage", "CORR-11", "Nagaland", "Massive landslide cutoff between Dimapur & Kohima. Inbound convoys carrying life-saving supplies to Manipur & Nagaland are being diverted via Peren bypass route.", datetime.now().isoformat(), 1),
        ("ALT-02", "FLASH FLOOD & MUDSLIDE ADVISORY: NH-6 Sonapur Tunnel", "WARNING", "Weather Hazard", "CORR-05", "Meghalaya", "Monsoon cloudburst (112mm rain). Single-lane regulated movement with high danger of sudden muck flow. Expected transit delay: 4.5 hours.", datetime.now().isoformat(), 1),
        ("ALT-03", "SUPPLY GAP CRITICAL: Imphal Medicine Buffer below 3.5 Days", "CRITICAL", "Supply Shortage", "CORR-11", "Manipur", "Medicines buffer depot at Imphal has dropped to 3.0 days due to Paglapahar blockage. Green Corridor activation recommended for vehicle VEH-MED-01.", datetime.now().isoformat(), 1),
        ("ALT-04", "HIGH-ALTITUDE FREEZE & SLUSH: Sela Pass (13,700 ft)", "WARNING", "Road Weather", "CORR-09", "Arunachal Pradesh", "Sub-zero temperatures and snow slush. All commercial freight vehicles advised to use snow chains and daylight transit only.", datetime.now().isoformat(), 1)
    ]

    cursor.executemany('''
    INSERT INTO alerts (id, title, severity, category, corridor_id, state, message, created_at, active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', alerts_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Initializing NER-LogiX Database...")
    init_db()
    seed_data_if_empty()
    print("Database initialization and seed complete!")
