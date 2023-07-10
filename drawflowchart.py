import pygraphviz as pgv
import json

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
file_structure={
	"onic\\ROM\\toolsupport\\jenkinsfile": {
		"onall\\toolsupport\\keil\\provision_cmsis_packs.bat": {
			"onall\\toolsupport\\keil\\activate_virtual_env.bat": {
				"onall\\toolsupport\\keil\\make_virtual_env.bat": {
					"onall\\toolsupport\\python\\run_python3.bat": [],
					"onall\\toolsupport\\keil\\keil-ini-tool.py": []
				}
			}
		},
		"onic\\ROM\\toolsupport\\start_build_coverity.bat": {
			"onall\\toolsupport\\python\\project-env-tool.bat": {
				"onall\\toolsupport\\python\\run_python3.bat": [],
				"onall\\toolsupport\\python\\project-env-tool.py": []
			},
			"onic\\ROM\\ROM.mmf": [],
			"onall\\toolsupport\\coverity\\build_with_coverity.bat": [],
			"onic\\ROM\\toolsupport\\start_build.bat": {
				"onic\\ROM\\toolsupport\\project_env.bat": [],
				"onic\\ROM\\toolsupport\\\\pack\\make_rom_pack.bat": {
					"onic\\ROM\\toolsupport\\python\\rom-pack-builder.py": []
				},
				"onic\\ROM\\toolsupport\\Keil\\buildImages.bat": [],
				"onic\\ROM\\toolsupport\\\\pack\\make_sec_pack.bat": {
					"onic\\ROM\\toolsupport\\python\\rom-pack-builder.py": []
				},
				"onic\\ROM\\toolsupport\\\\pack\\make_ns_pack.bat": {
					"onic\\ROM\\toolsupport\\python\\rom-pack-builder.py": []
				},
				"onhost\\testrunner-framework\\onhost\\TestRunner\\toolsupport\\start_build.bat": []
			}
		}
	}
}

# Load JSON structure from file
#with open('file_structure.json', 'r') as file:
#    file_structure = json.load(file)

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
with open('file_structure_updated.json', 'w') as file:
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
reversed_graph.draw("flow_diagram.png")
