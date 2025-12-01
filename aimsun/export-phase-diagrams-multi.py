"""
Draw phase diagrams in SVG embedded in html

v6: loop through multiple nodes and MCPs
v5: cater for control plan zones
v4: wrap SVGs in html body to allow multiple CPs
v3: include MCP zone in selection list
v2: initial concept version

Copyright: Tony Wicker, Stantec

"""

import os

# ============================================================================
# CONFIGURATION: Define your nodes and master control plans here
# ============================================================================

# List of node IDs to process
NODE_IDS = [34358114, 34358135, 34358193]

# List of Master Control Plan IDs to process
MCP_IDS = [34358300, 34358302]

# Output file path
OUTPUT_FILE = r"C:\Users\caleb\Documents\Projects\1022_WellingtonRoNS_Phase2\20250804 - Submodels Created\Resources\Phase Diagrams\phase_diagrams.html"

# ============================================================================

def getSignalTurns(node):
    # get node signal groups and turns
    signal_turns = {}
    for group in node.getSignals():
        turns = [x.getId() for x in group.getTurnings()]
        signal_turns[group.getId()] = turns

    return signal_turns

def getSignalsPerPhase(node, control_plan, scenario):

    # get control info for reqd node from specified control plan
    control_junction = control_plan.getControlJunction(node)

    phases_signals = []
    phase_times = []
    ringIDs = []
    cycle_time = 0

    if control_junction != None:

        phases = control_junction.getPhases() # GKControlPhase
        cycle_time = control_junction.getCycle()

        for index, phase in enumerate(phases):
            signalIds = []
            signals = phase.getSignals()
            signalIds = [x.getSignal() for x in signals]
            phases_signals.append(signalIds)

            phase_times.append((int(phase.getDuration()), phase.getInterphase()))
            ringIDs.append(phase.getIdRing())

    # return list of [turns per phase], list of (phase time, type)
    return phases_signals, phase_times, ringIDs, cycle_time

def activeTurn(turnId, groups, signal_turns):
    for group in groups:
        key = group.getId() if hasattr(group, "getId") else group
        turns = signal_turns.get(key)
        if turns and turnId in turns:
            return True
    return False

def getNodeName(node):
    """Get intersection name from entrance sections"""
    road_names = set()
    for section in node.getEntranceSections():
        if section.getName() != "":
            road_names.add(section.getName())
    if len(road_names) == 0:
        int_name = "unknown"
    else:
        int_name = " / ".join(road_names)
    return int_name

def getAllControlPlansForMCP(mcp):
    """Get all control plans from a master control plan's schedule"""
    cp_schedule = mcp.getSchedule()
    control_plans = [x.getControlPlan() for x in cp_schedule]
    return control_plans

def processNodeMCP(node, mcp, scenario, out_svg, nl):
    """Process a single node and master control plan combination"""
    
    int_name = getNodeName(node)
    
    # Write section header for this node/MCP combination
    out_svg.write('<div style="page-break-before: always;">')
    out_svg.write('<h1 style="color:blue;font-size:48px">')
    out_svg.write("Node {0}: {1}".format(node.getId(), int_name))
    out_svg.write('</h1>')
    out_svg.write('<h1 style="color:blue;font-size:36px">')
    out_svg.write("MCP: {0}".format(mcp.getName()))
    out_svg.write('</h1>')
    out_svg.write('<p>&nbsp;</p>')
    
    # Get all control plans for this MCP
    control_plans = getAllControlPlansForMCP(mcp)
    
    # get node signal groups and turns
    signal_turns = getSignalTurns(node)
    
    # Get turnings for this node in the scenario
    turnings = node.getTurnings()
    turnIds = []
    turns = []
    for turn in turnings:
        if turn.exists(scenario):
            turns.append(turn)
            turnIds.append(turn.getId())
    
    # Process each control plan
    for control_plan in control_plans:
        
        # get signal info
        phases_signals, phase_times, ringIDs, cycle_time = getSignalsPerPhase(node, control_plan, scenario)
        
        # max phases per ring
        num_rings = max(ringIDs) if ringIDs else 0
        max_phases = 0
        for i in range(1, num_rings + 1):
            _np = ringIDs.count(i)
            if _np > max_phases:
                max_phases = _np

        if len(phases_signals) > 0:

            # get geometry
            nsegments = 20
            x = []
            y = []
            turns_geo = []
            for turn in turns:
                points = turn.calculatePolyline(nsegments, False, [])
                pts = []
                for pt in points:
                    pts.append((pt.x, pt.y))
                    x.append(pt.x)
                    y.append(pt.y)
                turns_geo.append((turn.getId(), pts))

            height = max(y) - min(y)
            width = max(x) - min(x)

            # shift to zero to reduce size
            minx = min(x)
            miny = min(y)
            # need to account for reverse y direction in SVG
            shifty = (max(y) - miny) + (min(y) - miny)
            # allow for a border
            border = 5.0

            viewbox = str(min(x) - minx - border) + ' ' + str(min(y) - miny - border) + ' ' + str(width + 2.0 * border) + ' ' + str(height + 2.0 * border)
            widthb = width + 2.0 * border

            bbox = "{0},{0} {0},{2} {1},{2} {1},{0} {0},{0}".format(-border, width + 1.0 * border, height + 1.0 * border)

            line_style = [('"grey"', '"1mm"'), ('"limegreen"', '"4mm"')]

            viewport = [400, 400 * (width / height) * (max_phases + 1)]
            
            # output heading for CP svg
            out_svg.write('<h2 style="color:blue;font-size:32px">')
            cycletext = "  [cycle = " + str(int(cycle_time)) + "]"
            out_svg.write(control_plan.getName() + cycletext)
            out_svg.write('</h2>')

            for ringID in range(1, num_rings + 1):

                if num_rings > 1:
                    out_svg.write('<h3 style="color:blue;font-size:24px">')
                    out_svg.write('Ring ' + str(ringID))
                    out_svg.write('</h3>')

                out_svg.write('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" height="{0}px" width="{1}px" viewBox="'.format(viewport[0],
                                    viewport[1]) + viewbox + '" preserveAspectRatio="xMinYMid meet" >' + nl)
                
                out_svg.write('''<style>
.small {font: italic 4px sans-serif;}
.large {font: bold 24px sans-serif;}
</style>''' + nl)

                # output diagram for each phase per ring
                iphasex = 0
                for iphase, groups in enumerate(phases_signals):
                    if ringIDs[iphase] == ringID:

                        out_svg.write('<g id="phase{0}" transform="translate({1},0)">'.format(iphase, iphasex * widthb) + nl)

                        # bounding box for phase diagram
                        out_svg.write('<polyline points="{0}"'.format(bbox) + nl)
                        out_svg.write('fill="none" stroke="black" stroke-linecap="square" vector-effect="non-scaling-stroke" stroke-width="4px" />' + nl)

                        # phase number text (top left)
                        out_svg.write('<text dominant-baseline="hanging" x="{1}" y="{1}" class="small">P{0}</text>'.format(iphase + 1, -(border - 1.0)))
                        
                        # green / intergreen length text (bottom left)
                        if phase_times[iphase][1]:
                            phase_type = "IG"
                        else:
                            phase_type = "G"
                        phase_duration = phase_times[iphase][0]
                        out_svg.write('<text dominant-baseline="auto" x="{1}" y="{2}" class="small">{3}={4}</text>'.format(iphase, -(border - 1.0), height + 1.0 * border - 1.0, phase_type, phase_duration))
                        
                        # draw/colour all turns
                        for turnId, turn_geo in turns_geo:
                            if activeTurn(turnId, groups, signal_turns):
                                linestyle = 1
                            else:
                                linestyle = 0
                            out_svg.write('<polyline points="')
                            for pt in turn_geo:
                                out_svg.write("%.3f,%.3f " % (pt[0] - minx, abs(pt[1] - miny - shifty)))
                            out_svg.write('"' + nl)
                            out_svg.write('fill="none" stroke={0} stroke-linecap="square" vector-effect="non-scaling-stroke" stroke-width={1}/>'.format(line_style[linestyle][0], line_style[linestyle][1]) + nl)

                        iphasex = iphasex + 1
                        out_svg.write('</g>' + nl)

                out_svg.write('</svg>')

        else:
            out_svg.write('<p style="color:red;">No phases found for control plan: {0}</p>'.format(control_plan.getName()))
    
    out_svg.write('</div>')  # Close the page break div
    out_svg.write('<p>&nbsp;</p>')  # Add spacing between sections

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN SCRIPT
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

scenario = model.getActiveScenario()
nl = '\n'

# html top/bottom wrapper
html_wrap = [
    ['<!DOCTYPE html>',
     '<html lang="en">',
     '<head>',
     '<meta charset="utf-8">',
     '<title>Phase Diagrams</title>',
     '</head>',
     '<body font-size: 100%>'],
    ['</body>',
     '</html>']
]

print("Starting phase diagram generation...")
print("Processing {0} nodes and {1} MCPs".format(len(NODE_IDS), len(MCP_IDS)))

with open(OUTPUT_FILE, "w") as out_svg:
    
    # Write HTML header
    for line in html_wrap[0]:
        out_svg.write(line + nl)
    
    # Loop through each node
    for node_id in NODE_IDS:
        node = model.getCatalog().find(node_id)
        
        if node is None:
            print("WARNING: Node {0} not found, skipping...".format(node_id))
            out_svg.write('<h1 style="color:red;">Node {0} not found</h1>'.format(node_id))
            continue
        
        print("Processing Node {0}...".format(node_id))
        
        # Loop through each MCP
        for mcp_id in MCP_IDS:
            mcp = model.getCatalog().find(mcp_id)
            
            if mcp is None:
                print("WARNING: MCP {0} not found, skipping...".format(mcp_id))
                out_svg.write('<h2 style="color:red;">MCP {0} not found</h2>'.format(mcp_id))
                continue
            
            print("  Processing MCP: {0}...".format(mcp.getName()))
            
            # Process this node/MCP combination
            processNodeMCP(node, mcp, scenario, out_svg, nl)
    
    # Write HTML footer
    for line in html_wrap[1]:
        out_svg.write(line + nl)

print("Finished generating phase diagrams.")
print("Output saved to: {0}".format(OUTPUT_FILE))

# Open the file in default browser
os.startfile(OUTPUT_FILE, "open")