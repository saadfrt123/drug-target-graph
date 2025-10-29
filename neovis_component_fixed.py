"""
FIXED Neovis Component - Working Interactive Network Visualization
"""

import json
import hashlib

def create_visjs_network_component(drug_name: str, network_data: dict, 
                                  height: int = 800, width: str = "100%") -> str:
    """
    Create vis.js network using existing network data structure - FIXED VERSION
    
    Args:
        drug_name: Name of the drug
        network_data: Network data from get_drug_network() method
        height: Height in pixels
        width: Width as CSS value
    
    Returns:
        HTML string with vis.js visualization
    """
    
    # Generate unique ID
    viz_id = hashlib.md5(f"{drug_name}_visjs_fixed".encode()).hexdigest()[:8]
    
    # Convert network data to vis.js format
    nodes_data = []
    edges_data = []
    
    if network_data and 'nodes' in network_data:
        for node in network_data['nodes']:
            node_props = {
                'id': node.get('id', 0),
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
            edges_data.append({
                'from': edge.get('source', 0),
                'to': edge.get('target', 0),
                'label': edge.get('type', 'targets')
            })
    
    # Create HTML - WORKING VERSION
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
            <span>Primary Target</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #f39c12;"></div>
            <span>Secondary Target</span>
        </div>
        <div class="legend-item">
            <div class="legend-circle" style="background: #95a5a6;"></div>
            <span>Unclassified Target</span>
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
        console.log("=== NETWORK DATA DEBUG ===");
        console.log("Drug:", "{drug_name}");
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
                primary_target: {{
                    color: {{background: '#e74c3c', border: '#c0392b'}},
                    size: 25,
                    font: {{size: 14, color: 'white', bold: true, strokeWidth: 2, strokeColor: '#000'}}
                }},
                secondary_target: {{
                    color: {{background: '#f39c12', border: '#e67e22'}},
                    size: 20,
                    font: {{size: 12, color: 'white', bold: true, strokeWidth: 2, strokeColor: '#000'}}
                }},
                unclassified_target: {{
                    color: {{background: '#95a5a6', border: '#7f8c8d'}},
                    size: 18,
                    font: {{size: 11, color: 'white', bold: true, strokeWidth: 2, strokeColor: '#000'}}
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
        
        // Create network
        var container = document.getElementById('network_{viz_id}');
        var network = new vis.Network(container, {{nodes: nodes, edges: edges}}, options);
        
        console.log("Network created successfully!");
        
        // WORKING EVENT LISTENERS
        network.on("selectNode", function(params) {{
            console.log("=== NODE SELECTED ===");
            console.log("Params:", params);
            var nodeId = params.nodes[0];
            var nodeData = nodes.get(nodeId);
            console.log("Node data:", nodeData);
            
            if (!nodeData) {{
                console.log("No node data found!");
                return;
            }}
            
            // Show node info
            showNodeInfo(nodeData);
            
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
        
        // STABLE HOVER - Using vis.js native events
        var tooltipTimeout;
        var currentNodeId = null;
        
        // Use vis.js native hover events for better stability
        network.on("hoverNode", function (params) {{
            if (tooltipTimeout) {{
                clearTimeout(tooltipTimeout);
                tooltipTimeout = null;
            }}
            
            var nodeData = nodes.get(params.node);
            if (nodeData) {{
                currentNodeId = params.node;
                // Get mouse position for tooltip positioning
                var rect = container.getBoundingClientRect();
                var event = {{
                    clientX: rect.left + params.event.center.x,
                    clientY: rect.top + params.event.center.y
                }};
                showTooltip(event, nodeData);
            }}
        }});
        
        network.on("blurNode", function (params) {{
            currentNodeId = null;
            if (tooltipTimeout) {{
                clearTimeout(tooltipTimeout);
                tooltipTimeout = null;
            }}
            // Add delay before hiding to prevent flickering
            tooltipTimeout = setTimeout(function() {{
                hideTooltip();
            }}, 150);
        }});
        
        // Fallback for mouse leave
        container.addEventListener('mouseleave', function(event) {{
            currentNodeId = null;
            if (tooltipTimeout) {{
                clearTimeout(tooltipTimeout);
                tooltipTimeout = null;
            }}
            hideTooltip();
        }});
        
        // WORKING RIGHT-CLICK
        container.addEventListener('contextmenu', function(event) {{
            event.preventDefault();
            console.log("Right-click detected!");
            
            var pointer = network.getPointer({{
                x: event.clientX - container.getBoundingClientRect().left,
                y: event.clientY - container.getBoundingClientRect().top
            }});
            
            var clickedNode = network.getNodeAt(pointer);
            if (clickedNode) {{
                var nodeData = nodes.get(clickedNode);
                if (nodeData) {{
                    showContextMenu(event, nodeData);
                }}
            }}
        }});
        
        // TOOLTIP FUNCTIONS
        function showTooltip(event, nodeData) {{
            var tooltip = document.getElementById('tooltip');
            if (!tooltip) {{
                tooltip = document.createElement('div');
                tooltip.id = 'tooltip';
                tooltip.style.cssText = `
                    position: fixed;
                    background: rgba(0,0,0,0.95);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-size: 13px;
                    pointer-events: none;
                    z-index: 10000;
                    max-width: 280px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
                    border: 2px solid #555;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    opacity: 0;
                    transition: opacity 0.2s ease-in-out;
                `;
                document.body.appendChild(tooltip);
            }}
            
            var content = '<div style="font-weight: bold; margin-bottom: 8px; color: #fff;">' + (nodeData.label || 'Unknown') + '</div>';
            content += '<div style="color: #ccc; margin-bottom: 4px; font-size: 12px;">Type: ' + (nodeData.group || 'Unknown') + '</div>';
            
            // Better MOA handling
            if (nodeData.moa && nodeData.moa !== 'Not specified' && nodeData.moa !== '' && nodeData.moa !== 'Unknown') {{
                content += '<div style="color: #4CAF50; margin-bottom: 4px; font-size: 12px;">MOA: ' + nodeData.moa + '</div>';
            }} else {{
                content += '<div style="color: #666; margin-bottom: 4px; font-size: 12px;">MOA: Not available</div>';
            }}
            
            // Better Phase handling
            if (nodeData.phase && nodeData.phase !== 'Unknown' && nodeData.phase !== '' && nodeData.phase !== 'Not specified') {{
                content += '<div style="color: #FF9800; margin-bottom: 4px; font-size: 12px;">Phase: ' + nodeData.phase + '</div>';
            }} else {{
                content += '<div style="color: #666; margin-bottom: 4px; font-size: 12px;">Phase: Not available</div>';
            }}
            
            if (nodeData.mechanism && nodeData.mechanism !== '') {{
                content += '<div style="color: #2196F3; margin-bottom: 4px; font-size: 12px;">Mechanism: ' + nodeData.mechanism + '</div>';
            }}
            if (nodeData.relationship_type && nodeData.relationship_type !== 'Unknown') {{
                content += '<div style="color: #9C27B0; margin-bottom: 4px; font-size: 12px;">Relationship: ' + nodeData.relationship_type + '</div>';
            }}
            if (nodeData.confidence && nodeData.confidence > 0) {{
                content += '<div style="color: #FF5722; margin-bottom: 4px; font-size: 12px;">Confidence: ' + (nodeData.confidence * 100).toFixed(1) + '%</div>';
            }}
            
            tooltip.innerHTML = content;
            
            // Better positioning - avoid going off screen
            var x = event.clientX + 15;
            var y = event.clientY - 10;
            
            // Check if tooltip would go off screen
            if (x + 280 > window.innerWidth) {{
                x = event.clientX - 295;
            }}
            if (y < 10) {{
                y = event.clientY + 15;
            }}
            
            tooltip.style.left = x + 'px';
            tooltip.style.top = y + 'px';
            tooltip.style.display = 'block';
            
            // Fade in
            setTimeout(function() {{
                tooltip.style.opacity = '1';
            }}, 10);
        }}
        
        function hideTooltip() {{
            var tooltip = document.getElementById('tooltip');
            if (tooltip) {{
                // Fade out first, then hide
                tooltip.style.opacity = '0';
                setTimeout(function() {{
                    if (tooltip) {{
                        tooltip.style.display = 'none';
                    }}
                }}, 200);
            }}
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
            
            setTimeout(function() {{
                if (feedback) {{
                    feedback.style.display = 'none';
                }}
            }}, 5000);
        }}
        
        function showContextMenu(event, nodeData) {{
            console.log("Showing context menu for:", nodeData);
            
            var menu = document.createElement('div');
            menu.style.cssText = `
                position: fixed;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                z-index: 1000;
                padding: 8px 0;
                min-width: 200px;
            `;
            
            var header = document.createElement('div');
            header.innerHTML = '<strong style="padding: 8px 16px; color: #333;">' + nodeData.label + '</strong>';
            menu.appendChild(header);
            
            var item1 = document.createElement('div');
            item1.textContent = '🔬 Show Cascade Effects';
            item1.style.cssText = 'padding: 12px 16px; cursor: pointer; font-size: 14px; color: #333;';
            item1.addEventListener('click', function() {{
                alert('Cascade effects for ' + nodeData.label + ' will be loaded from Neo4j');
                document.body.removeChild(menu);
            }});
            menu.appendChild(item1);
            
            var item2 = document.createElement('div');
            item2.textContent = '🎯 Focus on Node';
            item2.style.cssText = 'padding: 12px 16px; cursor: pointer; font-size: 14px; color: #333;';
            item2.addEventListener('click', function() {{
                network.focus(nodeData.id, {{scale: 2.0, animation: {{duration: 1000}}}});
                document.body.removeChild(menu);
            }});
            menu.appendChild(item2);
            
            menu.style.left = event.clientX + 'px';
            menu.style.top = event.clientY + 'px';
            document.body.appendChild(menu);
            
            setTimeout(function() {{
                document.addEventListener('click', function removeMenu() {{
                    if (document.body.contains(menu)) {{
                        document.body.removeChild(menu);
                    }}
                    document.removeEventListener('click', removeMenu);
                }});
            }}, 100);
        }}
        
        // Control functions
        function stabilizeNetwork() {{
            network.stabilize();
        }}
        
        function reloadNetwork() {{
            location.reload();
        }}
        
        function clearNetwork() {{
            nodes.clear();
            edges.clear();
        }}
        
        function resetView() {{
            network.fit();
        }}
        
        console.log("All event listeners attached successfully!");
    </script>
</body>
</html>
    """
    
    return html
