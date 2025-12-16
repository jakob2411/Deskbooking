# Configuration Example for Office Desk Booking System

# You can create a config.py file to override default settings

# Server Configuration
HOST = '127.0.0.1'
PORT = 5001
DEBUG = False

# Excel File Configuration
EXCEL_FILE = 'office_seating.xlsx'

# Desk Names - Customize your desk names here!
DESK_NAMES = [
    'The Throne',
    'Procrastination Station',
    'Caffeine Corner',
    'Innovation Island',
    'Chaos Central'
]

# Holiday Configuration
# Available German regions: BW, BY, BE, BB, HB, HH, HE, MV, NI, NW, RP, SL, SN, ST, SH, TH
HOLIDAY_COUNTRY = 'Germany'
HOLIDAY_SUBDIV = 'BY'  # Bavaria

# Week Configuration
# How many weeks ahead to show for booking
WEEKS_AHEAD = 2

# Booking Rules
MAX_BOOKINGS_PER_DAY = 1  # Maximum bookings per user per day
ALLOW_CANCELLATION = True
