from flask import (Flask, render_template, request, send_file,
                       send_from_directory, jsonify)
import pandas as pd
from io import BytesIO
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client() # Automatically picks up GEMINI_API_KEY from environment

app = Flask(__name__, template_folder='templates', static_folder='static')

# ── DATA LOADING ──────────────────────────────────────────
prediction_file_path = os.path.join(
    os.path.dirname(
        __file__), "..", "CaDRReS-master", "output", "ccle_all_pred_end.csv"
)

predictions_df = pd.read_csv(prediction_file_path, index_col=0)
DEFAULT_THRESHOLD = 3.0

# Pre-compute tissue type metadata (done once at startup)


def _parse_tissue(cell_line: str) -> str:
    parts = cell_line.split('_')
    return '_'.join(parts[1:]) if len(parts) > 1 else 'UNKNOWN'


_tissue_map = {cl: _parse_tissue(cl) for cl in predictions_df.index}
_tissue_list = sorted(set(_tissue_map.values()))


def predict_drug_response(selected_cell_line, selected_drug, threshold):
    threshold = float(
        threshold) if threshold is not None else DEFAULT_THRESHOLD
    prediction = predictions_df.loc[selected_cell_line, selected_drug]
    return 'Sensitive' if prediction > threshold else 'Resistant'


# ── HOME ──────────────────────────────────────────────────
@app.route('/')
def index():
    cell_lines = predictions_df.index.tolist()
    drugs = predictions_df.columns.tolist()
    return render_template(
        'index.html',
        cell_lines=cell_lines,
        drugs=drugs,
        default_threshold=DEFAULT_THRESHOLD,
        tissue_list=_tissue_list,
    )


# ── RESULT ────────────────────────────────────────────────
@app.route('/result', methods=['POST'])
def result():
    selected_cell_line = request.form.get('cell_line')
    selected_drug = request.form.get('drug')
    threshold = request.form.get(
        'threshold', default=DEFAULT_THRESHOLD, type=float)

    sensitivity = predict_drug_response(
        selected_cell_line, selected_drug, threshold)

    sensitive_cell_lines = predictions_df[
        predictions_df[selected_drug] > threshold
    ].index.tolist()
    resistant_cell_lines = predictions_df[
        predictions_df[selected_drug] <= threshold
    ].index.tolist()

    cell_row = predictions_df.loc[selected_cell_line]
    all_drugs = cell_row.index.tolist()
    all_ic50 = [round(float(v), 4) for v in cell_row.values.tolist()]
    current_ic50 = float(predictions_df.loc[selected_cell_line, selected_drug])

    return render_template(
        'result.html',
        cell_line=selected_cell_line,
        drug=selected_drug,
        sensitivity=sensitivity,
        sensitive_count=len(sensitive_cell_lines),
        resistant_count=len(resistant_cell_lines),
        sensitive_cell_lines=sensitive_cell_lines,
        resistant_cell_lines=resistant_cell_lines,
        threshold=threshold,
        all_drugs=all_drugs,
        all_ic50=all_ic50,
        current_ic50=current_ic50,
    )


# ── EXPLORE PAGE ──────────────────────────────────────────
@app.route('/explore')
def explore():
    drugs = predictions_df.columns.tolist()
    return render_template(
        'explore.html',
        drugs=drugs,
        tissue_list=_tissue_list,
        default_threshold=DEFAULT_THRESHOLD,
    )


# ── HEATMAP DATA API ──────────────────────────────────────
@app.route('/api/heatmap-data')
def heatmap_data():
    """
    Returns JSON for Plotly heatmap:
    {
      x: [drug names],
      y: [cell line names],
      z: [[ic50 values]],
      tissues: [tissue per cell line],
      threshold: float
    }
    Supports optional ?tissue=LUNG filter.
    """
    tissue_filter = request.args.get('tissue', '').strip().upper()
    threshold = request.args.get('threshold', DEFAULT_THRESHOLD, type=float)

    if tissue_filter and tissue_filter != 'ALL':
        mask = [_tissue_map.get(cl, '') ==
                tissue_filter for cl in predictions_df.index]
        filtered_df = predictions_df[mask]
    else:
        filtered_df = predictions_df

    # Sort cell lines by their max IC50 (most sensitive lines first)
    filtered_df = filtered_df.loc[filtered_df.max(
        axis=1).sort_values(ascending=False).index]

    cell_lines = filtered_df.index.tolist()
    drugs = filtered_df.columns.tolist()
    z_values = [[round(float(v), 3) for v in row]
                for row in filtered_df.values.tolist()]
    tissues = [_tissue_map.get(cl, 'UNKNOWN') for cl in cell_lines]

    return jsonify({
        'x':         drugs,
        'y':         cell_lines,
        'z':         z_values,
        'tissues':   tissues,
        'threshold': threshold,
        'count':     len(cell_lines),
    })


# ── CSV DOWNLOADS ─────────────────────────────────────────
@app.route('/download_sensitive_csv/<cell_line>/<selected_drug>')
def download_sensitive_csv(cell_line, selected_drug):
    threshold = request.args.get(
        'threshold', default=DEFAULT_THRESHOLD, type=float)
    sensitive_cell_lines = predictions_df[
        predictions_df[selected_drug] > threshold
    ].index.tolist()
    df = pd.DataFrame({'Cell Lines': sensitive_cell_lines})
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f'{cell_line}_{selected_drug}_sensitive_cell_lines.csv',
        mimetype='text/csv',
    )


@app.route('/download_resistant_csv/<cell_line>/<selected_drug>')
def download_resistant_csv(cell_line, selected_drug):
    threshold = request.args.get(
        'threshold', default=DEFAULT_THRESHOLD, type=float)
    resistant_cell_lines = predictions_df[
        predictions_df[selected_drug] <= threshold
    ].index.tolist()
    df = pd.DataFrame({'Cell Lines': resistant_cell_lines})
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f'{cell_line}_{selected_drug}_resistant_cell_lines.csv',
        mimetype='text/csv',
    )


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/api/explain', methods=['POST'])
def api_explain():
    data = request.get_json()
    cell_line = data.get('cell_line')
    drug = data.get('drug')
    ic50 = data.get('ic50')
    sensitivity = data.get('sensitivity')
    tissue = data.get('tissue')

    if not all([cell_line, drug, ic50, sensitivity, tissue]):
        return jsonify({"error": "Missing parameters"}), 400

    prompt = f"""
    You are an expert clinical oncologist. Explain to another researcher why the cell line '{cell_line}' (tissue origin: {tissue}) shows a {sensitivity.lower()} response to the drug '{drug}', given that its predicted IC50 value is {ic50:.2f}.
    
    Keep the explanation under 150 words, scientifically accurate, and use a professional but accessible tone. Explain what the drug targets, and why this specific tissue type might or might not respond to it.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({"explanation": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/combinations', methods=['POST'])
def api_combinations():
    data = request.get_json()
    cell_line = data.get('cell_line')
    
    if not cell_line or cell_line not in predictions_df.index:
        return jsonify({"error": "Invalid or missing cell_line"}), 400

    # Get IC50s for this cell line and sort descending (highest IC50 = most sensitive)
    cell_data = predictions_df.loc[cell_line].sort_values(ascending=False)
    
    # Get top 3 drugs
    top_drugs = cell_data.index[:3].tolist()
    top_scores = cell_data.values[:3].tolist()
    
    if len(top_drugs) < 3:
        return jsonify({"error": "Not enough data for combinations"}), 400
        
    pairs = [
        (top_drugs[0], top_drugs[1], top_scores[0] + top_scores[1]),
        (top_drugs[0], top_drugs[2], top_scores[0] + top_scores[2]),
        (top_drugs[1], top_drugs[2], top_scores[1] + top_scores[2])
    ]
    
    tissue = cell_line.split('_')[1] if '_' in cell_line else 'Unknown'
    
    prompt = f"""
    You are an expert clinical oncologist. I have a cell line '{cell_line}' (tissue: {tissue}) which is highly sensitive to the following three drugs: {top_drugs[0]}, {top_drugs[1]}, and {top_drugs[2]}.
    
    I want to propose three combination therapies:
    1. {pairs[0][0]} + {pairs[0][1]}
    2. {pairs[1][0]} + {pairs[1][1]}
    3. {pairs[2][0]} + {pairs[2][1]}
    
    For EACH combination, write a 2-3 sentence clinical rationale explaining why combining these two specific drugs might be synergistic or beneficial for a {tissue} cancer. Format your response exactly like this:
    
    COMBINATION 1: [Rationale for {pairs[0][0]} + {pairs[0][1]}]
    COMBINATION 2: [Rationale for {pairs[1][0]} + {pairs[1][1]}]
    COMBINATION 3: [Rationale for {pairs[2][0]} + {pairs[2][1]}]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text
        
        import re
        
        # Parse the output
        rationales = []
        for i in range(1, 4):
            # Regex to match case-insensitive "COMBINATION i:" with optional markdown asterisks
            pattern = rf"(?i)\**COMBINATION\s+{i}:\**\s*(.*?)(?=(?i)\**COMBINATION\s+{i+1}:|$)"
            match = re.search(pattern, text, re.DOTALL)
            
            if match:
                rationale = match.group(1).strip()
                # Clean up any leftover markdown asterisks
                rationale = rationale.replace('**', '').strip()
                rationales.append(rationale)
            else:
                rationales.append("Rationale could not be generated.")
                
        results = [
            {"drug1": pairs[0][0], "drug2": pairs[0][1], "score": float(pairs[0][2]), "rationale": rationales[0]},
            {"drug1": pairs[1][0], "drug2": pairs[1][1], "score": float(pairs[1][2]), "rationale": rationales[1]},
            {"drug1": pairs[2][0], "drug2": pairs[2][1], "score": float(pairs[2][2]), "rationale": rationales[2]},
        ]
        return jsonify({"combinations": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
