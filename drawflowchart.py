import pygraphviz as pgv

# Define the file structure
file_structure = {
    "File1.py": {
        "FileA.py": ["FileB.py"],
        "FileC.py": []
    },
    "File2.py": [],
    "File3.py": ["FileD.py"]
}

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

# Set graph attributes
graph.graph_attr.update(rankdir="TB", ranksep="0.5", nodesep="0.5")

# Set layout and save the graph as an image
graph.layout(prog="dot")
#graph.layout(prog="nop")#, args="-Nshape=box -Efontsize=8"
graph.draw("flow_diagram.png")
