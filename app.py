import os
import io
import csv
import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta, date
import holidays

app = Flask(__name__)

# --- Configuration ---
DB_FILE = 'office_seating.db'
BAVARIAN_HOLIDAYS = holidays.Germany(subdiv='BY')
DESK_NAMES = ['Fenster links', 'Fenster rechts', 'Gang links', 'Gang rechts']


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            date TEXT NOT NULL,
            desk TEXT NOT NULL,
            user TEXT NOT NULL,
            PRIMARY KEY (date, desk)
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_bookings_user_date
        ON bookings(user, date)
        """
    )
    conn.commit()
    conn.close()

def get_current_and_next_week_dates():
    """Generates a list of dates (strings) for current and next week's work days."""
    today = date.today()
    work_days = []
    
    # Start from the beginning of current week (Monday)
    current_week_monday = today - timedelta(days=today.weekday())
    
    # Get dates for current and next week (2 weeks total)
    for week_offset in range(2):
        week_monday = current_week_monday + timedelta(weeks=week_offset)
        for day_offset in range(5):  # Mon to Fri
            day = week_monday + timedelta(days=day_offset)
            # Only include dates from today onwards and exclude holidays
            if day >= today and day not in BAVARIAN_HOLIDAYS:
                work_days.append(day.strftime('%Y-%m-%d'))
    
    return work_days

def fetch_bookings_for_dates(conn, dates):
    if not dates:
        return {}
    placeholders = ','.join('?' for _ in dates)
    rows = conn.execute(
        f"SELECT date, desk, user FROM bookings WHERE date IN ({placeholders})",
        dates,
    ).fetchall()
    bookings = {}
    for row in rows:
        bookings.setdefault(row['date'], {})[row['desk']] = row['user']
    return bookings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Returns the schedule for current and next week."""
    target_dates = get_current_and_next_week_dates()
    conn = get_db()
    bookings = fetch_bookings_for_dates(conn, target_dates)
    desk_columns = DESK_NAMES
    
    schedule = []
    
    for d in target_dates:
        # Format date as "Tuesday, 30.01.2026"
        date_obj = datetime.strptime(d, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%A, %d.%m.%Y')
        
        day_data = {
            'date': d,
            'formatted_date': formatted_date,
            'desks': []
        }
        
        for desk in desk_columns:
            occupant = bookings.get(d, {}).get(desk)
            day_data['desks'].append({
                'name': desk,
                'occupant': occupant
            })
            
        schedule.append(day_data)
        
    return jsonify({'schedule': schedule, 'desk_names': desk_columns})

@app.route('/api/book', methods=['POST'])
def book_seat():
    data = request.json
    user_name = data.get('name')
    target_date = data.get('date')
    target_desk = data.get('desk')
    
    if not user_name or not target_date or not target_desk:
        return jsonify({'success': False, 'message': 'Missing information.'}), 400

    conn = get_db()

    # 1. Check if desk is already taken
    existing = conn.execute(
        "SELECT user FROM bookings WHERE date = ? AND desk = ?",
        (target_date, target_desk),
    ).fetchone()
    if existing:
        return jsonify({'success': False, 'message': 'Desk already taken.'}), 409

    # 2. Check if user already booked this date
    already = conn.execute(
        "SELECT 1 FROM bookings WHERE date = ? AND user = ?",
        (target_date, user_name),
    ).fetchone()
    if already:
        return jsonify({'success': False, 'message': 'You have already booked a seat for this day.'}), 400

    # 3. Book the seat
    conn.execute(
        "INSERT INTO bookings (date, desk, user) VALUES (?, ?, ?)",
        (target_date, target_desk, user_name),
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/cancel', methods=['POST'])
def cancel_booking():
    """Cancel a booking."""
    data = request.json
    user_name = data.get('name')
    target_date = data.get('date')
    target_desk = data.get('desk')
    
    if not user_name or not target_date or not target_desk:
        return jsonify({'success': False, 'message': 'Missing information.'}), 400
    
    conn = get_db()

    current = conn.execute(
        "SELECT user FROM bookings WHERE date = ? AND desk = ?",
        (target_date, target_desk),
    ).fetchone()

    if not current:
        return jsonify({'success': False, 'message': 'No booking to cancel.'}), 404

    if current['user'] != user_name:
        return jsonify({'success': False, 'message': 'You can only cancel your own bookings.'}), 403

    conn.execute(
        "DELETE FROM bookings WHERE date = ? AND desk = ?",
        (target_date, target_desk),
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/download', methods=['GET'])
def download_schedule():
    """Download all bookings as CSV."""
    conn = get_db()
    rows = conn.execute(
        "SELECT date, desk, user FROM bookings ORDER BY date, desk"
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Desk', 'User'])
    for row in rows:
        writer.writerow([row['date'], row['desk'], row['user']])

    mem = io.BytesIO(output.getvalue().encode('utf-8'))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name='office_seating.csv', mimetype='text/csv')

init_db()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host=host, port=port)