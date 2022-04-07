import argparse
from solution import Tree, Drawer, drawDfs

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, type=str, help='Graphml file submitted for input')
parser.add_argument('-o', '--output', required=True, type=str, help='Svg file resulting from the output')
parser.add_argument('-s', '--scale', required=False, type=int, help='Image scaling')


args = parser.parse_args()
inputFile = args.input
outputFile = args.output
scale = args.scale

graph = Tree(inputFile)
drawer = Drawer(scale)

drawn = drawDfs(graph, 0)
nodeCoordinates = {k: ((v[0] + 40)*scale, (v[1] + 40)*scale) for k, v in drawn.items()}
for node, coordinates in nodeCoordinates.items():
    for end in graph.edges[node]:
        drawer.addEdge(coordinates, nodeCoordinates[end])

drawer.saveResult(outputFile)
