#!/usr/bin/env python3
"""
Startup script for CrewAI Automation Pipeline
This script handles setup verification and graceful startup
"""

import os
import sys
import subprocess
import time

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def run_tests():
    """Run setup tests"""
    print("\nRunning setup tests...")
    try:
        from test_setup import run_all_tests
        return run_all_tests()
    except ImportError:
        print("❌ test_setup.py not found")
        return False

def start_pipeline():
    """Start the main pipeline"""
    print("\nStarting CrewAI pipeline...")
    try:
        import main
        main.main()
    except KeyboardInterrupt:
        print("\n\n🛑 Pipeline stopped by user")
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        print("Check pipeline.log for details")

def main():
    """Main startup sequence"""
    print("=" * 60)
    print("CREWAI AUTOMATION PIPELINE STARTUP")
    print("=" * 60)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("\n❌ Setup failed at requirements installation")
        sys.exit(1)
    
    # Step 2: Run tests
    if not run_tests():
        print("\n❌ Setup tests failed. Please fix the issues before continuing.")
        response = input("\nDo you want to start anyway? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    
    # Step 3: Start pipeline
    print("\n" + "=" * 60)
    print("STARTING PIPELINE IN 5 SECONDS...")
    print("Press Ctrl+C to cancel")
    print("=" * 60)
    
    try:
        for i in range(5, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        
        start_pipeline()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Startup cancelled by user")

if __name__ == "__main__":
    main()