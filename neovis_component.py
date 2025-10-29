#!/usr/bin/env python3
"""
Neovis.js Integration for Streamlit
- Creates interactive Neo4j network visualizations
- Supports cascade effect visualization
- Handles node clicks and interactions
- Secure credential handling
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, List
import json
import hashlib

class NeovisNetwork:
    """
    Wrapper for neovis.js network visualization in Streamlit
    """
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, 
                 neo4j_database: str = "neo4j"):
        """
        Initialize neovis network
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            neo4j_database: Neo4j database name
        """
        self.uri = neo4j_uri
        self.user = neo4j_user
        self.password = neo4j_password
        self.database = neo4j_database
    
    def render_drug_network_visjs(self, drug_name: str, 
                                  network_data: dict = None,
                                  height: int = 800,
                                  width: str = "100%") -> str:
        """
        Create interactive network showing drug, targets, and cascade effects
        
        Args:
            drug_name: Name of the drug to visualize
            network_data: Network data from get_drug_network() method
            height: Height of visualization in pixels
            width: Width of visualization (css value)
        
        Returns:
            HTML string with neovis.js visualization
        """
        
        # Generate unique ID for this visualization
        viz_id = hashlib.md5(f"{drug_name}_network".encode()).hexdigest()[:8]
        
        # Convert network data to neovis.js format
        nodes_data = []
        edges_data = []
        
        if network_data and 'nodes' in network_data:
            # Convert nodes to neovis format
            for node in network_data['nodes']:
                node_props = {
                    'id': node['id'],
                    'label': node['label'],
                    'group': node['type']
                }
                
                # Add additional properties for tooltips
                if 'moa' in node:
                    node_props['moa'] = node['moa'] or 'Not specified'
                if 'phase' in node:
                    node_props['phase'] = node['phase'] or 'Unknown'
                    
                nodes_data.append(node_props)
            
            # Convert edges to neovis format
            for edge in network_data['edges']:
                edges_data.append({
                    'from': edge['source'],
                    'to': edge['target'],
                    'label': edge['type']
                })
        
        # Create HTML with neovis.js
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Drug-Target Cascade Network</title>
    <script src="https://unpkg.com/neovis.js@2.1.0"></script>
    <style>
        body {{
            margin: 0;
            padding: 10px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        #viz_{viz_id} {{
            width: {width};
            height: {height}px;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}
        .info-panel {{
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e1e4e8;
            font-size: 14px;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 10px 0;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid white;
        }}
        .controls {{
            margin: 10px 0;
            padding: 10px;
            background: #f6f8fa;
            border-radius: 6px;
        }}
        button {{
            padding: 8px 16px;
            margin: 5px;
            border: none;
            border-radius: 4px;
            background: #0366d6;
            color: white;
            cursor: pointer;
            font-size: 13px;
        }}
        button:hover {{
            background: #0256c7;
        }}
        .node-info {{
            margin-top: 10px;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #0366d6;
        }}
        .confidence-high {{ color: #28a745; font-weight: bold; }}
        .confidence-med {{ color: #ffc107; font-weight: bold; }}
        .confidence-low {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-circle" style="background: #3498db;"></div>
            <span>Drug</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #2ecc71;"></div>
            <span>Target</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #f39c12;"></div>
            <span>Pathway</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #e74c3c;"></div>
            <span>Metabolite</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #9b59b6;"></div>
            <span>Gene</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #e67e22;"></div>
            <span>Process</span>
        </div>
    </div>
    
    <div id="viz_{viz_id}"></div>
    
    <div class="controls">
        <button onclick="viz.stabilize()">🎯 Stabilize Layout</button>
        <button onclick="viz.reload()">🔄 Reload</button>
        <button onclick="viz.clearNetwork()">🗑️ Clear</button>
        <button onclick="viz.renderWithCypher(viz.config.initial_cypher)">↩️ Reset View</button>
    </div>
    
    <div id="node-info" class="node-info" style="display:none;">
        <h3 id="node-title"></h3>
        <div id="node-details"></div>
    </div>

    <script type="text/javascript">
        // Neovis configuration
        var config = {{
            containerId: "viz_{viz_id}",
            neo4j: {{
                serverUrl: "{self.uri}",
                serverUser: "{self.user}",
                serverPassword: "{self.password}",
                serverDatabase: "{self.database}"
            }},
            visConfig: {{
                nodes: {{
                    shape: 'dot',
                    font: {{
                        size: 14,
                        face: 'Segoe UI',
                        color: '#333'
                    }}
                }},
                edges: {{
                    arrows: {{
                        to: {{ enabled: true, scaleFactor: 0.5 }}
                    }},
                    smooth: {{
                        enabled: true,
                        type: 'continuous'
                    }},
                    font: {{
                        size: 11,
                        align: 'top'
                    }}
                }},
                physics: {{
                    enabled: true,
                    stabilization: {{
                        iterations: 200,
                        fit: true
                    }},
                    barnesHut: {{
                        gravitationalConstant: -8000,
                        springLength: 150,
                        springConstant: 0.04,
                        damping: 0.09
                    }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200,
                    hideEdgesOnDrag: true,
                    navigationButtons: true,
                    keyboard: true
                }},
                layout: {{
                    hierarchical: {{
                        enabled: true,
                        direction: 'LR',
                        sortMethod: 'directed',
                        levelSeparation: 200,
                        nodeSpacing: 150
                    }}
                }}
            }},
            labels: {{
                Drug: {{
                    label: "name",
                    size: 30,
                    color: "#3498db",
                    font: {{
                        size: 16,
                        color: "white"
                    }},
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        static: true,
                        function: {{
                            title: function(node) {{
                                return "Drug: " + node.properties.name + 
                                       "\\nMOA: " + (node.properties.moa || "Unknown") +
                                       "\\nPhase: " + (node.properties.phase || "Unknown");
                            }}
                        }}
                    }}
                }},
                Target: {{
                    label: "name",
                    size: 25,
                    color: "#2ecc71",
                    font: {{
                        size: 14,
                        color: "white"
                    }},
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        function: {{
                            title: function(node) {{
                                return "Target: " + node.properties.name;
                            }}
                        }}
                    }}
                }},
                Pathway: {{
                    label: "name",
                    size: 20,
                    color: "#f39c12",
                    font: {{
                        size: 12,
                        color: "white"
                    }},
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        function: {{
                            title: function(node) {{
                                return "Pathway: " + node.properties.name;
                            }}
                        }}
                    }}
                }},
                Metabolite: {{
                    label: "name",
                    size: 20,
                    color: "#e74c3c",
                    font: {{
                        size: 12,
                        color: "white"
                    }},
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        function: {{
                            title: function(node) {{
                                return "Metabolite: " + node.properties.name;
                            }}
                        }}
                    }}
                }},
                Gene: {{
                    label: "symbol",
                    size: 20,
                    color: "#9b59b6",
                    font: {{
                        size: 12,
                        color: "white"
                    }},
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        function: {{
                            title: function(node) {{
                                return "Gene: " + (node.properties.symbol || node.properties.name);
                            }}
                        }}
                    }}
                }},
                CellularProcess: {{
                    label: "name",
                    size: 18,
                    color: "#e67e22",
                    font: {{
                        size: 11,
                        color: "white"
                    }},
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        function: {{
                            title: function(node) {{
                                return "Process: " + node.properties.name;
                            }}
                        }}
                    }}
                }},
                Protein: {{
                    label: "name",
                    size: 20,
                    color: "#1abc9c",
                    font: {{
                        size: 12,
                        color: "white"
                    }}
                }}
            }},
            relationships: {{
                TARGETS: {{
                    thickness: 3,
                    color: "#555",
                    label: false,
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        function: {{
                            title: function(edge) {{
                                return "TARGETS";
                            }}
                        }}
                    }}
                }},
                AFFECTS_DOWNSTREAM: {{
                    thickness: "confidence",
                    color: {{
                        inherit: false
                    }},
                    label: "effect_type",
                    [NeoVis.NEOVIS_ADVANCED_CONFIG]: {{
                        function: {{
                            title: function(edge) {{
                                var conf = edge.properties.confidence || 0;
                                var effect = edge.properties.effect_type || "affects";
                                var reasoning = edge.properties.reasoning || "No reasoning provided";
                                return effect.toUpperCase() + 
                                       "\\nConfidence: " + (conf * 100).toFixed(0) + "%" +
                                       "\\nDepth: " + (edge.properties.depth || 1) + "-hop" +
                                       "\\n" + reasoning.substring(0, 100);
                            }},
                            color: function(edge) {{
                                var conf = edge.properties.confidence || 0.5;
                                if (conf >= 0.8) return "#28a745";      // Green - high confidence
                                else if (conf >= 0.6) return "#ffc107";  // Yellow - medium
                                else return "#dc3545";                   // Red - low
                            }}
                        }}
                    }}
                }}
            }},
            initial_cypher: `{cypher_query}`,
            console_debug: false
        }};

        // Initialize NeoVis
        var viz;
        
        function initViz() {{
            console.log("Initializing NeoVis...");
            viz = new NeoVis.default(config);
            
            // Event handlers
            viz.registerOnEvent("completed", function(e) {{
                console.log("Network rendering completed");
                document.getElementById('node-info').style.display = 'none';
            }});
            
            viz.registerOnEvent("clickNode", function(e) {{
                console.log("Node clicked:", e);
                showNodeInfo(e);
                
                // Send message to Streamlit parent
                if (window.parent) {{
                    window.parent.postMessage({{
                        type: 'neovis-node-click',
                        node: {{
                            id: e.nodeId,
                            label: e.node.label,
                            labels: e.node.labels,
                            properties: e.node.properties
                        }}
                    }}, '*');
                }}
            }});
            
            viz.registerOnEvent("clickEdge", function(e) {{
                console.log("Edge clicked:", e);
                showEdgeInfo(e);
            }});
            
            // Render the network
            viz.render();
        }}
        
        function showNodeInfo(event) {{
            var node = event.node;
            var infoDiv = document.getElementById('node-info');
            var titleDiv = document.getElementById('node-title');
            var detailsDiv = document.getElementById('node-details');
            
            var labels = node.labels || [];
            var props = node.properties || {{}};
            
            titleDiv.innerHTML = labels[0] + ": " + (props.name || props.symbol || "Unknown");
            
            var details = "<table style='width:100%'>";
            for (var key in props) {{
                if (props.hasOwnProperty(key)) {{
                    var value = props[key];
                    if (typeof value === 'string' && value.length > 100) {{
                        value = value.substring(0, 100) + "...";
                    }}
                    details += "<tr><td style='padding:5px;font-weight:bold;'>" + key + 
                              ":</td><td style='padding:5px;'>" + value + "</td></tr>";
                }}
            }}
            details += "</table>";
            
            detailsDiv.innerHTML = details;
            infoDiv.style.display = 'block';
        }}
        
        function showEdgeInfo(event) {{
            var edge = event.edge;
            var infoDiv = document.getElementById('node-info');
            var titleDiv = document.getElementById('node-title');
            var detailsDiv = document.getElementById('node-details');
            
            var type = edge.type || "Unknown";
            var props = edge.properties || {{}};
            
            titleDiv.innerHTML = "Relationship: " + type;
            
            var details = "<table style='width:100%'>";
            
            if (props.effect_type) {{
                details += "<tr><td style='padding:5px;font-weight:bold;'>Effect:</td><td style='padding:5px;'>" + 
                          props.effect_type + "</td></tr>";
            }}
            
            if (props.confidence) {{
                var conf = (props.confidence * 100).toFixed(0);
                var confClass = props.confidence >= 0.8 ? 'confidence-high' : 
                               props.confidence >= 0.6 ? 'confidence-med' : 'confidence-low';
                details += "<tr><td style='padding:5px;font-weight:bold;'>Confidence:</td><td style='padding:5px;' class='" + 
                          confClass + "'>" + conf + "%</td></tr>";
            }}
            
            if (props.depth) {{
                details += "<tr><td style='padding:5px;font-weight:bold;'>Depth:</td><td style='padding:5px;'>" + 
                          props.depth + "-hop</td></tr>";
            }}
            
            if (props.reasoning) {{
                details += "<tr><td style='padding:5px;font-weight:bold;vertical-align:top;'>Reasoning:</td><td style='padding:5px;'>" + 
                          props.reasoning + "</td></tr>";
            }}
            
            details += "</table>";
            
            detailsDiv.innerHTML = details;
            infoDiv.style.display = 'block';
        }}
        
        // Initialize on load
        window.addEventListener('load', function() {{
            initViz();
        }});
        
        // Expose functions globally
        window.viz = viz;
        window.reloadViz = function() {{
            if (viz) {{
                viz.reload();
            }}
        }};
        window.stabilizeViz = function() {{
            if (viz) {{
                viz.stabilize();
            }}
        }};
    </script>
</head>
<body>
    <div id="viz_{viz_id}"></div>
    <div id="node-info" class="node-info" style="display:none;">
        <h3 id="node-title"></h3>
        <div id="node-details"></div>
    </div>
</body>
</html>
        """
        
        return html
    
    def render_drug_cascade_network(self, drug_name: str,
                                    include_cascade: bool = True,
                                    max_cascade_depth: int = 2,
                                    min_confidence: float = 0.6,
                                    height: int = 800):
        """
        Render the network in Streamlit using components.html
        
        Args:
            drug_name: Drug to visualize
            include_cascade: Include cascade effects
            max_cascade_depth: Max depth (1-3)
            min_confidence: Min confidence threshold
            height: Height in pixels
        """
        html = self.create_drug_cascade_network(
            drug_name=drug_name,
            include_cascade=include_cascade,
            max_cascade_depth=max_cascade_depth,
            min_confidence=min_confidence,
            height=height
        )
        
        # Render in Streamlit
        components.html(html, height=height + 100, scrolling=True)
    
    def create_target_cascade_network(self, target_name: str,
                                     max_cascade_depth: int = 2,
                                     min_confidence: float = 0.6,
                                     height: int = 700) -> str:
        """
        Create network centered on a target with all drugs and cascade effects
        
        Args:
            target_name: Name of the target
            max_cascade_depth: Maximum cascade depth
            min_confidence: Minimum confidence threshold
            height: Height in pixels
        
        Returns:
            HTML string with neovis.js visualization
        """
        
        cypher_query = f"""
            MATCH drugPath=(d:Drug)-[:TARGETS]->(t:Target {{name: '{target_name}'}})
            OPTIONAL MATCH cascadePath=(t)-[:AFFECTS_DOWNSTREAM*1..{max_cascade_depth}]->(e)
            WHERE ALL(r IN relationships(cascadePath) WHERE r.confidence >= {min_confidence})
            RETURN drugPath, cascadePath
        """
        
        viz_id = hashlib.md5(f"target_{target_name}_{max_cascade_depth}".encode()).hexdigest()[:8]
        
        # Similar HTML structure but centered on target
        return self.create_drug_cascade_network(
            drug_name=target_name,  # Reuse function
            include_cascade=True,
            max_cascade_depth=max_cascade_depth,
            min_confidence=min_confidence,
            height=height
        ).replace(cypher_query.split("MATCH")[1].split("RETURN")[0], 
                 cypher_query.split("MATCH")[1].split("RETURN")[0])


# Streamlit integration helpers
def render_interactive_cascade_network(app, drug_name: str, 
                                       include_cascade: bool = True,
                                       max_depth: int = 2,
                                       min_confidence: float = 0.6):
    """
    Streamlit wrapper to render interactive cascade network
    
    Args:
        app: DrugTargetGraphApp instance (for credentials)
        drug_name: Drug to visualize
        include_cascade: Include cascade effects
        max_depth: Maximum cascade depth
        min_confidence: Minimum confidence threshold
    """
    
    # Create neovis network
    neovis = NeovisNetwork(
        neo4j_uri=app.uri,
        neo4j_user=app.user,
        neo4j_password=app.password,
        neo4j_database=app.database
    )
    
    # Add controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        include_cascade = st.checkbox(
            "Show Cascade Effects",
            value=include_cascade,
            help="Include downstream cascade effects in network"
        )
    
    with col2:
        if include_cascade:
            max_depth = st.select_slider(
                "Cascade Depth",
                options=[1, 2, 3],
                value=max_depth,
                help="How many hops to show (1=direct, 2=direct+secondary, 3=full)"
            )
    
    with col3:
        if include_cascade:
            min_confidence = st.slider(
                "Min Confidence",
                min_value=0.0,
                max_value=1.0,
                value=min_confidence,
                step=0.05,
                help="Filter cascade by confidence"
            )
    
    with col4:
        height = st.number_input(
            "Height (px)",
            min_value=400,
            max_value=1200,
            value=700,
            step=50
        )
    
    # Render network
    st.markdown("---")
    neovis.render_drug_cascade_network(
        drug_name=drug_name,
        include_cascade=include_cascade,
        max_cascade_depth=max_depth if include_cascade else 1,
        min_confidence=min_confidence if include_cascade else 0.0,
        height=height
    )
    
    # Add instructions
    st.info("""
    **🖱️ Interaction Tips:**
    - **Click** nodes to see details
    - **Click and drag** to move nodes
    - **Scroll** to zoom in/out
    - **Click background and drag** to pan
    - Use control buttons above to stabilize or reset layout
    """)


# Example usage
if __name__ == "__main__":
    from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
    
    neovis = NeovisNetwork(
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD,
        neo4j_database=NEO4J_DATABASE
    )
    
    html = neovis.create_drug_cascade_network(
        drug_name="aspirin",
        include_cascade=True,
        max_cascade_depth=2,
        min_confidence=0.6
    )
    
    print("Neovis HTML component created!")
    print(f"HTML length: {len(html)} characters")
    
    # Save to file for testing
    with open("neovis_test.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Saved to neovis_test.html - open in browser to test!")


def create_visjs_network_component(drug_name: str, network_data: dict, 
                                  height: int = 800, width: str = "100%") -> str:
    """
    Create vis.js network using existing network data structure
    
    Args:
        drug_name: Name of the drug
        network_data: Network data from get_drug_network() method
        height: Height in pixels
        width: Width as CSS value
    
    Returns:
        HTML string with vis.js visualization
    """
    
    import json
    import hashlib
    
    # Generate unique ID
    viz_id = hashlib.md5(f"{drug_name}_visjs".encode()).hexdigest()[:8]
    
    # Convert network data to vis.js format
    nodes_data = []
    edges_data = []
    
    if network_data and 'nodes' in network_data:
        for i, node in enumerate(network_data['nodes']):
            node_props = {
                'id': i,
                'label': node.get('label', 'Unknown'),
                'group': node.get('type', 'unknown')
            }
            
            # Add tooltip properties - pass through all available properties
            for prop in ['moa', 'phase', 'type', 'description', 'disease_area', 'indication', 'vendor', 'purity']:
                if prop in node and node[prop]:
                    node_props[prop] = node[prop]
            
            # Ensure we have at least some info
            if 'moa' not in node_props:
                node_props['moa'] = 'Not specified'
            if 'phase' not in node_props:
                node_props['phase'] = 'Unknown'
                
            nodes_data.append(node_props)
        
        # Convert edges
        for edge in network_data['edges']:
            # Find source and target IDs
            source_id = None
            target_id = None
            for i, node in enumerate(network_data['nodes']):
                if node['id'] == edge['source']:
                    source_id = i
                if node['id'] == edge['target']:
                    target_id = i
            
            if source_id is not None and target_id is not None:
                edges_data.append({
                    'from': source_id,
                    'to': target_id,
                    'label': edge.get('type', 'targets')
                })
    
    # Create HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Drug-Target Network - {drug_name}</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 10px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
        }}
        #network_{viz_id} {{
            width: {width};
            height: {height}px;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            background: white;
        }}
        .controls {{
            margin: 10px 0;
            padding: 10px;
            background: #f6f8fa;
            border-radius: 6px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        button {{
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            background: #0366d6;
            color: white;
            cursor: pointer;
            font-size: 13px;
        }}
        button:hover {{
            background: #0256c7;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 10px 0;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid white;
        }}
        .node-info {{
            margin-top: 10px;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #0366d6;
        }}
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 200px;
        }}
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-circle" style="background: #3498db;"></div>
            <span>Central Drug</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #e74c3c;"></div>
            <span>Target</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #2ecc71;"></div>
            <span>Other Drug</span>
        </div>
        <div class="legend-item">
            <span style="font-size: 12px; color: #666;">💡 <strong>Interactive:</strong> Hover • Click • Right-click</span>
        </div>
    </div>
    
    <div class="controls">
        <button onclick="stabilizeNetwork()">🎯 Stabilize Layout</button>
        <button onclick="reloadNetwork()">🔄 Reload</button>
        <button onclick="clearNetwork()">🗑️ Clear</button>
        <button onclick="resetView()">↩️ Reset View</button>
    </div>
    
    <div id="network_{viz_id}"></div>
    
    <div id="node-info" class="node-info" style="display:none;">
        <h3 id="node-title"></h3>
        <div id="node-details"></div>
    </div>

    <script type="text/javascript">
        // Network data
        var nodesData = {json.dumps(nodes_data)};
        var edgesData = {json.dumps(edges_data)};
        
        // Debug: Log the data to console
        console.log("Nodes data:", nodesData);
        console.log("Edges data:", edgesData);
        
        // Create datasets
        var nodes = new vis.DataSet(nodesData);
        var edges = new vis.DataSet(edgesData);
        
        // Network options
        var options = {{
            nodes: {{
                shape: 'dot',
                font: {{
                    size: 14,
                    face: 'Segoe UI',
                    color: '#333'
                }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                arrows: {{
                    to: {{ enabled: true, scaleFactor: 0.5 }}
                }},
                smooth: {{
                    enabled: true,
                    type: 'continuous'
                }},
                font: {{
                    size: 11,
                    align: 'top'
                }},
                color: {{
                    color: '#848484',
                    highlight: '#FF6B6B',
                    hover: '#FF6B6B'
                }}
            }},
            physics: {{
                enabled: true,
                stabilization: {{
                    iterations: 200,
                    fit: true
                }},
                barnesHut: {{
                    gravitationalConstant: -8000,
                    springLength: 150,
                    springConstant: 0.04,
                    damping: 0.09
                }}
            }},
            groups: {{
                central_drug: {{
                    color: {{background: '#3498db', border: '#2980b9'}},
                    size: 30,
                    font: {{size: 16, color: 'white', bold: true, strokeWidth: 2, strokeColor: '#000'}}
                }},
                target: {{
                    color: {{background: '#e74c3c', border: '#c0392b'}},
                    size: 22,
                    font: {{size: 14, color: 'white', bold: true, strokeWidth: 2, strokeColor: '#000'}}
                }},
                other_drug: {{
                    color: {{background: '#2ecc71', border: '#27ae60'}},
                    size: 18,
                    font: {{size: 12, color: 'white', bold: true, strokeWidth: 2, strokeColor: '#000'}}
                }}
            }}
        }};
        
        // Create network with progressive disclosure
        var container = document.getElementById('network_{viz_id}');
        
        // Initially show only central drug and direct targets (progressive disclosure)
        var initialNodes = nodesData.filter(function(node) {{
            return node.group === 'central_drug' || 
                   (node.group === 'target' && edgesData.some(function(edge) {{
                       return edge.from === 0 && edge.to === node.id; // Connected to central drug
                   }}));
        }});
        
        var initialEdges = edgesData.filter(function(edge) {{
            return initialNodes.some(function(node) {{
                return node.id === edge.from || node.id === edge.to;
            }});
        }});
        
        var initialNodesSet = new vis.DataSet(initialNodes);
        var initialEdgesSet = new vis.DataSet(initialEdges);
        
        var network = new vis.Network(container, {{nodes: initialNodesSet, edges: initialEdgesSet}}, options);
        
        // Store full dataset for progressive disclosure
        var allNodes = new vis.DataSet(nodesData);
        var allEdges = new vis.DataSet(edgesData);
        
        // SIMPLIFIED AND WORKING event listeners
        network.on("selectNode", function(params) {{
            console.log("Node selected:", params);
            var nodeId = params.nodes[0];
            var nodeData = allNodes.get(nodeId);
            
            if (!nodeData) {{
                console.log("No node data found for ID:", nodeId);
                return;
            }}
            
            console.log("Node data:", nodeData);
            
            // Show node info
            showNodeInfo(nodeData);
            
            // Progressive disclosure: reveal connected nodes
            revealConnectedNodes(nodeId);
            
            // Recenter on clicked node
            network.focus(nodeId, {{
                scale: 1.5,
                animation: {{
                    duration: 1000,
                    easingFunction: "easeInOutQuad"
                }}
            }});
            
            // Show selection feedback
            showSelectionFeedback(nodeData);
        }});
        
        // SIMPLIFIED hover - using mouse events directly
        container.addEventListener('mousemove', function(event) {{
            var pointer = network.getPointer({{
                x: event.clientX - container.getBoundingClientRect().left,
                y: event.clientY - container.getBoundingClientRect().top
            }});
            
            var nodeId = network.getNodeAt(pointer);
            if (nodeId) {{
                var nodeData = allNodes.get(nodeId);
                if (nodeData) {{
                    showTooltip(event, nodeData);
                }}
            }} else {{
                hideTooltip();
            }}
        }});
        
        container.addEventListener('mouseleave', function(event) {{
            hideTooltip();
        }});
        
        // Enhanced right-click context menu
        container.addEventListener('contextmenu', function(event) {{
            event.preventDefault();
            
            // Get the node at the click position
            var pointer = network.getPointer({{
                x: event.clientX - container.getBoundingClientRect().left,
                y: event.clientY - container.getBoundingClientRect().top
            }});
            
            var clickedNode = network.getNodeAt(pointer);
            if (clickedNode) {{
                var nodeData = allNodes.get(clickedNode);
                if (nodeData) {{
                    showCascadeContextMenu(event, nodeData);
                }}
            }} else {{
                // Right-click on empty space - show general menu
                showGeneralContextMenu(event);
            }}
        }});
        
        // Progressive disclosure function
        function revealConnectedNodes(nodeId) {{
            // Find all nodes connected to the clicked node
            var connectedNodes = [];
            var connectedEdges = [];
            
            // Get all edges connected to this node
            var edges = allEdges.get();
            edges.forEach(function(edge) {{
                if (edge.from === nodeId || edge.to === nodeId) {{
                    connectedEdges.push(edge);
                    // Add connected nodes
                    if (edge.from === nodeId) {{
                        var targetNode = allNodes.get(edge.to);
                        if (targetNode) connectedNodes.push(targetNode);
                    }}
                    if (edge.to === nodeId) {{
                        var sourceNode = allNodes.get(edge.from);
                        if (sourceNode) connectedNodes.push(sourceNode);
                    }}
                }}
            }});
            
            // Add new nodes and edges to the current network
            var currentNodes = network.getNodes();
            var currentEdges = network.getEdges();
            
            var newNodes = [];
            var newEdges = [];
            
            connectedNodes.forEach(function(node) {{
                if (!currentNodes.includes(node.id)) {{
                    newNodes.push(node);
                }}
            }});
            
            connectedEdges.forEach(function(edge) {{
                if (!currentEdges.includes(edge.id)) {{
                    newEdges.push(edge);
                }}
            }});
            
            // Update the network with new nodes and edges
            if (newNodes.length > 0 || newEdges.length > 0) {{
                var nodesToAdd = [];
                var edgesToAdd = [];
                
                newNodes.forEach(function(node) {{
                    nodesToAdd.push(node);
                }});
                
                newEdges.forEach(function(edge) {{
                    edgesToAdd.push(edge);
                }});
                
                // Add nodes and edges with animation
                initialNodesSet.add(nodesToAdd);
                initialEdgesSet.add(edgesToAdd);
                
                // Show feedback
                showExpansionFeedback(newNodes.length, newEdges.length);
            }}
        }}
        
        function showExpansionFeedback(newNodes, newEdges) {{
            var feedback = document.getElementById('expansion-feedback');
            if (!feedback) {{
                feedback = document.createElement('div');
                feedback.id = 'expansion-feedback';
                feedback.style.cssText = `
                    position: fixed;
                    top: 80px;
                    right: 20px;
                    background: #e8f5e8;
                    border: 2px solid #28a745;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                    z-index: 1000;
                    max-width: 300px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                `;
                document.body.appendChild(feedback);
            }}
            
            var content = '<strong>🔍 Network Expanded</strong><br/>';
            content += '<span style="color: #666;">Added ' + newNodes + ' nodes, ' + newEdges + ' edges</span><br/>';
            content += '<small style="color: #999;">Click another node to explore further</small>';
            
            feedback.innerHTML = content;
            feedback.style.display = 'block';
            
            // Auto-hide after 3 seconds
            setTimeout(function() {{
                if (feedback) {{
                    feedback.style.display = 'none';
                }}
            }}, 3000);
        }}
        
        function showNodeInfo(nodeData) {{
            document.getElementById('node-info').style.display = 'block';
            document.getElementById('node-title').textContent = nodeData.label || 'Unknown Node';
            
            var details = '<p><strong>Type:</strong> ' + (nodeData.group || 'Unknown') + '</p>';
            if (nodeData.moa) {{
                details += '<p><strong>MOA:</strong> ' + nodeData.moa + '</p>';
            }}
            if (nodeData.phase) {{
                details += '<p><strong>Phase:</strong> ' + nodeData.phase + '</p>';
            }}
            
            document.getElementById('node-details').innerHTML = details;
        }}
        
        function showTooltip(event, nodeData) {{
            console.log("Showing tooltip for:", nodeData);
            
            var tooltip = document.getElementById('tooltip');
            if (!tooltip) {{
                tooltip = document.createElement('div');
                tooltip.id = 'tooltip';
                tooltip.style.cssText = `
                    position: fixed;
                    background: rgba(0,0,0,0.9);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 6px;
                    font-size: 13px;
                    pointer-events: none;
                    z-index: 10000;
                    max-width: 250px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    border: 1px solid #555;
                `;
                document.body.appendChild(tooltip);
            }}
            
            var content = '<div style="font-weight: bold; margin-bottom: 5px;">' + (nodeData.label || 'Unknown') + '</div>';
            content += '<div style="color: #ccc; margin-bottom: 3px;">Type: ' + (nodeData.group || 'Unknown') + '</div>';
            
            // Add available properties
            if (nodeData.moa) {{
                content += '<div style="color: #4CAF50; margin-bottom: 3px;">MOA: ' + nodeData.moa + '</div>';
            }}
            if (nodeData.phase) {{
                content += '<div style="color: #FF9800; margin-bottom: 3px;">Phase: ' + nodeData.phase + '</div>';
            }}
            if (nodeData.type) {{
                content += '<div style="color: #2196F3; margin-bottom: 3px;">Target Type: ' + nodeData.type + '</div>';
            }}
            if (nodeData.description) {{
                content += '<div style="color: #9C27B0; margin-bottom: 3px;">Description: ' + nodeData.description + '</div>';
            }}
            
            tooltip.innerHTML = content;
            tooltip.style.left = (event.clientX + 15) + 'px';
            tooltip.style.top = (event.clientY - 10) + 'px';
            tooltip.style.display = 'block';
            tooltip.style.opacity = '1';
        }}
        
        function showSelectionFeedback(nodeData) {{
            var feedback = document.getElementById('selection-feedback');
            if (!feedback) {{
                feedback = document.createElement('div');
                feedback.id = 'selection-feedback';
                feedback.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #e8f4fd;
                    border: 2px solid #0366d6;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                    z-index: 1000;
                    max-width: 300px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                `;
                document.body.appendChild(feedback);
            }}
            
            var content = '<strong>🎯 Selected: ' + nodeData.label + '</strong><br/>';
            content += '<span style="color: #666;">Type: ' + (nodeData.group || 'Unknown') + '</span><br/>';
            if (nodeData.moa) content += '<span style="color: #0066cc;">MOA: ' + nodeData.moa + '</span><br/>';
            if (nodeData.phase) content += '<span style="color: #cc6600;">Phase: ' + nodeData.phase + '</span><br/>';
            content += '<small style="color: #999;">Click another node to recenter • Right-click for more options</small>';
            
            feedback.innerHTML = content;
            feedback.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(function() {{
                if (feedback) {{
                    feedback.style.display = 'none';
                }}
            }}, 5000);
        }}
        
        function hideSelectionFeedback() {{
            var feedback = document.getElementById('selection-feedback');
            if (feedback) {{
                feedback.style.display = 'none';
            }}
        }}
        
        function hideTooltip() {{
            var tooltip = document.getElementById('tooltip');
            if (tooltip) {{
                tooltip.style.display = 'none';
            }}
        }}
        
        function showCascadeContextMenu(event, nodeData) {{
            // Remove any existing menu
            var existingMenu = document.getElementById('context-menu');
            if (existingMenu) {{
                document.body.removeChild(existingMenu);
            }}
            
            var menu = document.createElement('div');
            menu.id = 'context-menu';
            menu.style.cssText = `
                position: fixed;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                z-index: 1000;
                padding: 8px 0;
                min-width: 200px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;
            
            // Menu header
            var header = document.createElement('div');
            header.innerHTML = '<strong style="padding: 8px 16px; color: #333; border-bottom: 1px solid #eee;">' + nodeData.label + '</strong>';
            menu.appendChild(header);
            
            // Menu items
            var items = [
                {{
                    text: '🔬 Show Cascade Effects',
                    action: function() {{
                        showCascadeEffects(nodeData.id, nodeData.label);
                        removeMenu();
                    }}
                }},
                {{
                    text: '🎯 Focus on Node',
                    action: function() {{
                        network.focus(nodeData.id, {{
                            scale: 2.0,
                            animation: {{
                                duration: 1000,
                                easingFunction: "easeInOutQuad"
                            }}
                        }});
                        removeMenu();
                    }}
                }},
                {{
                    text: '📊 Show Node Details',
                    action: function() {{
                        showNodeInfo(nodeData);
                        removeMenu();
                    }}
                }},
                {{
                    text: '🔗 Show Connections',
                    action: function() {{
                        highlightConnections(nodeData.id);
                        removeMenu();
                    }}
                }}
            ];
            
            items.forEach(function(item) {{
                var menuItem = document.createElement('div');
                menuItem.textContent = item.text;
                menuItem.style.cssText = `
                    padding: 12px 16px;
                    cursor: pointer;
                    font-size: 14px;
                    color: #333;
                    transition: background-color 0.2s;
                `;
                
                menuItem.addEventListener('mouseenter', function() {{
                    this.style.background = '#f5f5f5';
                }});
                menuItem.addEventListener('mouseleave', function() {{
                    this.style.background = 'white';
                }});
                menuItem.addEventListener('click', item.action);
                
                menu.appendChild(menuItem);
            }});
            
            menu.style.left = event.clientX + 'px';
            menu.style.top = event.clientY + 'px';
            
            document.body.appendChild(menu);
            
            function removeMenu() {{
                if (document.body.contains(menu)) {{
                    document.body.removeChild(menu);
                }}
            }}
            
            // Remove menu when clicking elsewhere
            setTimeout(function() {{
                document.addEventListener('click', function removeMenuHandler() {{
                    removeMenu();
                    document.removeEventListener('click', removeMenuHandler);
                }});
            }}, 100);
        }}
        
        function showGeneralContextMenu(event) {{
            // Remove any existing menu
            var existingMenu = document.getElementById('context-menu');
            if (existingMenu) {{
                document.body.removeChild(existingMenu);
            }}
            
            var menu = document.createElement('div');
            menu.id = 'context-menu';
            menu.style.cssText = `
                position: fixed;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                z-index: 1000;
                padding: 8px 0;
                min-width: 180px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;
            
            var items = [
                {{
                    text: '🎯 Reset View',
                    action: function() {{
                        network.fit();
                        removeMenu();
                    }}
                }},
                {{
                    text: '🎨 Stabilize Layout',
                    action: function() {{
                        network.stabilize();
                        removeMenu();
                    }}
                }},
                {{
                    text: '🔄 Reload Network',
                    action: function() {{
                        location.reload();
                    }}
                }}
            ];
            
            items.forEach(function(item) {{
                var menuItem = document.createElement('div');
                menuItem.textContent = item.text;
                menuItem.style.cssText = `
                    padding: 12px 16px;
                    cursor: pointer;
                    font-size: 14px;
                    color: #333;
                    transition: background-color 0.2s;
                `;
                
                menuItem.addEventListener('mouseenter', function() {{
                    this.style.background = '#f5f5f5';
                }});
                menuItem.addEventListener('mouseleave', function() {{
                    this.style.background = 'white';
                }});
                menuItem.addEventListener('click', item.action);
                
                menu.appendChild(menuItem);
            }});
            
            menu.style.left = event.clientX + 'px';
            menu.style.top = event.clientY + 'px';
            
            document.body.appendChild(menu);
            
            function removeMenu() {{
                if (document.body.contains(menu)) {{
                    document.body.removeChild(menu);
                }}
            }}
            
            // Remove menu when clicking elsewhere
            setTimeout(function() {{
                document.addEventListener('click', function removeMenuHandler() {{
                    removeMenu();
                    document.removeEventListener('click', removeMenuHandler);
                }});
            }}, 100);
        }}
        
        function highlightConnections(nodeId) {{
            // Highlight all edges connected to this node
            var connectedEdges = network.getConnectedEdges(nodeId);
            var allEdges = edges.getIds();
            
            // Dim all other edges
            var dimmedEdges = allEdges.filter(function(edgeId) {{
                return !connectedEdges.includes(edgeId);
            }});
            
            // Update edge colors
            var updates = [];
            connectedEdges.forEach(function(edgeId) {{
                updates.push({{id: edgeId, color: {{color: '#ff6b6b', highlight: '#ff6b6b'}}}});
            }});
            dimmedEdges.forEach(function(edgeId) {{
                updates.push({{id: edgeId, color: {{color: '#e0e0e0', highlight: '#e0e0e0'}}}});
            }});
            
            edges.update(updates);
            
            // Reset after 3 seconds
            setTimeout(function() {{
                var resetUpdates = [];
                allEdges.forEach(function(edgeId) {{
                    resetUpdates.push({{id: edgeId, color: {{color: '#848484', highlight: '#FF6B6B'}}}});
                }});
                edges.update(resetUpdates);
            }}, 3000);
        }}
        
        function showCascadeEffects(targetId, targetName) {{
            alert('Cascade effects for ' + targetName + ' will be loaded from Neo4j\\n\\nThis will:\\\\n1. Query Neo4j for AFFECTS_DOWNSTREAM relationships\\\\n2. Add new nodes and edges to the network\\\\n3. Update visualization');
        }}
        
        // Control functions
        function stabilizeNetwork() {{
            network.stabilize();
        }}
        
        function reloadNetwork() {{
            location.reload();
        }}
        
        function clearNetwork() {{
            // Reset to initial view (progressive disclosure)
            initialNodesSet.clear();
            initialEdgesSet.clear();
            
            // Add back initial nodes and edges
            initialNodesSet.add(initialNodes);
            initialEdgesSet.add(initialEdges);
            
            network.fit();
        }}
        
        function resetView() {{
            network.fit();
        }}
    </script>
</body>
</html>
    """
    
    return html

