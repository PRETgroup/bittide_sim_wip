#!/usr/bin/env python3
"""
Debug helper script for bittide simulation
"""
import sys
import json
import traceback
from ParseConfig import load_nodes_from_config

def debug_config_parsing(config_path):
    """Debug configuration parsing step by step"""
    print(f"🔍 Debugging configuration parsing for: {config_path}")
    print("=" * 50)
    
    try:
        # Load and display config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Config loaded successfully")
        print(f"📋 Found {len(config.get('nodes', []))} nodes")
        print(f"📋 Found {len(config.get('links', []))} link groups")
        
        # Try to parse nodes and links
        print("\n🔧 Parsing nodes and links...")
        nodes, links = load_nodes_from_config(config_path, None)
        
        print(f"✅ Successfully parsed {len(nodes)} nodes")
        print(f"✅ Successfully parsed {len(links)} link groups")
        
        # Display node information
        print("\n📊 Node Details:")
        for node_id, node in nodes.items():
            print(f"  • {node_id}: freq={node.freq}Hz, buffers={len(node.buffers)}")
            if hasattr(node, 'controller') and node.controller:
                controller_type = type(node.controller).__name__
                print(f"    Controller: {controller_type}")
            
            # Display buffer information
            for buffer_name, buffer in node.buffers.items():
                print(f"    Buffer {buffer_name}: capacity={buffer.capacity}, initial={buffer.occupancy}")
        
        # Display link information
        print("\n🔗 Link Details:")
        for source_id, destinations in links.items():
            print(f"  From {source_id}:")
            for dest_id, link_settings in destinations.items():
                print(f"    → {dest_id}: delay_model={type(link_settings.delay_model).__name__}")
        
        return nodes, links
        
    except Exception as e:
        print(f"❌ Error during config parsing:")
        print(f"   {type(e).__name__}: {e}")
        print("\n📍 Traceback:")
        traceback.print_exc()
        return None, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_config.py <config_file>")
        print("Available configs:")
        import os
        config_files = [f for f in os.listdir('configs') if f.endswith('.json')]
        for cf in config_files:
            print(f"  - configs/{cf}")
        return
    
    config_path = sys.argv[1]
    debug_config_parsing(config_path)

if __name__ == "__main__":
    main()
