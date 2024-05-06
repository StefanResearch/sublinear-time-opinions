import GraphReader
import Eval
import Estimator

import numpy

numRepetitions = 10

def runExperimentsDisagreement(datasets, opinionDistributions):
	ks = [1000, 2500, 5000, 10000, 20000]

	for dataset in datasets:
		for opinionDistribution in opinionDistributions:
			runExperimentsDisagreementWithValues(dataset, opinionDistribution, ks, None)

			G = Eval.loadGraphForParameters(dataset, opinionDistribution)
			runExperimentsDisagreementWithValues(dataset, opinionDistribution, ks, G)

'''
	if G == None, uses the true expressed opinions from z, otherwise uses the
	random walk oracle
'''
def runExperimentsDisagreementWithValues(dataset, opinionDistribution, ks, G):
	meanErrors = []
	stdErrors = []

	for k in ks:
		print(f'Running disagreement experiments for k={k} on {dataset}')
		meanError, stdError = estimateDisagreement(dataset, opinionDistribution, k, G)

		meanErrors.append(meanError)
		stdErrors.append(stdError)

	suffix = 'z' if G==None else 's'

	import matplotlib.pyplot as plt
	plt.errorbar(ks,meanErrors,stdErrors,marker='o')
	plt.ylabel('normalized average error')
	plt.xlabel('#sampled edges')
	plt.xticks(rotation=90)
	plt.xticks(ks)
	plt.savefig(f'../plots_disagreement/{dataset}_{opinionDistribution}_{suffix}_error.pdf', bbox_inches='tight')
	plt.close('all')

def estimateDisagreement(dataset, opinionDistribution, numberOfEdges, G):
	edges, z, _, measures = loadEdgeListForParameters(dataset, opinionDistribution)
	m = len(edges)

	errors= []

	for repetition in range(numRepetitions):
		print(f'	running repetition {repetition}')
		experimentType = f'disagreement{numberOfEdges}'
		
		sampledIndices = numpy.random.choice(range(len(edges)), size=numberOfEdges, replace=True)
		sampledEdges = [edges[i] for i in sampledIndices]

		if G is not None:
			parameters = {
				'numSteps': 600,
				'numWalks': 4000
			}
			sampledVertices = set()
			for (u,v) in sampledEdges:
				sampledVertices.add(u)
				sampledVertices.add(v)
			sampledVertices = list(sampledVertices)
			z, _ = Estimator.estimateExpressedOpinions(G, sampledVertices, parameters)

		error = estimateDisagreementForEdges(sampledEdges, z, m, measures)

		errors.append(error)

	meanError = numpy.mean(errors)
	stdError = numpy.std(errors)

	return meanError, stdError

def estimateDisagreementForEdges(edges, z, m, measures):
	estimatedDisagreement = 0

	for (u,v) in edges:
		estimatedDisagreement += (z[u] - z[v])**2

	estimatedDisagreement = estimatedDisagreement * m / len(edges)
	
	trueDisagreement = measures['ad']

	error = numpy.absolute(estimatedDisagreement - trueDisagreement)/trueDisagreement

	return error

def loadEdgeListForParameters(dataset, opinionDistribution):
	prefix = '../include/OpinionQuantities-mine/outputs'
	graphFile = f'{prefix}/{dataset}_G.txt'
	expressedOpinionsFile = f'{prefix}/{dataset}_{opinionDistribution}_z.txt'
	innateOpinionsFile = f'{prefix}/{dataset}_{opinionDistribution}_s.txt'
	measuresFile = f'{prefix}/{dataset}_{opinionDistribution}_measures.txt'

	edges, z, s, measures = edgeListFromSparseCSV(graphFile,
									   expressedOpinionsFile,
									   innateOpinionsFile,
									   measuresFile,
									   separator=' ')
	print(f'	Read edge list for {dataset} with {len(edges)} edges.')

	edges = list(edges)

	return edges, z, s, measures

def edgeListFromSparseCSV(graphFile, expressedOpinionsFile, innateOpinionsFile, measuresFilePath, separator=',', skipHeader=False, inputIsZeroIndexed=False):
	'''
		since the input file might contain some edges multiple times or as
		directed edges, we start by summing over all of these weights
	'''
	edges = set()

	with open(graphFile) as fp:
		line = fp.readline()
		if skipHeader:
			line = fp.readline()

		n = int(line)

		line = fp.readline()
		while line:
			lineSplit = str.split(line.strip(), separator)

			u = int(lineSplit[0])
			v = int(lineSplit[1])

			edges.add( (u,v) )

			line = fp.readline()

	z = GraphReader.readOpinionsFile(expressedOpinionsFile)
	s = GraphReader.readOpinionsFile(innateOpinionsFile)
	measures = GraphReader.readMeasuresFile(measuresFilePath, separator)

	return edges, z, s, measures

