#!/usr/bin/env python3
"""
Simple launcher for ERESUS F429 Multi-Agent Testing System
"""

import sys
import os
from test_agents import TestCoordinator

def main():
    print("🚀 ERESUS F429 Firmware Testing Launcher")
    print("="*50)
    
    # Get port from user or use default
    port = input("Enter COM port (default: COM3): ").strip() or "COM3"
    
    # Create coordinator
    coordinator = TestCoordinator(port=port)
    
    # Connect and test
    if coordinator.connect():
        print(f"✅ Connected to {port}")
        results = coordinator.run_all_tests()
        coordinator.print_summary(results)
    else:
        print(f"❌ Failed to connect to {port}")
        print("💡 Try different COM port or check USB connection")

if __name__ == "__main__":
    main()
