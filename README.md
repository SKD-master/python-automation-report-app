# One-Click Report Generator (Flask)

## What it is
A minimal Flask web application that accepts an uploaded CSV or Excel file, cleans the data, generates summary statistics and a monthly revenue chart (if Date & Revenue columns exist), and returns a downloadable Excel report.

## Run locally (development)
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open http://127.0.0.1:5000 in your browser.

## Deploy to Render (recommended simple option)
1. Create a new Web Service on Render (https://render.com).
2. Connect your GitHub repo containing this project.
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python app.py`
5. Deploy.

## Quick selling options
- **Sell access link**: Deploy to a cheap Render/Heroku instance and sell access via Gumroad — buyers receive the link and credentials.
- **Sell packaged app**: Zip the project and sell the zip on Gumroad. Buyers run locally following README.
- **Add payments**: For in-app payments, integrate Stripe or PayPal (requires SSL/domain & account setup).

## Notes
- Replace `app.secret_key` with a secure random string in production.
- For production, run behind a proper WSGI server (gunicorn) and configure static file serving.