import numpy

import Graph

'''
	Reads a sparse csv file and returns a Graph object.

	Assumes that the csv-file has the following format:
	u,v,edgeWeight
	where u and v are integers and edgeWeight is a float
'''
def graphFromSparseCSV(graphFile, expressedOpinionsFile, innateOpinionsFile, measuresFilePath, separator=',', skipHeader=False, inputIsZeroIndexed=False):
	'''
		since the input file might contain some edges multiple times or as
		directed edges, we start by summing over all of these weights
	'''
	neighbors = []

	n = 0
	with open(graphFile) as fp:
		line = fp.readline()
		if skipHeader:
			line = fp.readline()

		n = int(line)

		for i in range(n):
			neighbors.append(dict())

		line = fp.readline()
		while line:
			lineSplit = str.split(line.strip(), separator)

			u = int(lineSplit[0])
			v = int(lineSplit[1])
			edgeWeight = float(lineSplit[2]) if len(lineSplit) > 2 else 1

			if inputIsZeroIndexed:
				u += 1
				v += 1

			if v not in neighbors[u]:
				neighbors[u][v] = 0
			if u not in neighbors[v]:
				neighbors[v][u] = 0

			neighbors[u][v] += edgeWeight
			neighbors[v][u] += edgeWeight

			line = fp.readline()

	G = Graph.Graph()
	G.graphFile = graphFile
	G.expressedOpinionsFile = expressedOpinionsFile
	G.innateOpinionsFile = innateOpinionsFile

	G.numVertices = n
	for i in range(n):
		G.neighbors.append([])
		G.cumulatedWeights.append([])

	for u in range(n):
		for v in neighbors[u].keys():
			' make sure that each edge is only added once '
			if u < v:
				edgeWeight = neighbors[u][v]
				G.addEdge(u,v,edgeWeight)

	G.z = readOpinionsFile(expressedOpinionsFile)
	G.s = readOpinionsFile(innateOpinionsFile)
	G.measures = readMeasuresFile(measuresFilePath, separator)

	return G

def readOpinionsFile(opinionsFilePath):
	opinions = []

	with open(opinionsFilePath) as fp:
		line = fp.readline()
		while line:
			opinion = float(line.strip())
			opinions.append(opinion)

			line = fp.readline()

	return opinions

def readMeasuresFile(measuresFilePath, separator=','):
	measures = dict()

	with open(measuresFilePath) as fp:
		line = fp.readline()
		while line and len(line.strip()) > 0:
			lineSplit = str.split(line.strip(), separator)

			measure = lineSplit[0]
			value = float(lineSplit[1])
			measures[measure] = value

			line = fp.readline()

	return measures

