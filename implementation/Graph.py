import random
import numpy

import time

class Graph:
	'''
		The graph is stored as a dict over unordered lists. Because of how the
		graph is stored, the vertex ids start at 1 (and not at 0).

		- neighbors is a dict of lists that stores the neighbors in an unordered
		way.
		- cumulatedWeights is a dict of lists that stores cumulates weights,
			i.e., cumulatedWeights[u][5] stores the cumulated weights of
			neighbors 0..5 of vertex u.
	'''
	def __init__(self):
		self.neighbors = []
		self.cumulatedWeights = []

		self.numVertices = 0
		self.numEdges = 0
		self.totalEdgeWeights = 0
		self.z = []
		self.s = []
		self.measures = dict()

		self.graphFile = ''
		self.expressedOpinionsFile = ''
		self.innateOpinionsFile = ''


	'''
		Returns the total weight of all edges incident upon u.
	'''
	def totalEdgeWeight(self, u):
		if len(self.cumulatedWeights[u]) == 0:
			return 0

		return self.cumulatedWeights[u][-1]

	'''
		u and v should be integers,
		edgeWeight should be a float.

		Does not ensure consistency
		(e.g., there could be multiple edges of different weights).
	'''
	def addEdge(self, u, v, weight):
		self.neighbors[u].append(v)
		self.neighbors[v].append(u)

		self.cumulatedWeights[u].append( self.totalEdgeWeight(u) + weight )
		self.cumulatedWeights[v].append( self.totalEdgeWeight(v) + weight )

		self.numEdges += 1
		self.totalEdgeWeights += weight

	def addVertex(self, u):
		self.neighbors[u] = []
		self.cumulatedWeights[u] = []

		self.numVertices += 1

	'''
		Returns a uniformly random neighbor of vertex u
		together with the weight of the edge.

		This does NOT take into account edge weights.
	'''
	def randomNeighbor(self, u):
		neighbor = random.choice(self.neighbors[u])

		return neighbor

	'''
		Returns a random neighbor v of vertex u with probability proportional
		the weight of the edge, i.e., each neighbors is returned with
		probability w(u,v)/totalEdgeWeight(u).
	'''
	def weightedRandomNeighborIndex(self, u):
		''' We sample a random weight in [0,totalEdgeWeight(u)].
			Then we use binary search to find the edge such that the random
			weight is in the interval
			[cumulatedWeights[u][i], cumulatedWeights[u][i+1]) and return the
			edge (u,neighbors[u][i]). This gives the desired probability
			distribution.

			Note that this returns the INDEX of a random neighbor (not the
			neighbor itself).
		'''
		targetWeight = random.uniform(0,self.totalEdgeWeight(u))
		
		if targetWeight >= self.totalEdgeWeight(u):
			return self.neighbors[u][-1]

		n = len(self.neighbors[u])
		left = 0
		right = n
		while True:
			i = int((left + right)/2)
			if targetWeight <= self.cumulatedWeights[u][i]:
				if i == 0:
					return 0
				else:
					if targetWeight >= self.cumulatedWeights[u][i-1]:
						return i
					else:
						right = max(0,i-1)
			else:
				left = min(i+1,n-1)
				if left == n-1:
					return n-1

		print('If you see this, something went wrong sampling a weighted random neighbor.')
		return 0

	'''
		Returns the number of edges from G[S] to G[V\S].
	'''
	def numEdgesLeavingSet(self, S):
		numEdgesLeaving = 0
		for u in S:
			for neighbor in self.neighbors[u]:
				if neighbor not in S and -neighbor not in S:
					numEdgesLeaving += 1

		return numEdgesLeaving

	'''
		Returns the volume of a set of vertices S.
	'''
	def volume(self, S):
		vol = 0
		for s in S:
			vol += self.degree(s)

		return vol

	'''
		Returns the degree of vertex u.
	'''
	def degree(self, u):
		return len(self.neighbors[u])

	def bucketizedVertices(self, numBuckets):
		bucketizedVertices = []

		degrees = {}
		for u in range(len(self.neighbors)):
			degrees[u] = self.degree(u)

		sortedVertices = sorted(degrees.items(), key=lambda x:x[1])
		sortedVertices = [x for (x,y) in sortedVertices]
		bucketizedVertices = numpy.array_split(sortedVertices, numBuckets)
		
		return bucketizedVertices
