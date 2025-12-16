# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup

**Linux/Mac:**
```bash
./scripts/setup.sh
```

**Windows:**
```cmd
scripts\setup.bat
```

**Manual Setup:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Run

```bash
python src/app.py
```

### Step 3: Open Browser

Navigate to: **http://127.0.0.1:5001**

---

## 📖 Basic Usage

### Booking a Desk

1. **Enter your name** in the input field at the top
2. **Click on any available desk** (shown in gray)
3. Your booking appears in **green** with "You"

### Canceling a Booking

1. **Hover over your booking** (green desk)
2. The desk turns **red** and shows "Click to Cancel"
3. **Click** to cancel

### Downloading Schedule

Click the **"📥 Download Schedule"** button to export all bookings as Excel

---

## 🎨 Visual Guide

**Desk Colors:**
- **Gray** - Available desk (click to book)
- **Green** - Your booking (hover to cancel)
- **Red** - Booked by someone else (shows their name)

---

## ⚙️ Customization

Edit `src/app.py` to customize:

**Change desk names:**
```python
df = pd.DataFrame(columns=['Date', 'Your Desk Name 1', 'Your Desk Name 2', ...])
```

**Change holiday region:**
```python
BAVARIAN_HOLIDAYS = holidays.Germany(subdiv='BY')  # Change 'BY' to your region
```

**Available regions:** BW, BY, BE, BB, HB, HH, HE, MV, NI, NW, RP, SL, SN, ST, SH, TH

---

## 🐛 Troubleshooting

**Port already in use?**
- macOS uses port 5000 for AirPlay
- App uses port 5001 by default
- To change: Edit `src/app.py` line `app.run(debug=False, host='127.0.0.1', port=YOUR_PORT)`

**Can't create Excel file?**
- Check write permissions in the app directory
- File is created automatically on first run

**Dependencies not installing?**
- Ensure Python 3.13+ is installed: `python3 --version`
- Upgrade pip: `pip install --upgrade pip`

---

## 📚 More Help

- See [README.md](README.md) for full documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Open an issue on GitHub for support
