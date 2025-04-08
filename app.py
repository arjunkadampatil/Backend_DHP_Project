from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

PRECALC_FILE = 'filtered_data.csv'

def load_precalc():
    return pd.read_csv(PRECALC_FILE)

@app.route('/questions-per-month')
def questions_per_month():
    df = load_precalc()
    df = df[df['View'] == 'questions-month']
    labels = sorted(df['Label'].unique())
    tags = df['Tag'].unique()
    datasets = []
    for tag in tags:
        tag_data = df[df['Tag'] == tag].set_index('Label').reindex(labels, fill_value=0)
        datasets.append({'label': tag, 'data': tag_data['Value'].tolist()})
    return jsonify({'labels': labels, 'datasets': datasets})

@app.route('/hourly-trend')
def hourly_trend():
    df = load_precalc()
    df = df[df['View'] == 'hourly-trend']
    labels = list(map(str, range(24)))
    tags = df['Tag'].unique()
    datasets = []
    for tag in tags:
        tag_data = df[df['Tag'] == tag].set_index('Label').reindex(labels, fill_value=0)
        datasets.append({'label': tag, 'data': tag_data['Value'].tolist()})
    return jsonify({'labels': labels, 'datasets': datasets})

@app.route('/questions-by-year')
def questions_by_year():
    df = load_precalc()
    df = df[df['View'] == 'questions-year']
    return jsonify({
        'labels': df['Label'].tolist(),
        'data': df['Value'].tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)
