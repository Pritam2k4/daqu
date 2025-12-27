from supabase import create_client, Client
from app.config import settings

# Initialize Supabase client
supabase: Client = None

def get_supabase() -> Client:
    """Get Supabase client instance"""
    global supabase
    
    if supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env file")
        
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    return supabase

def test_connection():
    """Test Supabase connection"""
    try:
        client = get_supabase()
        # Try a simple query
        response = client.table('users').select('count', count='exact').execute()
        return True, f"Connected successfully. Users count: {response.count}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
