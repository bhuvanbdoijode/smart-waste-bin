import requests
import json
from datetime import datetime
from config import Config

class FirebaseService:
    def __init__(self):
        self.base_url = Config.FIREBASE_DATABASE_URL
        
    def _make_request(self, method, endpoint, data=None):
        """Helper method to make Firebase REST API requests"""
        url = f"{self.base_url}/{endpoint}.json"
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'PUT':
                response = requests.put(url, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url)
            
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.exceptions.RequestException as e:
            print(f"Firebase request error: {e}")
            return None
    
    def get_all_bins(self):
        """Retrieve all bins from Firebase"""
        data = self._make_request('GET', 'bins')
        if not data:
            return []
        
        bins = []
        for bin_id, bin_data in data.items():
            bin_data['id'] = bin_id
            bins.append(bin_data)
        
        return bins
    
    def get_bin(self, bin_id):
        """Get a specific bin by ID"""
        return self._make_request('GET', f'bins/{bin_id}')
    
    def add_bin(self, bin_data):
        """Add a new bin to Firebase"""
        bin_data['last_updated'] = datetime.now().isoformat()
        bin_data['fill_level'] = bin_data.get('fill_level', 0)
        
        result = self._make_request('POST', 'bins', bin_data)
        return result.get('name') if result else None
    
    def update_bin(self, bin_id, bin_data):
        """Update an existing bin"""
        bin_data['last_updated'] = datetime.now().isoformat()
        return self._make_request('PATCH', f'bins/{bin_id}', bin_data)
    
    def delete_bin(self, bin_id):
        """Delete a bin from Firebase"""
        return self._make_request('DELETE', f'bins/{bin_id}')
    
    def update_fill_level(self, bin_id, fill_level):
        """Update only the fill level of a bin"""
        data = {
            'fill_level': fill_level,
            'last_updated': datetime.now().isoformat()
        }
        return self._make_request('PATCH', f'bins/{bin_id}', data)
    
    def get_bin_statistics(self):
        """Calculate statistics for all bins"""
        bins = self.get_all_bins()
        
        stats = {
            'total': len(bins),
            'full': 0,
            'half': 0,
            'empty': 0
        }
        
        for bin_data in bins:
            level = bin_data.get('fill_level', 0)
            if level >= 80:
                stats['full'] += 1
            elif level >= 50:
                stats['half'] += 1
            else:
                stats['empty'] += 1
        
        return stats

def save_admin_fcm_token(token: str):
    # Store admin FCM token using REST API
    firebase_service._make_request('PUT', 'fcm_tokens/admin', token)

def get_admin_fcm_token():
    # Retrieve admin FCM token using REST API
    return firebase_service._make_request('GET', 'fcm_tokens/admin')

def send_bin_full_notification(bin_id: str, fill_level: int):
    # from firebase_admin import messaging  # Uncomment if firebase_admin is installed and configured

    token = get_admin_fcm_token()
    if not token:
        print("No admin FCM token stored, skipping FCM send.")
        return

    try:
        from firebase_admin import messaging
    except ImportError:
        print("firebase_admin.messaging is not available. FCM notification not sent.")
        return

    message = messaging.Message(
        notification=messaging.Notification(
            title="Smart Waste Bin Alert",
            body=f"Bin {bin_id} is {fill_level}% full.",
        ),
        token=token,
    )

    try:
        response = messaging.send(message)
        print("Successfully sent FCM message:", response)
    except Exception as e:
        print("Error sending FCM message:", e)

# Create a singleton instance
firebase_service = FirebaseService()

def update_bin_fill(bin_id, fill_level):
    firebase_service.update_fill_level(bin_id, fill_level)
