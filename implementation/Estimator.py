import OracleModule

import numpy
import time

def getGroundTruthExpressedOpinions(G, sampledVertices, parameters=None):
	opinions = {}
	for u in sampledVertices:
		opinions[u] = G.z[u]
	return opinions

def getGroundTruthInnateOpinions(G, sampledVertices, parameters=None):
	opinions = {}
	for u in sampledVertices:
		opinions[u] = G.s[u]
	return opinions

def estimateExpressedOpinions(G, sampledVertices, parameters):
	numSteps = parameters['numSteps']
	numWalks = parameters['numWalks']
	opinions, timeForQueries = OracleModule.estimateOpinionsOfGivenVertices(sampledVertices,
									G.graphFile,
									numSteps,
									numWalks,
									G.innateOpinionsFile)

	return opinions, timeForQueries

def weightedNeighborSum(G, u, selectedNeighborIndices):
	neighborSum = 0

	for i in selectedNeighborIndices:
		neighbor = G.neighbors[u][i]
		if i == 0:
			edgeWeight = G.cumulatedWeights[u][i]
		else:
			edgeWeight = G.cumulatedWeights[u][i] - G.cumulatedWeights[u][i-1]

		neighborSum += edgeWeight * G.z[neighbor]

	return neighborSum

def estimateInnateOpinion(G, u, parameters):
	numSamples = parameters['numSamples']
	repetitions = parameters['repetitions']

	opinion = (1 + G.cumulatedWeights[u][-1]) * G.z[u]

	if numSamples >= len(G.neighbors[u]):
		opinion -= weightedNeighborSum(G, u, range(len(G.neighbors[u])))
	else:
		estimatedSums = []
		for _ in range(repetitions):
			selectedNeighborIndices = []
			for i in range(numSamples):
				selectedNeighborIndices.append(G.weightedRandomNeighborIndex(u))
			estimatedSum = weightedNeighborSum(G, u, selectedNeighborIndices)
			estimatedSum *= G.cumulatedWeights[u][-1] / numSamples # do re-scaling
			estimatedSums.append(estimatedSum)

		opinion -= numpy.median(estimatedSums)

	opinion = min(opinion, 1)
	opinion = max(opinion, 0)

	return opinion

def estimateInnateOpinions(G, sampledVertices, parameters=None):
	t = time.time()

	opinions = dict()
	for u in sampledVertices:
		opinion = estimateInnateOpinion(G, u, parameters)
		opinions[u] = opinion

	totalTime = time.time() - t

	return opinions, totalTime


'''
	Estimate the average expressed opinions.
'''
def estimateAvgExpressedOpinion(G, expressedOpinions, parameters=None):
	avgOpinion = 0

	for u in expressedOpinions:
		avgOpinion += expressedOpinions[u]

	numVerticesToSample = len(expressedOpinions)
	avgOpinion = avgOpinion/numVerticesToSample

	return avgOpinion

'''
	Estimate the sum of expressed/innate opinions.
'''
def estimateSumOfExpressedOpinions(G, expressedOpinions):
	return G.numVertices * estimateAvgExpressedOpinion(G, expressedOpinions)

'''
	Estimate the controvsery.
'''
def estimateControversy(G, expressedOpinions):
	controversy = 0

	for u in expressedOpinions:
		controversy += expressedOpinions[u] ** 2

	numVerticesToSample = len(expressedOpinions)
	controversy = (G.numVertices / numVerticesToSample) * controversy

	return controversy

'''
	Estimate squared norm of innate opinions.
'''
def estimateSquaredNormS(G, innateOpinions):
	return estimateControversy(G, innateOpinions)

'''
	Estimate the internal conflict.
'''
def estimateInternalConflict(G, expressedOpinions, innateOpinions):
	internalConflict = 0

	for u in expressedOpinions:
		internalConflict += (expressedOpinions[u] - innateOpinions[u]) ** 2

	numVerticesToSample = len(expressedOpinions)
	internalConflict = (G.numVertices / numVerticesToSample) * internalConflict

	return internalConflict

'''
	Estimate the disagreement--controversy.
'''
def estimateDisCon(G, expressedOpinions, innateOpinions):
	disCon = 0

	for u in expressedOpinions:
		disCon += expressedOpinions[u] * innateOpinions[u]

	numVerticesToSample = len(expressedOpinions)
	disCon = (G.numVertices / numVerticesToSample) * disCon
	disCon = max(disCon, 0)
	disCon = min(disCon, G.numVertices)

	return disCon

'''
	Estimate the polarization.
'''

def estimatePolarization(G, expressedOpinions, avgOpinion):
	polarization = 0

	for u in expressedOpinions:
		polarization += (expressedOpinions[u] - avgOpinion)**2

	numVerticesToSample = len(expressedOpinions)
	polarization = (G.numVertices / numVerticesToSample) * polarization

	return polarization

'''
	Estimate the disagreement.
'''

def estimateDisagreement(G, expressedOpinions, innateOpinions):
	squaredNormS = estimateSquaredNormS(G, innateOpinions)
	controversy = estimateControversy(G, expressedOpinions)
	internalConflict = estimateInternalConflict(G, expressedOpinions, innateOpinions)

	disagreement = (squaredNormS - controversy - internalConflict)/2
	disagreement = max(disagreement, 0)
	disagreement = min(disagreement, G.totalEdgeWeights)

	return disagreement

