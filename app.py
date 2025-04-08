from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

CSV_FILE = 'filtered_data.csv'

def load_data():
    df = pd.read_csv(CSV_FILE)
    df['Date and Time'] = pd.to_datetime(df['Date and Time'], errors='coerce')

    # ⚠️ Remove timezone info to avoid warning
    df['Date and Time'] = df['Date and Time'].dt.tz_localize(None)

    df.dropna(subset=['Date and Time'], inplace=True)
    df['Month'] = df['Date and Time'].dt.to_period('M').astype(str)
    df['Year'] = df['Date and Time'].dt.year
    df['Hour'] = df['Date and Time'].dt.hour

    rows = []
    for _, row in df.iterrows():
        tags = str(row['Tags (Languages)']).split(',')
        for tag in tags:
            rows.append({
                'Tag': tag.strip(),
                'Date and Time': row['Date and Time'],
                'Month': row['Month'],
                'Year': row['Year'],
                'Hour': row['Hour']
            })
    return pd.DataFrame(rows)

@app.route('/questions-per-month')
def questions_per_month():
    df = load_data()
    top_tags = df['Tag'].value_counts().nlargest(5).index.tolist()
    df = df[df['Tag'].isin(top_tags)]
    pivot = df.groupby(['Month', 'Tag']).size().unstack(fill_value=0).sort_index()
    return jsonify({
        'labels': pivot.index.tolist(),
        'datasets': [{'label': tag, 'data': pivot[tag].tolist()} for tag in pivot.columns]
    })

@app.route('/hourly-trend')
def hourly_trend():
    df = load_data()
    top_tags = df['Tag'].value_counts().nlargest(5).index.tolist()
    df = df[df['Tag'].isin(top_tags)]
    hourly = df.groupby(['Hour', 'Tag']).size().unstack(fill_value=0).reindex(range(24), fill_value=0)
    return jsonify({
        'labels': list(range(24)),
        'datasets': [{'label': tag, 'data': hourly[tag].tolist()} for tag in hourly.columns]
    })

@app.route('/questions-by-year')
def questions_by_year():
    df = load_data()
    by_year = df.groupby('Year').size()
    return jsonify({
        'labels': by_year.index.astype(str).tolist(),
        'data': by_year.tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)
