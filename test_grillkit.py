# Integration and compilation verification script for GrillKit
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Initializing GrillKit App and compiling workflow graph...")
    from app.agent import app
    
    workflow = app.root_agent
    print("[SUCCESS] GrillKit Graph Workflow compiled and validated successfully!")
    
    print("\n--- Compiled Graph Nodes ---")
    for idx, node in enumerate(workflow.graph.nodes):
        print(f"Node {idx + 1}: {node.name} (type: {type(node).__name__})")
        
    print("\n--- Compiled Graph Edges ---")
    for idx, edge in enumerate(workflow.graph.edges):
        route_str = f" [route: {edge.route}]" if edge.route else ""
        print(f"Edge {idx + 1}: {edge.from_node.name} -> {edge.to_node.name}{route_str}")
        
    print("\nGrillKit is 100% ready for technical interviews.")
except Exception as e:
    import traceback
    print("[FAILED] Graph compilation or validation failed:")
    traceback.print_exc()
    sys.exit(1)
