"""
NER-LogiX Intelligent Multi-Factor Route Optimization & Resilient Alternate Routing Engine
Calculates standard and risk-resilient bypass routes across North Eastern Region road networks
using weighted Dijkstra pathfinding, terrain penalties, bridge load verification, and live disruption avoidance.
"""

import heapq
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

class RouteEngine:
    def __init__(self):
        pass

    def load_graph(self):
        """
        Loads nodes and corridors from SQLite to construct the bidirectional routing graph.
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, state, district, lat, lng, elevation_m, hub_type FROM nodes")
        nodes = {row['id']: dict(row) for row in cursor.fetchall()}

        cursor.execute("""
        SELECT id, code, name, from_node, to_node, distance_km, base_travel_hours,
               terrain_type, road_class, status, status_reason, slope_angle_deg,
               disruption_risk_score, bridge_max_tonnage, rainfall_24h_mm
        FROM corridors
        """)
        corridors = [dict(row) for row in cursor.fetchall()]
        conn.close()

        graph = {node_id: [] for node_id in nodes}
        for c in corridors:
            u, v = c['from_node'], c['to_node']
            if u in graph and v in graph:
                # Add forward edge
                graph[u].append((v, c))
                # Add reverse edge (bidirectional road)
                graph[v].append((u, c))

        return nodes, corridors, graph

    def calculate_routes(self, origin_id, dest_id, vehicle_weight_tonnes=15.0, avoid_high_risk=True):
        """
        Computes Primary Route, AI-Recommended Resilient Alternate Route, and Emergency Corridor.
        """
        nodes, corridors, graph = self.load_graph()

        if origin_id not in nodes or dest_id not in nodes:
            return {"error": f"Invalid origin '{origin_id}' or destination '{dest_id}'."}

        if origin_id == dest_id:
            return {"error": "Origin and destination are the same location."}

        # 1. Calculate Standard Shortest Distance Route (ignores temporary risks for baseline)
        standard_path = self._dijkstra(graph, origin_id, dest_id, weight_mode='distance', max_tonnage=vehicle_weight_tonnes)

        # 2. Calculate AI Resilient Route (penalizes risk, blocked roads, and weak bridges)
        resilient_path = self._dijkstra(graph, origin_id, dest_id, weight_mode='ai_resilient', max_tonnage=vehicle_weight_tonnes)

        # 3. Calculate Backup / Alternate Route (if resilient is different from standard, or finds 2nd best)
        emergency_path = self._dijkstra(graph, origin_id, dest_id, weight_mode='green_corridor', max_tonnage=vehicle_weight_tonnes)

        routes = []

        if resilient_path:
            routes.append(self._format_route_details("AI-Recommended Resilient Route", resilient_path, nodes, is_recommended=True))

        if standard_path and standard_path != resilient_path:
            routes.append(self._format_route_details("Primary / Direct Route (Subject to Blockages)", standard_path, nodes, is_recommended=False))

        if emergency_path and emergency_path != resilient_path and emergency_path != standard_path:
            routes.append(self._format_route_details("Emergency SDRF/NDRF Bypass Corridor", emergency_path, nodes, is_recommended=False))

        return {
            "origin": nodes[origin_id],
            "destination": nodes[dest_id],
            "requested_cargo_tonnage": vehicle_weight_tonnes,
            "routes_found": len(routes),
            "routes": routes
        }

    def _dijkstra(self, graph, start, goal, weight_mode='ai_resilient', max_tonnage=15.0):
        # priority queue stores: (cumulative_cost, current_node, path_nodes, path_edges)
        pq = [(0.0, start, [start], [])]
        visited = {}

        while pq:
            cost, u, path_nodes, path_edges = heapq.heappop(pq)

            if u in visited and visited[u] <= cost:
                continue
            visited[u] = cost

            if u == goal:
                return {'nodes': path_nodes, 'edges': path_edges}

            for v, edge in graph[u]:
                edge_cost = self._compute_edge_cost(edge, weight_mode, max_tonnage)
                if edge_cost >= 1e8: # Impassable
                    continue

                new_cost = cost + edge_cost
                if v not in visited or new_cost < visited[v]:
                    heapq.heappush(pq, (new_cost, v, path_nodes + [v], path_edges + [edge]))

        return None

    def _compute_edge_cost(self, edge, mode, max_tonnage):
        dist = edge['distance_km']
        risk = edge['disruption_risk_score']
        status = edge['status']
        tonnage_limit = edge['bridge_max_tonnage']

        # Weight capacity check: Heavy vehicles cannot cross under-capacity bridges
        if max_tonnage > tonnage_limit:
            if mode in ['ai_resilient', 'green_corridor']:
                return 1e9  # Disallow for resilient route

        if mode == 'distance':
            return dist

        elif mode == 'ai_resilient':
            if status == 'BLOCKED':
                return 1e9 # Avoid completely if alternate exists
            
            # Non-linear penalty for disruption risk
            risk_multiplier = 1.0 + (risk / 100.0) ** 2 * 3.5
            caution_penalty = 50.0 if status == 'CAUTION' else 0.0
            return dist * risk_multiplier + caution_penalty

        elif mode == 'green_corridor':
            # Emergency route prioritizes 4-lane or designated bypasses
            if status == 'BLOCKED':
                return 1e9
            multiplier = 0.8 if 'Highway' in edge['road_class'] else 1.2
            return dist * multiplier + (risk * 0.5)

        return dist

    def _format_route_details(self, label, path_data, nodes, is_recommended=False):
        node_ids = path_data['nodes']
        edges = path_data['edges']

        total_distance_km = sum(e['distance_km'] for e in edges)
        base_hours = sum(e['base_travel_hours'] for e in edges)

        # Calculate delay based on edge status and risk scores
        delay_hours = 0.0
        max_risk = 0.0
        has_blocked_segment = False
        has_caution_segment = False
        reasons = []

        for e in edges:
            if e['status'] == 'BLOCKED':
                has_blocked_segment = True
                delay_hours += 8.0
                reasons.append(f"{e['code']} is BLOCKED: {e['status_reason']}")
            elif e['status'] == 'CAUTION':
                has_caution_segment = True
                delay_hours += 2.0
                reasons.append(f"{e['code']} CAUTION: {e['status_reason']}")

            if e['disruption_risk_score'] > max_risk:
                max_risk = e['disruption_risk_score']

        total_travel_hours = round(base_hours + delay_hours, 1)

        # Safety rating
        avg_risk = sum(e['disruption_risk_score'] for e in edges) / len(edges) if edges else 0
        safety_score = max(5, round(100 - avg_risk, 1))

        # Waypoints coordinates for GIS rendering
        waypoints = []
        for nid in node_ids:
            node = nodes[nid]
            waypoints.append({
                'id': node['id'],
                'name': node['name'],
                'state': node['state'],
                'district': node['district'],
                'lat': node['lat'],
                'lng': node['lng'],
                'elevation_m': node['elevation_m']
            })

        # Elevation stats
        elevations = [w['elevation_m'] for w in waypoints]
        min_elevation = min(elevations) if elevations else 0
        max_elevation = max(elevations) if elevations else 0

        # Step-by-step turns
        turn_by_turn = []
        for i, edge in enumerate(edges):
            u_name = nodes[edge['from_node']]['name']
            v_name = nodes[edge['to_node']]['name']
            turn_by_turn.append({
                'step': i + 1,
                'instruction': f"Transit via {edge['code']} ({edge['name']}) towards {v_name}",
                'distance_km': edge['distance_km'],
                'road_type': edge['road_class'],
                'terrain': edge['terrain_type'],
                'segment_status': edge['status'],
                'segment_risk': edge['disruption_risk_score']
            })

        return {
            'label': label,
            'is_recommended': is_recommended,
            'total_distance_km': round(total_distance_km, 1),
            'base_travel_hours': round(base_hours, 1),
            'delay_hours': round(delay_hours, 1),
            'total_travel_hours': total_travel_hours,
            'safety_score': safety_score,
            'max_corridor_risk': max_risk,
            'has_blocked_segment': has_blocked_segment,
            'has_caution_segment': has_caution_segment,
            'status_notes': reasons,
            'min_elevation_m': min_elevation,
            'max_elevation_m': max_elevation,
            'waypoints': waypoints,
            'turn_by_turn': turn_by_turn
        }

route_engine = RouteEngine()

if __name__ == '__main__':
    # Test pathfinding from Guwahati to Imphal (DIM to IMP has Paglapahar blockage)
    result = route_engine.calculate_routes('GUW', 'IMP', vehicle_weight_tonnes=18.0)
    print("Origin -> Destination:", result['origin']['name'], "->", result['destination']['name'])
    for r in result['routes']:
        print(f"[{r['label']}] Dist: {r['total_distance_km']}km, Hours: {r['total_travel_hours']}h (Delay: +{r['delay_hours']}h), Safety: {r['safety_score']}%, Blocked: {r['has_blocked_segment']}")
        for step in r['turn_by_turn']:
            print("  -", step['instruction'], f"({step['distance_km']}km, status: {step['segment_status']})")
