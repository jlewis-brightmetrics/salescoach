import os
from app import app

if __name__ == '__main__':
    # Replit sets PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    
    # Set Flask environment for Replit
    os.environ['FLASK_ENV'] = 'production'
    
    print(f"🚀 Starting Salescoach on Replit - Port {port}")
    print("📱 Make sure to set OPENAI_API_KEY in Replit Secrets!")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False,
        threaded=True
    ) 