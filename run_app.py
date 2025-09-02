#!/usr/bin/env python3
"""
Launcher script for the Drug-Target Graph Database Streamlit app
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    print("🚀 Launching Drug-Target Graph Database...")
    print("📱 Opening Streamlit app in your browser...")
    print("🔗 The app will be available at: http://localhost:8501")
    print("\n💡 Tips:")
    print("- Make sure Neo4j Desktop is running")
    print("- Your database should be started")
    print("- Use the sidebar to configure connection if needed")
    print("\n⏹️  Press Ctrl+C to stop the app")
    
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Install requirements: pip install -r requirements.txt")
        print("3. Check that Neo4j is running")

if __name__ == "__main__":
    main()
