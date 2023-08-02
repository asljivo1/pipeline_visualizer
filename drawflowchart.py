import pygraphviz as pgv
import json
import sys
import re

if len(sys.argv) > 1:
    filename = sys.argv[1]
    print("Received filename:", filename)
else:
    print("No filename provided.")
# file_structure = {
#     "File1.py": {
#         "FileA.py": {
#             "FileB.py" : []
#         },
#         "FileC.py": []
#     },
#     "File2.py": [],
#     "File3.py": ["FileD.py"]
# }
file_structure=None

# Load JSON structure from file
with open(filename, 'r') as file:
    file_structure = json.load(file)

# Replace backslashes
def replace_backslashes(dictionary):
    updated_dict = {}
    for key, value in dictionary.items():
        if isinstance(key, str):
            updated_key = key.replace("\\", "/")
        else:
            updated_key = key
        if isinstance(value, dict):
            value = replace_backslashes(value)
        updated_dict[updated_key] = value
    return updated_dict

file_structure = replace_backslashes(file_structure)

# Save updated JSON structure back to file
with open(filename, 'w') as file:
    json.dump(file_structure, file, indent=4)

# Create a graph
graph = pgv.AGraph(directed=True)

# Set node attributes
node_attrs = {
    "shape": "rectangle",
    "style": "filled",
    "fillcolor": "white",
}

# Recursive function to add nodes and edges
def add_nodes_and_edges(file, dependencies):
    graph.add_node(file, **node_attrs)

    if isinstance(dependencies, dict):
        for dependency, sub_dependencies in dependencies.items():
            graph.add_node(dependency, **node_attrs)
            graph.add_edge(file, dependency)
            add_nodes_and_edges(dependency, sub_dependencies)
    elif isinstance(dependencies, list):
        for dependency in dependencies:
            graph.add_node(dependency, **node_attrs)
            graph.add_edge(file, dependency)

# Iterate through the file structure
for file, dependencies in file_structure.items():
    add_nodes_and_edges(file, dependencies)

# Create a new graph with reversed nodes
reversed_graph = pgv.AGraph(directed=True)
for node in reversed(graph.nodes()):
    reversed_graph.add_node(node, **node_attrs)

# Add edges to the reversed graph
for edge in graph.edges():
    reversed_graph.add_edge(edge[0], edge[1])

# Set graph attributes
reversed_graph.graph_attr.update(rankdir="LR", ranksep="0.5", nodesep="0.5")

# Set layout and save the graph as an image
reversed_graph.layout(prog="dot")

png_filename = None
pattern = r"file_structure_(\d+)\.json"
match = re.search(pattern, filename)
if match:
    # Extract the number from the matched group
    counter_number = int(match.group(1))
    png_filename = f"flow_diagram_{counter_number}.png"
else:
    print("No counter number found in the filename.")
    png_filename = f"flow_diagram_0000.png"

reversed_graph.draw(png_filename)
