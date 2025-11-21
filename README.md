# Smart Waste Bin Monitoring System

A complete full-stack web application for monitoring waste bins in real-time using Flask, Firebase, and Bootstrap.

## Features

- **User Authentication**: Admin and Housekeeping roles with Flask-Login
- **Real-time Dashboard**: Auto-refreshing every 3 seconds with live statistics
- **Admin Panel**: Add, edit, and delete bins
- **Firebase Integration**: Cloud-based real-time database
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Color-coded Status**: Visual indicators for bin fill levels

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: Firebase Realtime Database
- **Authentication**: Flask-Login (session-based)

## Project Structure

```
smart-waste-bin/
│
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── firebase_service.py     # Firebase integration
├── models.py               # User authentication models
├── requirements.txt        # Python dependencies
│
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       ├── dashboard.js   # Dashboard logic
│       └── admin.js       # Admin panel logic
│
└── templates/
    ├── base.html          # Base template
    ├── login.html         # Login page
    ├── dashboard.html     # Main dashboard
    ├── add_bin.html       # Add bin form
    └── edit_bin.html      # Edit bin form
```

## Installation & Setup

### 1. Clone or Create Project Directory

```bash
mkdir smart-waste-bin
cd smart-waste-bin
```

### 2. Create the folder structure

```bash
mkdir -p static/css static/js templates
```

### 3. Copy all the files to their respective locations

- Copy Python files to the root directory
- Copy HTML files to the `templates/` folder
- Copy CSS files to the `static/css/` folder
- Copy JS files to the `static/js/` folder

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use an existing one
3. Navigate to **Realtime Database** and create a database
4. Set security rules to allow read/write (for development):

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

**Note**: For production, implement proper security rules!

5. Copy your Firebase Database URL (looks like: `https://your-project.firebaseio.com`)

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here-change-this
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
```

### 7. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Login Credentials

- **Admin Account**:
  - Username: `admin`
  - Password: `admin123`
  
- **Housekeeping Account**:
  - Username: `housekeeping`
  - Password: `house123`

### Dashboard Features

- View all bins with real-time updates
- Color-coded status indicators:
  - 🔴 **Red (Full)**: Fill level ≥ 80%
  - 🟡 **Yellow (Half Full)**: Fill level 50-79%
  - 🟢 **Green (Empty)**: Fill level < 50%
- Statistics cards showing total, full, half-full, and empty bins

### Admin Features

- **Add Bin**: Create new waste bin entries
- **Edit Bin**: Update bin information and fill levels
- **Delete Bin**: Remove bins from the system

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET/POST | `/login` | User login | No |
| GET | `/logout` | User logout | Yes |
| GET | `/dashboard` | Main dashboard | Yes |
| GET/POST | `/bins/add` | Add new bin | Admin only |
| GET/POST | `/bins/edit/<id>` | Edit bin | Admin only |
| POST | `/bins/delete/<id>` | Delete bin | Admin only |
| GET | `/api/bins` | Get all bins (JSON) | Yes |

## Firebase Data Structure

```json
{
  "bins": {
    "bin_id_1": {
      "location": "Building A - Floor 1",
      "type": "General",
      "capacity": 100,
      "fill_level": 45,
      "last_updated": "2025-11-21T10:30:00"
    },
    "bin_id_2": {
      "location": "Building B - Cafeteria",
      "type": "Recyclable",
      "capacity": 150,
      "fill_level": 85,
      "last_updated": "2025-11-21T10:35:00"
    }
  }
}
```

## Customization

### Changing Auto-refresh Interval

Edit `templates/dashboard.html`:

```javascript
// Change 3000 to desired milliseconds (e.g., 5000 for 5 seconds)
refreshInterval = setInterval(loadBinsData, 3000);
```

### Adding New User Accounts

Edit `models.py`:

```python
USERS = {
    'newuser': {
        'password': 'newpassword',
        'role': 'admin'  # or 'housekeeping'
    }
}
```

### Modifying Fill Level Thresholds

Edit `firebase_service.py` in the `get_bin_statistics` method:

```python
if level >= 80:  # Change threshold here
    stats['full'] += 1
```

## Production Deployment

### Security Recommendations

1. **Change default credentials** in `models.py`
2. **Use strong SECRET_KEY** in environment variables
3. **Implement proper Firebase security rules**
4. **Enable HTTPS** and set `SESSION_COOKIE_SECURE = True`
5. **Use a production WSGI server** (Gunicorn, uWSGI)

### Example Production Command

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Firebase Connection Issues

- Verify your Firebase URL is correct
- Check Firebase security rules
- Ensure internet connectivity

### Auto-refresh Not Working

- Check browser console for errors
- Verify `/api/bins` endpoint returns valid JSON
- Check if JavaScript is enabled

### Login Issues

- Verify credentials match those in `models.py`
- Check if session cookies are enabled
- Clear browser cache and cookies

## Future Enhancements

- IoT sensor integration for automatic fill level updates
- Email/SMS notifications for full bins
- Historical data analytics and reporting
- Mobile app version
- Map view of bin locations
- Route optimization for collection

## License

This project is open-source and available for educational and commercial use.

## Support

For issues or questions, please review the code comments for detailed explanations.