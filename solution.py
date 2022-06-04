import drawSvg
from pygraphml import GraphMLParser
from scipy.optimize import linprog


class Drawer:
    def __init__(self):
        self.nodesCoordinates = dict()
        self.edgesCoordinates = list()

    def addNode(self, node, coordinates, dummy, root):
        self.nodesCoordinates[node] = (coordinates, dummy, root)

    def addEdge(self, node1, node2):
        self.edgesCoordinates.append((node1, node2))

    def saveResult(self, output_file: str):
        xSize = int(max(map(lambda x: x[0][0], self.nodesCoordinates.values())) + 40)
        ySize = int(max(map(lambda x: x[0][1], self.nodesCoordinates.values())) + 40)

        canvas = drawSvg.Drawing(xSize, ySize)

        for edge in self.edgesCoordinates:
            startNode, endNode = edge
            startNodeCoordinates = self.nodesCoordinates[startNode][0]
            endNodeCoordinates = self.nodesCoordinates[endNode][0]

            line = drawSvg.Lines(
                startNodeCoordinates[0] + 30, ySize - startNodeCoordinates[1] - 30,
                endNodeCoordinates[0] + 30, ySize - endNodeCoordinates[1] - 30,
                close=False,
                stroke='grey',
                stroke_width=3)
            canvas.append(line)

        radius = 5
        for ((x, y), dummy, root) in self.nodesCoordinates.values():
            if dummy:
                continue
            circle = drawSvg.Circle(x + 30, ySize - y - 30, radius, fill='#33ff42' if root else 'red')
            canvas.append(circle)

        canvas.saveSvg(output_file)


class OrGraph:
    def __init__(self, input_file):
        if input_file == "dummy":
            self.edgesForIn = []
            self.edgesForOut = []
            self.nodeInfo = []
            self.size = 0
            return

        graph = GraphMLParser().parse(input_file)
        nodesMap = {}  # node name -> node num

        for node in graph.nodes():
            id = node.id
            nodesMap[id] = len(nodesMap)
        self.size = len(nodesMap)
        self.edgesForIn = [[] for _ in range(self.size)]
        self.edgesForOut = [[] for _ in range(self.size)]

        for edge in graph.edges():
            startNode = nodesMap[edge.node1.id]
            endNode = nodesMap[edge.node2.id]
            self.edgesForOut[startNode].append(endNode)
            self.edgesForIn[endNode].append(startNode)

    def addEdge(self, In, Out):
        self.edgesForOut[In].append(Out)
        self.edgesForIn[Out].append(In)

    def addNode(self, dummy, root):
        self.edgesForIn.append([])
        self.edgesForOut.append([])
        self.nodeInfo.append((dummy, root))
        num = self.size
        self.size += 1
        return num


def CoffmanGrahamAlgorithm(my_graph, W):
    size = my_graph.size
    pi = [0] * size
    for i in range(1, size + 1):
        v = None
        for u in range(size):
            if pi[u] > 0:
                continue
            ok = True
            for par in my_graph.edgesForIn[u]:
                if pi[par] == 0:
                    ok = False
            if not ok:
                continue
            u_set = set([pi[par] for par in my_graph.edgesForIn[u]])
            if v is None or compareTwoSets(u_set, v[1]) < 0:
                v = (u, u_set)
        if v is None:
            break
        pi[v[0]] = i

    marked = [-1] * size
    layers = [[]]
    for _ in range(size):
        v = None
        for u in range(size):
            if marked[u] >= 0:
                continue
            if -1 in [marked[to] for to in my_graph.edgesForOut[u]]:
                continue
            if v is None or pi[u] > pi[v]:
                v = u
        if len(layers[-1]) >= W or len(layers) in [marked[to] for to in my_graph.edgesForOut[v]]:
            layers.append([])
        layers[-1].append(v)
        marked[v] = len(layers)
    layers.reverse()
    return layers


def compareTwoSets(First, Second):
    for a, b in zip(sorted(First, reverse=True), sorted(Second, reverse=True)):
        if a > b:
            return 1
        if a < b:
            return -1

    if len(First) > len(Second):
        return 1
    if len(First) < len(Second):
        return -1
    return 0


def minimizeDummies(my_graph):
    size = my_graph.size
    c = [len(my_graph.edgesForIn[edge]) - len(my_graph.edgesForOut[edge]) for edge in range(size)]
    A = []
    for u in range(size):
        for v in my_graph.edgesForOut[u]:
            row = [0] * size
            row[u] = 1
            row[v] = -1
            A.append(row)
    b = [-1] * len(A)

    outcome = linprog(c, A, b, bounds=(0, size - 1), method="revised simplex")
    layers = []
    for (vertex, layer) in zip(range(size), list(map(int, outcome.x))):
        while len(layers) <= layer:
            layers.append([])
        layers[layer].append(vertex)
    return layers
