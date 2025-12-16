import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta, date
import holidays

app = Flask(__name__)

# --- Configuration ---
EXCEL_FILE = 'office_seating.xlsx'
BAVARIAN_HOLIDAYS = holidays.Germany(subdiv='BY')

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

def init_excel():
    """Initializes the Excel file with templates if it doesn't exist."""
    if not os.path.exists(EXCEL_FILE):
        # Create template structure with funny desk names
        df = pd.DataFrame(columns=['Date', 'The Throne', 'Procrastination Station', 'Caffeine Corner', 'Innovation Island', 'Chaos Central'])
        df.to_excel(EXCEL_FILE, index=False)

def read_data():
    """Reads the Excel file and normalizes it."""
    init_excel()
    df = pd.read_excel(EXCEL_FILE)
    df['Date'] = df['Date'].astype(str) # Ensure dates are strings for comparison
    return df

def save_data(df):
    """Saves the DataFrame back to Excel."""
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Returns the schedule for current and next week."""
    target_dates = get_current_and_next_week_dates()
    df = read_data()
    
    # Get all desk columns (exclude 'Date')
    desk_columns = [c for c in df.columns if c != 'Date']
    
    schedule = []
    
    for d in target_dates:
        # Check if row exists for this date
        row = df[df['Date'] == d]
        
        # Format date as "Tuesday, 30.01.2026"
        date_obj = datetime.strptime(d, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%A, %d.%m.%Y')
        
        day_data = {
            'date': d,
            'formatted_date': formatted_date,
            'desks': []
        }
        
        for desk in desk_columns:
            occupant = None
            if not row.empty:
                val = row.iloc[0][desk]
                if pd.notna(val) and str(val).strip() != "":
                    occupant = str(val)
            
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

    df = read_data()
    
    # 1. Check if row exists for date, if not create it
    if target_date not in df['Date'].values:
        new_row = {col: None for col in df.columns}
        new_row['Date'] = target_date
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Get the index of the date
    idx = df.index[df['Date'] == target_date].tolist()[0]
    
    # 2. Check if desk is already taken
    current_occupant = df.at[idx, target_desk]
    if pd.notna(current_occupant) and str(current_occupant).strip() != "":
        return jsonify({'success': False, 'message': 'Desk already taken.'}), 409

    # 3. Check if USER has already booked a desk for this day (Max 1 rule)
    row_data = df.iloc[idx]
    for col in df.columns:
        if col != 'Date' and row_data[col] == user_name:
             return jsonify({'success': False, 'message': 'You have already booked a seat for this day.'}), 400

    # 4. Book the seat
    df.at[idx, target_desk] = user_name
    save_data(df)
    
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
    
    df = read_data()
    
    # Check if booking exists
    if target_date not in df['Date'].values:
        return jsonify({'success': False, 'message': 'No booking found.'}), 404
    
    idx = df.index[df['Date'] == target_date].tolist()[0]
    current_occupant = df.at[idx, target_desk]
    
    # Check if the user owns this booking
    if pd.isna(current_occupant) or str(current_occupant).strip() == "":
        return jsonify({'success': False, 'message': 'No booking to cancel.'}), 404
    
    if current_occupant != user_name:
        return jsonify({'success': False, 'message': 'You can only cancel your own bookings.'}), 403
    
    # Cancel the booking
    df.at[idx, target_desk] = None
    save_data(df)
    
    return jsonify({'success': True})

@app.route('/api/download', methods=['GET'])
def download_schedule():
    """Download the Excel file with all bookings."""
    if not os.path.exists(EXCEL_FILE):
        init_excel()
    return send_file(EXCEL_FILE, as_attachment=True, download_name='office_seating.xlsx')

if __name__ == '__main__':
    init_excel()
    app.run(debug=False, host='127.0.0.1', port=5001)