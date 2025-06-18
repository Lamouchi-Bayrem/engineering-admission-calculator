from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Hypothetical last year (2023-2024) orientation score thresholds
ORIENTATION_THRESHOLDS = {
    'ENIT': {'min_score': 85, 'avg_score': 90},
    'ENSI': {'min_score': 80, 'avg_score': 88},
    'INSAT': {'min_score': 78, 'avg_score': 85}
}

def calculate_score_a(data):
    try:
        mg = float(data.get('mg', 0))
        rank1 = int(data.get('rank1', 1))
        effectif1 = int(data.get('effectif1', 1))
        rank2 = int(data.get('rank2', 1))
        effectif2 = int(data.get('effectif2', 1))
        birth_year = int(data.get('birthYear', 2000))
        bac_score = float(data.get('bacScore', 0))
        french1 = float(data.get('french1', 0))
        french2 = float(data.get('french2', 0))
        english1 = float(data.get('english1', 0))
        english2 = float(data.get('english2', 0))
        math1 = float(data.get('math1', 0))
        math2 = float(data.get('math2', 0))
        physics1 = float(data.get('physics1', 0))
        physics2 = float(data.get('physics2', 0))
        cs1 = float(data.get('cs1', 0))
        cs2 = float(data.get('cs2', 0))

        # Calculate M
        M = 0
        if mg >= 15:
            M = 100
        elif 10 < mg < 15:
            M = 20 * (mg - 10)

        # Calculate R
        ri1 = (rank1 - 1) / effectif1
        ri2 = (rank2 - 1) / effectif2
        Ri1 = 100 - (700 * ri1) / 3 if ri1 <= 0.3 else 0
        Ri2 = 100 - (700 * ri2) / 3 if ri2 <= 0.3 else 0
        R = (Ri1 + Ri2) / 2

        # Calculate B1
        B1 = 5 if birth_year >= 2023 - 22 else 0

        # Calculate B2
        B2 = 0
        if bac_score >= 16:
            B2 = 20
        elif bac_score >= 14:
            B2 = 15
        elif bac_score >= 12:
            B2 = 10
        elif bac_score >= 11:
            B2 = 5

        # Calculate ML
        ML = (french1 + french2 + english1 + english2) / 4

        # Calculate Score E (weighted average: 40% Math, 30% Physics, 30% CS, scaled to 100)
        score_e = ((math1 + math2) * 0.4 + (physics1 + physics2) * 0.3 + (cs1 + cs2) * 0.3) / 2 * 5

        # Calculate Score A
        score_a = 0.2 * M + (1.4 / 3) * R + (5 / 6) * ML + (2 / 3) * (B1 + B2)
        global_score = score_a * 0.7 + score_e * 0.3

        # Generate orientation suggestions
        suggestions = []
        for school, thresholds in ORIENTATION_THRESHOLDS.items():
            if global_score >= thresholds['min_score']:
                status = 'Strong' if global_score >= thresholds['avg_score'] else 'Moderate'
                suggestions.append(f'{school}: {status} chance (Min: {thresholds["min_score"]}, Avg: {thresholds["avg_score"]})')
            else:
                suggestions.append(f'{school}: Low chance (Min: {thresholds["min_score"]}, Avg: {thresholds["avg_score"]})')

        return {
            'scoreA': round(score_a, 2),
            'scoreE': round(score_e, 2),
            'globalScore': round(global_score, 2),
            'scoreEComponents': {
                'math': round((math1 + math2) / 2, 2),
                'physics': round((physics1 + physics2) / 2, 2),
                'cs': round((cs1 + cs2) / 2, 2)
            },
            'suggestions': suggestions
        }
    except (ValueError, TypeError):
        return {'error': 'Invalid input data'}

def calculate_score_second_year(data):
    try:
        l1 = float(data.get('l1', 0))
        l2 = float(data.get('l2', 0))
        l3 = float(data.get('l3', 0))
        m1 = float(data.get('m1', 0))
        birth_year = int(data.get('birthYear', 2000))
        bac_score = float(data.get('bacScore', 0))
        redoublant = data.get('redoublant', False) == 'on'

        # Calculate M
        mg = (l1 + l2 + l3 + m1) / 4
        M = 0
        if mg >= 15:
            M = 100
        elif 10 < mg < 15:
            M = 20 * (mg - 10)

        # Calculate B1
        B1 = 5 if birth_year >= 2023 - 24 else 0

        # Calculate B2
        B2 = 0
        if bac_score >= 16:
            B2 = 20
        elif bac_score >= 14:
            B2 = 15
        elif bac_score >= 12:
            B2 = 10
        elif bac_score >= 11:
            B2 = 5

        # Calculate C
        C = 0.8 if redoublant else 1

        score = C * (M + B1 + B2)

        # Generate orientation suggestions
        suggestions = []
        for school, thresholds in ORIENTATION_THRESHOLDS.items():
            if score >= thresholds['min_score']:
                status = 'Strong' if score >= thresholds['avg_score'] else 'Moderate'
                suggestions.append(f'{school}: {status} chance (Min: {thresholds["min_score"]}, Avg: {thresholds["avg_score"]})')
            else:
                suggestions.append(f'{school}: Low chance (Min: {thresholds["min_score"]}, Avg: {thresholds["avg_score"]})')

        return {'score': round(score, 2), 'suggestions': suggestions}
    except (ValueError, TypeError):
        return {'error': 'Invalid input data'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate/first', methods=['POST'])
def calculate_first_year():
    data = request.get_json()
    result = calculate_score_a(data)
    return jsonify(result)

@app.route('/api/calculate/second', methods=['POST'])
def calculate_second_year():
    data = request.get_json()
    result = calculate_score_second_year(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)