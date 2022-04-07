import drawSvg
from pygraphml import GraphMLParser


class Drawer:
    def __init__(self, scale):
        self.nodesCoordinates = set()
        self.edgesCoordinates = []
        self.scale = scale

    def addEdge(self, node1, node2):
        self.nodesCoordinates.add(node1)
        self.nodesCoordinates.add(node2)
        self.edgesCoordinates.append((node1, node2))

    def saveResult(self, output_file: str):
        xSize = int(max(map(lambda x: x[0], self.nodesCoordinates)) + 20) * self.scale
        ySize = int(max(map(lambda x: x[1], self.nodesCoordinates)) + 20) * self.scale

        canvas = drawSvg.Drawing(xSize, ySize)

        for edge in self.edgesCoordinates:
            startNode, endNode = edge
            line = drawSvg.Lines(
                startNode[0], ySize - startNode[1],
                endNode[0], ySize - endNode[1],
                close=False,
                stroke='grey',
                stroke_width=3*self.scale)
            canvas.append(line)

        radius = min(map(lambda v: (v[0][0] - v[1][0]) ** 2 + (v[0][1] - v[1][1]) ** 2,
                    self.edgesCoordinates))
        radius = min(radius / 2, 6) * self.scale
        for (x, y) in self.nodesCoordinates:
            circle = drawSvg.Circle(x, ySize - y, radius, fill='red')
            canvas.append(circle)

        canvas.saveSvg(output_file)


class Tree:
    def __init__(self, input_file):
        graph = GraphMLParser().parse(input_file)
        nodesMap = {}  # node name -> node num

        for node in graph.nodes():
            id = node.id
            nodesMap[id] = len(nodesMap)
        self.size = len(nodesMap)
        self.edges = [[] for _ in range(self.size)]

        for edge in graph.edges():
            startNode = nodesMap[edge.node1.id]
            endNode = nodesMap[edge.node2.id]
            self.edges[startNode].append(endNode)


def shiftCoords(m, shift):
    return {k: (v[0] + shift[0], v[1] + shift[1]) for k, v in m.items()}


def drawDfs(graph, v):
    result = {
        v: (0, 0)
    }
    left, right = None, None
    nodeNeighbours = graph.edges[v]
    if len(nodeNeighbours) == 0:
        return result
    left = drawDfs(graph, nodeNeighbours[0])
    result = {**result, **shiftCoords(left, (0, 30))}
    if len(nodeNeighbours) == 2:
        right = drawDfs(graph, nodeNeighbours[1])
        xShift = max(map(lambda x: x[0], left.values())) + 30
        result = {**result, **shiftCoords(right, (xShift, 0))}

    return result
