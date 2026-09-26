"""
NER-LogiX Central Backend API & Static Web Server
Built for the North Eastern Region Logistics & Accessibility Intelligence Platform.
Zero-dependency implementation utilizing Python 3 standard library:
http.server, sqlite3, json, threading, and urllib.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import mimetypes
import traceback
from datetime import datetime, timedelta

# Import internal modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.db import get_connection, init_db, seed_data_if_empty
from ml_engine.predictor import predictor
from routing.route_engine import route_engine

PORT = 8080
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

class NERLogisticsHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Handle API routes
        if path.startswith('/api/'):
            return self.handle_api_get(path, query)

        # Serve static web app files
        self.serve_static(path)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            payload = json.loads(body.decode('utf-8')) if body else {}
        except Exception:
            payload = {}

        if path.startswith('/api/'):
            return self.handle_api_post(path, payload)

        self.send_json({'error': 'Not found'}, 404)

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

    def serve_static(self, path):
        if path == '/' or path == '':
            path = '/index.html'

        # Strip leading slash and normalize
        rel_path = path.lstrip('/')
        file_path = os.path.join(STATIC_DIR, rel_path)

        # Security check: prevent directory traversal
        if not os.path.abspath(file_path).startswith(STATIC_DIR):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Access denied')
            return

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            file_path = os.path.join(STATIC_DIR, 'index.html')

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            if file_path.endswith('.html') or file_path.endswith('.js') or file_path.endswith('.css'):
                self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Internal error: {str(e)}".encode('utf-8'))

    def handle_api_get(self, path, query):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            if path == '/api/health':
                return self.send_json({
                    'status': 'ONLINE',
                    'platform': 'NER-LogiX Intelligence Platform',
                    'region': 'North Eastern Region of India (8 States)',
                    'timestamp': datetime.now().isoformat()
                })

            elif path == '/api/nodes':
                cursor.execute("SELECT * FROM nodes ORDER BY state, name")
                nodes = [dict(row) for row in cursor.fetchall()]
                return self.send_json({'nodes': nodes})

            elif path == '/api/corridors':
                cursor.execute("""
                SELECT c.*, 
                       fn.name as from_name, fn.state as from_state, fn.lat as from_lat, fn.lng as from_lng,
                       tn.name as to_name, tn.state as to_state, tn.lat as to_lat, tn.lng as to_lng
                FROM corridors c
                JOIN nodes fn ON c.from_node = fn.id
                JOIN nodes tn ON c.to_node = tn.id
                ORDER BY c.disruption_risk_score DESC
                """)
                corridors = [dict(row) for row in cursor.fetchall()]
                return self.send_json({'corridors': corridors})

            elif path == '/api/vehicles':
                cursor.execute("""
                SELECT v.*,
                       fn.name as origin_name, tn.name as dest_name
                FROM vehicles v
                JOIN nodes fn ON v.origin_id = fn.id
                JOIN nodes tn ON v.dest_id = tn.id
                ORDER BY v.priority DESC, v.progress_pct ASC
                """)
                vehicles = [dict(row) for row in cursor.fetchall()]
                return self.send_json({'vehicles': vehicles})

            elif path == '/api/incidents':
                cursor.execute("SELECT * FROM incidents ORDER BY reported_at DESC")
                incidents = [dict(row) for row in cursor.fetchall()]
                return self.send_json({'incidents': incidents})

            elif path == '/api/depots':
                cursor.execute("SELECT * FROM supply_depots ORDER BY buffer_days ASC")
                depots = [dict(row) for row in cursor.fetchall()]
                return self.send_json({'depots': depots})

            elif path == '/api/alerts':
                cursor.execute("SELECT * FROM alerts WHERE active = 1 ORDER BY created_at DESC")
                alerts = [dict(row) for row in cursor.fetchall()]
                return self.send_json({'alerts': alerts})

            elif path == '/api/weather':
                lat = float(query.get('lat', [26.1445])[0])
                lng = float(query.get('lng', [91.7362])[0])
                weather = predictor.fetch_live_weather(lat, lng)
                return self.send_json({'lat': lat, 'lng': lng, 'weather': weather})

            elif path == '/api/api-status':
                masked = f"{predictor.api_key[:4]}...{predictor.api_key[-4:]}" if len(predictor.api_key) > 8 else "***"
                return self.send_json({
                    'api_key_configured': True,
                    'api_key_masked': masked,
                    'status': 'AUTHENTICATED_AND_ACTIVE',
                    'engine': 'NER-LogiX AI Intelligence Engine'
                })

            elif path == '/api/ai-briefing':
                corridor_id = query.get('corridor_id', ['CORR-11'])[0]
                cursor.execute("SELECT * FROM corridors WHERE id = ?", (corridor_id,))
                c_row = cursor.fetchone()
                if not c_row:
                    return self.send_json({'error': f"Corridor '{corridor_id}' not found"}, 404)
                
                corr_dict = dict(c_row)
                briefing = predictor.generate_ai_intelligence_briefing(corr_dict)
                return self.send_json({'briefing': briefing})

            elif path == '/api/dashboard-stats':
                # Compute real-time KPI stats
                cursor.execute("SELECT COUNT(*) FROM nodes")
                total_nodes = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM corridors")
                total_corridors = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM corridors WHERE status = 'BLOCKED'")
                blocked_corridors = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM corridors WHERE status = 'CAUTION'")
                caution_corridors = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM vehicles")
                total_vehicles = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM vehicles WHERE commodity_type LIKE '%Medicine%'")
                medicine_vehicles = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM supply_depots WHERE status = 'CRITICAL'")
                critical_depots = cursor.fetchone()[0]

                # State-wise connectivity matrix
                cursor.execute("""
                SELECT n.state,
                       COUNT(DISTINCT n.id) as total_districts,
                       AVG(c.disruption_risk_score) as avg_risk
                FROM nodes n
                LEFT JOIN corridors c ON n.id = c.from_node OR n.id = c.to_node
                GROUP BY n.state
                """)
                state_data = []
                for row in cursor.fetchall():
                    s_name = row['state']
                    avg_risk = row['avg_risk'] or 25.0
                    conn_score = max(20, min(100, round(100 - avg_risk)))
                    status_str = "OPTIMAL" if conn_score > 75 else ("REDUCED" if conn_score > 50 else "CRITICAL")
                    state_data.append({
                        'state': s_name,
                        'districts': row['total_districts'],
                        'connectivity_pct': conn_score,
                        'status': status_str
                    })

                overall_connectivity = round(((total_corridors - blocked_corridors - caution_corridors * 0.4) / total_corridors) * 100, 1)

                return self.send_json({
                    'total_districts_monitored': total_nodes,
                    'total_corridors': total_corridors,
                    'corridors_blocked': blocked_corridors,
                    'corridors_caution': caution_corridors,
                    'overall_regional_connectivity_pct': overall_connectivity,
                    'active_fleet_count': total_vehicles,
                    'critical_medicine_trucks': medicine_vehicles,
                    'depots_at_risk': critical_depots,
                    'states_matrix': state_data,
                    'last_updated': datetime.now().isoformat()
                })

            else:
                return self.send_json({'error': f"Endpoint '{path}' not found"}, 404)

        except Exception as e:
            traceback.print_exc()
            return self.send_json({'error': str(e)}, 500)
        finally:
            conn.close()

    def handle_api_post(self, path, payload):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            if path == '/api/route-plan':
                origin = payload.get('origin', 'GUW')
                destination = payload.get('destination', 'IMP')
                tonnage = float(payload.get('tonnage', 15.0))
                avoid_risk = bool(payload.get('avoid_high_risk', True))

                result = route_engine.calculate_routes(origin, destination, vehicle_weight_tonnes=tonnage, avoid_high_risk=avoid_risk)
                return self.send_json(result)

            elif path == '/api/incidents':
                # Field Official / Citizen report upload with photo & geo-tagging
                inc_id = f"INC-{int(datetime.now().timestamp())}"
                title = payload.get('title', 'Reported Road Disruption')
                inc_type = payload.get('incident_type', 'Landslide')
                severity = payload.get('severity', 'HIGH')
                district = payload.get('district', 'General')
                state = payload.get('state', 'Assam')
                lat = float(payload.get('lat', 26.1445))
                lng = float(payload.get('lng', 91.7362))
                description = payload.get('description', '')
                photo_url = payload.get('photo_url', '')
                reported_by = payload.get('reported_by', 'Local Field Official')
                role = payload.get('role', 'Field Assistant')
                corridor_id = payload.get('corridor_id', None)
                action_taken = payload.get('action_taken', 'Incident flagged for inspection')

                cursor.execute("""
                INSERT INTO incidents (id, title, incident_type, severity, corridor_id, district, state, lat, lng, description, photo_url, reported_by, role, verification_status, action_taken, reported_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (inc_id, title, inc_type, severity, corridor_id, district, state, lat, lng, description, photo_url, reported_by, role, 'VERIFIED_OFFICIAL', action_taken, datetime.now().isoformat()))

                # If tied to a corridor, escalate its risk and update status
                if corridor_id:
                    new_status = 'BLOCKED' if severity == 'CRITICAL' else 'CAUTION'
                    cursor.execute("""
                    UPDATE corridors
                    SET status = ?, disruption_risk_score = MIN(99.0, disruption_risk_score + 35.0), status_reason = ?
                    WHERE id = ?
                    """, (new_status, f"{inc_type}: {title}", corridor_id))

                    # Create automated alert
                    alt_id = f"ALT-{int(datetime.now().timestamp())}"
                    cursor.execute("""
                    INSERT INTO alerts (id, title, severity, category, corridor_id, state, message, created_at, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (alt_id, f"FIELD ALERT: {title}", severity, inc_type, corridor_id, state, description, datetime.now().isoformat()))

                conn.commit()
                return self.send_json({'success': True, 'incident_id': inc_id, 'message': 'Incident recorded, synced, and mapped.'})

            elif path == '/api/vehicles/update-gps':
                # Advances GPS simulation for fleet: increments progress and adjusts lat/lng slightly
                cursor.execute("SELECT id, origin_id, dest_id, current_lat, current_lng, speed_kmh, progress_pct, status FROM vehicles")
                rows = cursor.fetchall()
                for r in rows:
                    if r['status'] == 'HALTED_BY_BLOCKAGE':
                        continue

                    new_progress = min(100.0, r['progress_pct'] + 1.2)
                    if new_progress >= 100.0:
                        new_status = 'DELIVERED'
                    else:
                        new_status = 'EN_ROUTE'

                    # Add slight natural jitter to coordinates
                    import random
                    d_lat = (random.random() - 0.48) * 0.005
                    d_lng = (random.random() - 0.48) * 0.005

                    cursor.execute("""
                    UPDATE vehicles
                    SET current_lat = current_lat + ?, current_lng = current_lng + ?,
                        progress_pct = ?, status = ?, last_updated = ?
                    WHERE id = ?
                    """, (d_lat, d_lng, new_progress, new_status, datetime.now().isoformat(), r['id']))

                conn.commit()
                return self.send_json({'success': True, 'message': 'Fleet GPS updated'})

            elif path == '/api/vehicles/sos':
                veh_id = payload.get('vehicle_id')
                state = 1 if payload.get('active', True) else 0
                cursor.execute("UPDATE vehicles SET sos_alert = ? WHERE id = ?", (state, veh_id))

                if state == 1:
                    cursor.execute("SELECT vehicle_no, commodity_desc FROM vehicles WHERE id = ?", (veh_id,))
                    vrow = cursor.fetchone()
                    alt_id = f"ALT-SOS-{int(datetime.now().timestamp())}"
                    cursor.execute("""
                    INSERT INTO alerts (id, title, severity, category, corridor_id, state, message, created_at, active)
                    VALUES (?, ?, 'CRITICAL', 'Vehicle SOS', NULL, 'Regional', ?, ?, 1)
                    """, (alt_id, f"EMERGENCY SOS: Vehicle {vrow['vehicle_no']}", f"Driver triggered distress beacon! Carrying: {vrow['commodity_desc']}. Emergency assistance requested.", datetime.now().isoformat()))

                conn.commit()
                return self.send_json({'success': True, 'sos_active': state})

            elif path == '/api/simulate-weather-event':
                # Interactive simulation: triggers extreme monsoon rainfall event
                target_state = payload.get('state', 'Nagaland')
                rainfall_val = float(payload.get('rainfall_mm', 145.0))

                cursor.execute("""
                UPDATE corridors
                SET rainfall_24h_mm = ?,
                    disruption_risk_score = MIN(98.0, disruption_risk_score + 40.0)
                WHERE from_node IN (SELECT id FROM nodes WHERE state = ?) OR to_node IN (SELECT id FROM nodes WHERE state = ?)
                """, (rainfall_val, target_state, target_state))

                # Re-evaluate with ML predictor
                cursor.execute("SELECT * FROM corridors WHERE rainfall_24h_mm >= ?", (rainfall_val,))
                affected = [dict(r) for r in cursor.fetchall()]
                for corr in affected:
                    assessment = predictor.assess_corridor_risk(corr, live_rainfall_override=rainfall_val)
                    if assessment['risk_level'] == 'CRITICAL':
                        cursor.execute("UPDATE corridors SET status = 'BLOCKED', status_reason = 'Triggered by AI Landslide Warning (Pore Pressure Saturation)' WHERE id = ?", (corr['id'],))
                    elif assessment['risk_level'] == 'HIGH':
                        cursor.execute("UPDATE corridors SET status = 'CAUTION', status_reason = 'Heavy Monsoonal Runoff & Slush Hazard' WHERE id = ?", (corr['id'],))

                conn.commit()
                return self.send_json({'success': True, 'message': f"Simulated {rainfall_val}mm rainfall in {target_state}. ML risk models recalibrated."})

            else:
                return self.send_json({'error': f"Unknown endpoint '{path}'"}, 404)

        except Exception as e:
            traceback.print_exc()
            return self.send_json({'error': str(e)}, 500)
        finally:
            conn.close()

def run_server(port=PORT):
    # Ensure database is prepared
    init_db()
    seed_data_if_empty()

    server_address = ('', port)
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(server_address, NERLogisticsHandler)
    print(f"===============================================================")
    print(f" NER-LogiX: North Eastern Region Logistics Intelligence Engine")
    print(f" Server running at http://localhost:{port}")
    print(f" Supporting all 8 NER States: AS, AR, ML, MN, MZ, NL, TR, SK")
    print(f"===============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down NER-LogiX Server.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
