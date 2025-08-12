from flask import Flask, request, render_template, send_file, redirect, url_for, flash, session
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import io
import os

UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
CHART_FOLDER = 'static/charts'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)

app = Flask(__name__)
# SECRET_KEY will be read from environment in production (Render). For local dev this default is fine.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
# Optional: set an ACCESS_CODE if you want to gate the app (we'll use this later if you want)
ACCESS_CODE = os.environ.get("ACCESS_CODE", "")

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def generate_report(df, base_name='report'):
    # Basic cleaning
    df = df.copy()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(how='all')
    # Summary
    total_revenue = df['Revenue'].sum() if 'Revenue' in df.columns else None
    total_units = df['Units Sold'].sum() if 'Units Sold' in df.columns else None
    top_product = df.groupby('Product')['Revenue'].sum().idxmax() if 'Product' in df.columns and 'Revenue' in df.columns else None
    top_region = df.groupby('Region')['Revenue'].sum().idxmax() if 'Region' in df.columns and 'Revenue' in df.columns else None

    # Monthly revenue chart if Date and Revenue available
    chart_path = None
    if 'Date' in df.columns and 'Revenue' in df.columns:
        monthly_revenue = df.groupby(df['Date'].dt.to_period('M'))['Revenue'].sum()
        plt.figure(figsize=(8,4))
        monthly_revenue.plot(kind='bar')
        plt.title('Monthly Revenue')
        plt.xlabel('Month')
        plt.ylabel('Revenue')
        plt.tight_layout()
        chart_path = os.path.join(CHART_FOLDER, f'{base_name}_monthly.png')
        plt.savefig(chart_path)
        plt.close()

    # Create Excel report
    excel_path = os.path.join(REPORT_FOLDER, f'{base_name}_report.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Summary sheet
        summary = {
            'Total Revenue': [total_revenue],
            'Total Units Sold': [total_units],
            'Top Product': [top_product],
            'Top Region': [top_region]
        }
        pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)

        # Raw data
        df.to_excel(writer, sheet_name='Raw Data', index=False)

    return excel_path, chart_path, total_revenue, total_units, top_product, top_region

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = os.path.join(UPLOAD_FOLDER, datetime.now().strftime('%Y%m%d%H%M%S_') + file.filename)
        file.save(filename)
        try:
            df = pd.read_csv(filename)
        except Exception:
            try:
                df = pd.read_excel(filename)
            except Exception as e:
                flash('Unable to read file. Make sure it is a valid CSV or Excel file.')
                return redirect(request.url)

        excel_path, chart_path, total_revenue, total_units, top_product, top_region = generate_report(df, base_name=datetime.now().strftime('%Y%m%d%H%M%S'))
        return render_template('result.html',
                               excel_path=os.path.basename(excel_path),
                               chart_path=os.path.basename(chart_path) if chart_path else None,
                               total_revenue=total_revenue,
                               total_units=total_units,
                               top_product=top_product,
                               top_region=top_region)
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(REPORT_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash('File not found.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Read PORT & DEBUG from environment (Render sets PORT automatically)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() in ('1', 'true')
    app.run(host='0.0.0.0', port=port, debug=debug)