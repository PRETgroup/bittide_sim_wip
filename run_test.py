#!/usr/bin/env python3
"""
Simple test runner for debugging
"""
import sys
import os

def run_test(config_name, duration=5.0):
    """Run a simple test with the given config"""
    config_path = f"configs/{config_name}"
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False
    
    print(f"🚀 Running test with {config_name} for {duration}s...")
    
    try:
        # Import and run
        import subprocess
        result = subprocess.run([
            sys.executable, "System.py", 
            "--conf", config_path,
            "--duration", str(duration)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Test completed successfully!")
            print("📊 Output:")
            print(result.stdout[-500:])  # Show last 500 chars
            return True
        else:
            print("❌ Test failed!")
            print("📊 Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out (30s limit)")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def list_configs():
    """List available configuration files"""
    configs = []
    if os.path.exists("configs"):
        for f in os.listdir("configs"):
            if f.endswith(".json"):
                configs.append(f)
    return configs

def main():
    print("🔧 Bittide Debug Test Runner")
    print("=" * 30)
    
    configs = list_configs()
    if not configs:
        print("❌ No config files found in configs/")
        return
    
    print("📋 Available configurations:")
    for i, config in enumerate(configs, 1):
        print(f"  {i}. {config}")
    
    if len(sys.argv) > 1:
        config_name = sys.argv[1]
        if not config_name.endswith('.json'):
            config_name += '.json'
    else:
        print("\n🔍 Select a configuration to test:")
        try:
            choice = int(input("Enter number: ")) - 1
            if 0 <= choice < len(configs):
                config_name = configs[choice]
            else:
                print("❌ Invalid choice")
                return
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Cancelled")
            return
    
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    
    success = run_test(config_name, duration)
    
    if success:
        print(f"\n🎉 Test with {config_name} completed successfully!")
    else:
        print(f"\n💥 Test with {config_name} failed!")
        print("\n🔍 Try debugging with:")
        print(f"   python debug_config.py configs/{config_name}")
        print(f"   python debug_controller.py configs/{config_name}")

if __name__ == "__main__":
    main()
