import argparse

from numpy import median

from solution import OrGraph, Drawer, minimizeDummies, CoffmanGrahamAlgorithm

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, type=str, help='Graphml file submitted for input')
parser.add_argument('-o', '--output', required=True, type=str, help='Svg file resulting from the output')
parser.add_argument('-w', '--width', required=False, type=int, help='Maximum allowable layer width')

args = parser.parse_args()
input = args.input
output = args.output
W = args.width

myGraph = OrGraph(input)
layers = []

if W is None:
    layers = minimizeDummies(myGraph)
else:
    layers = CoffmanGrahamAlgorithm(myGraph, W)

new_graph = OrGraph("dummy")
size = myGraph.size
for u in range(size):
    assert u == new_graph.addNode(False, len(myGraph.edgesForIn[u]) == 0)
layer_num = [0] * size
for (num, layer) in enumerate(layers):
    for v in layer:
        layer_num[v] = num
for u in range(size):
    for v in myGraph.edgesForOut[u]:
        if layer_num[u] + 1 == layer_num[v]:
            new_graph.addEdge(u, v)
        else:
            start = u
            for layer in range(layer_num[u] + 1, layer_num[v]):
                dummy = new_graph.addNode(True, False)
                layers[layer].append(dummy)
                new_graph.addEdge(start, dummy)
                start = dummy
            new_graph.addEdge(start, v)

drawer = Drawer()
step = 50
coords = {}


def nodesDistribution(u):
    return median(list(map(lambda x: coords[x][0], new_graph.edgesForIn[u]))), u


for (layer_num, layer) in enumerate(layers):
    if layer_num > 0:
        layer = list(map(lambda x: x[1], sorted([nodesDistribution(u) for u in layer])))
    for (num, u) in enumerate(layer):
        coords[u] = ((layer_num % 2) * (step / 2) + num * step, layer_num * step)
        drawer.addNode(u, coords[u], new_graph.nodeInfo[u][0], new_graph.nodeInfo[u][1])

for u in range(new_graph.size):
    for v in new_graph.edgesForOut[u]:
        drawer.addEdge(u, v)

drawer.saveResult(output)
