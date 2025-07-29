#!/usr/bin/env python3
"""
Debug helper for controller behavior
"""
import sys
import json
import numpy as np
from ParseConfig import load_nodes_from_config

def debug_controller_step(config_path, steps=10):
    """Debug controller behavior step by step"""
    print(f"🎮 Debugging controller behavior for: {config_path}")
    print("=" * 50)
    
    try:
        # Load configuration
        nodes, links = load_nodes_from_config(config_path, None)
        
        if not nodes:
            print("❌ Failed to load nodes")
            return
        
        # Find nodes with controllers
        controlled_nodes = []
        for node_id, node in nodes.items():
            if hasattr(node, 'controller') and node.controller:
                controlled_nodes.append((node_id, node))
                controller_type = type(node.controller).__name__
                print(f"📊 Found controller: {node_id} -> {controller_type}")
        
        if not controlled_nodes:
            print("❌ No controllers found in configuration")
            return
        
        print(f"\n🔄 Running {steps} controller steps...")
        
        for step in range(steps):
            print(f"\n--- Step {step + 1} ---")
            
            for node_id, node in controlled_nodes:
                try:
                    # Get current buffer states
                    buffer_states = {}
                    for buffer_name, buffer in node.buffers.items():
                        buffer_states[buffer_name] = buffer
                        print(f"  Buffer {buffer_name}: {buffer.get_occupancy_as_percent():.1f}%")
                    
                    # Run controller step
                    if hasattr(node.controller, 'step'):
                        result = node.controller.step(buffer_states)
                        print(f"  Controller {node_id} output: {result}")
                        
                        # If result has freq_correction, show it
                        if hasattr(result, 'freq_correction'):
                            print(f"    freq_correction: {result.freq_correction}")
                        if hasattr(result, 'do_tick'):
                            print(f"    do_tick: {result.do_tick}")
                    
                    # Simulate some buffer change
                    for buffer_name, buffer in node.buffers.items():
                        # Add small random change to simulate traffic
                        change = np.random.randint(-2, 3)
                        new_occ = max(0, min(buffer.capacity, buffer.occupancy + change))
                        buffer.occupancy = new_occ
                
                except Exception as e:
                    print(f"  ❌ Error in controller {node_id}: {e}")
        
    except Exception as e:
        print(f"❌ Error during controller debugging: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_controller.py <config_file> [steps]")
        return
    
    config_path = sys.argv[1]
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    debug_controller_step(config_path, steps)

if __name__ == "__main__":
    main()
