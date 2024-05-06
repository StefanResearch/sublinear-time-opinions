import numpy

import GraphReader

import Estimator
import OracleModule

numRepetitions = 10
experimentsOutputFolderPath = '../results/'

def runExperimentsWithDegreeBuckets(datasets, opinionDistributions):
	numBuckets = 20
	verticesPerBucket = 500

	parameterSet = {
		'numSteps': 600,
		'numWalks': 4000
	}

	for dataset in datasets:
		for opinionDistribution in opinionDistributions:
			runExperimentsWithDegreeBucketsForSetting(dataset,
											  opinionDistribution,
											  parameterSet,
											  numBuckets,
											  verticesPerBucket)

def runExperimentsWithDegreeBucketsForSetting(dataset,
											  opinionDistribution,
											  parameterSet,
											  numBuckets,
											  verticesPerBucket):
	G = loadGraphForParameters(dataset, opinionDistribution)

	bucketizedVertices = G.bucketizedVertices(numBuckets)

	errorsBucket = [[] for i in range(numBuckets)]
	timesBucket = [[] for i in range(numBuckets)]

	errorsAll = []
	timesAll = []

	for repetition in range(numRepetitions):
		print(f'	running repetition {repetition}')
		for numBucket in range(numBuckets):
			experimentType = f'givenSBucket{numBucket}'
			
			sampledVertices = numpy.random.choice(bucketizedVertices[numBucket], size=verticesPerBucket, replace=True)

			innateOpinions = Estimator.getGroundTruthInnateOpinions(G, sampledVertices, parameters=parameterSet)
			expressedOpinions, errors, time = runExperimentsEstimateOpinions(G, dataset, opinionDistribution, sampledVertices, parameterSet, experimentType, writeOpinions=True)

			errorsBucket[numBucket].extend(errors)
			timesBucket[numBucket].append(time)

			errorsAll.extend(errors)
			timesAll.append(time)

	avgErrorAll = numpy.mean(errorsAll)
	stdErrorAll = numpy.std(errorsAll)

	avgTimesAll = numpy.mean(timesAll)
	stdTimesAll = numpy.std(timesAll)

	avgErrors = [numpy.mean(errorsBucket[i])/avgErrorAll for i in range(numBuckets)]
	stdErrors = [numpy.std(errorsBucket[i])/stdErrorAll for i in range(numBuckets)]

	avgTimes = [numpy.mean(timesBucket[i])/avgTimesAll for i in range(numBuckets)]
	stdTimes = [numpy.std(timesBucket[i])/stdTimesAll for i in range(numBuckets)]

	import matplotlib.pyplot as plt
	plt.errorbar(range(numBuckets),avgErrors,stdErrors,marker='o')
	plt.ylabel('normalized avg error in bucket')
	plt.xlabel('bucket')
	plt.xticks(range(numBuckets))
	plt.savefig(f'../plots_buckets/{dataset}_{opinionDistribution}_error.pdf', bbox_inches='tight')
	plt.close('all')

	plt.errorbar(range(numBuckets),avgTimes,stdTimes,marker='o')
	plt.ylabel('normalized avg time in bucket')
	plt.xlabel('bucket')
	plt.xticks(range(numBuckets))
	plt.savefig(f'../plots_buckets/{dataset}_{opinionDistribution}_time.pdf', bbox_inches='tight')
	plt.close('all')

def runExperiments(datasets, opinionDistributions):
	numVertexSamples = [500,1000,2000,3000,4000,5000,7500,10000]

	'''
		experiments givenSIncreases
		experiments for scaling steps and samples
	'''
	initialStepSize = 100
	initialWalkNumber = 100
	increases = [1.5**i for i in range(1,13)]

	parameters = []
	for increase in increases:
		parameterSet = dict()
		parameterSet['numSteps'] = int(initialStepSize * increase)
		parameterSet['numWalks'] = int(initialWalkNumber * increase)
		parameters.append(parameterSet)

	runExperimentsWithParameters(datasets,
								 opinionDistributions,
								 parameters,
								 numVertexSamples,
								 'givenSIncreases')

	'''
		experiments givenZ
	'''
	parameters = []
	numSamplesValues = [100,200,400,600,800]
	numRepetitionsValues = [1,3,5]
	for numSamples in numSamplesValues:
		for numRepetitions in numRepetitionsValues:
			parameterSet = dict()
			parameterSet['numSamples'] = numSamples
			parameterSet['repetitions'] = numRepetitions
			parameters.append(parameterSet)

	runExperimentsWithParameters(datasets,
								 opinionDistributions,
								 parameters,
								 numVertexSamples,
								 'givenZ')

	'''
		experiments givenS
	'''
	stepSizes = [100,200,400,600]
	walkNumbers = [100,500,1000,2000,4000,6000]

	parameters = []
	for numSteps in stepSizes:
		for numWalks in walkNumbers:
			parameterSet = dict()
			parameterSet['numSteps'] = numSteps
			parameterSet['numWalks'] = numWalks
			parameters.append(parameterSet)

	runExperimentsWithParameters(datasets,
								 opinionDistributions,
								 parameters,
								 numVertexSamples,
								 'givenS')

def runExperimentsWithParameters(datasets,
								 opinionDistributions,
								 parameters,
								 numVertexSamples,
								 experimentType):
	for opinionDistribution in opinionDistributions:
		for i in range(len(datasets)):
			dataset = datasets[i]
			print(f'Running for dataset {dataset} {opinionDistribution} {experimentType}.')

			G = loadGraphForParameters(dataset, opinionDistribution)

			for i in range(numRepetitions):
				print(f'	Starting repetition {i}.')
				for parameterSet in parameters:
					runExperimentsEstimateMeasures(G,
												   dataset,
												   numVertexSamples,
												   opinionDistribution,
												   parameterSet,
												   experimentType)
	
def runExperimentsEstimateMeasures(G,
								   dataset,
								   numVertexSamples,
								   opinionDistribution,
								   parameterSet,
								   experimentType):

	numVerticesToSample = numpy.max(numVertexSamples)
	vertices = range(G.numVertices)
	sampledVertices = numpy.random.choice(vertices, size=numVerticesToSample, replace=True)

	measuresFilePath = f"{experimentsOutputFolderPath}/{dataset}_measures_{opinionDistribution}_{experimentType}.csv"

	with open(measuresFilePath, 'a') as measuresFile:
		expressedOpinions = dict()
		innateOpinions = dict()
		paramString = ''
		if 'givenS' in experimentType:
			innateOpinions = Estimator.getGroundTruthInnateOpinions(G, sampledVertices, parameters=parameterSet)
			expressedOpinions,_,_ = runExperimentsEstimateOpinions(G, dataset, opinionDistribution, sampledVertices, parameterSet, experimentType, writeOpinions=True)

			measuresFile.write(f'measure,trueValue,estimatedValue,numSteps,numWalks,numSampledVertices\n')
			paramString = f'{parameterSet["numSteps"]},{parameterSet["numWalks"]}'
		else: # givenZ
			expressedOpinions = Estimator.getGroundTruthExpressedOpinions(G, sampledVertices, parameters=parameterSet)
			innateOpinions,_,_ = runExperimentsEstimateOpinions(G, dataset, opinionDistribution, sampledVertices, parameterSet, experimentType, writeOpinions=True)

			measuresFile.write(f'measure,trueValue,estimatedValue,numSamples,repetitions,numSampledVertices\n')
			paramString = f'{parameterSet["numSamples"]},{parameterSet["repetitions"]}'

		'''
			Now we subsample from sampledVertices for each number of vertices
			contained in numVertexSamples. For each of these samples, we
			estimate the measures and write the results to the disk.
		'''
		for numVerticesToSample in numVertexSamples:
			parameterSet['numVerticesToSample'] = numVerticesToSample

			subsampledVertices = numpy.random.choice(sampledVertices, size=numVerticesToSample, replace=True)
			expressedOpinionsSubsampled = dict()
			innateOpinionsSubsampled = dict()
			for vertex in subsampledVertices:
				expressedOpinionsSubsampled[vertex] = expressedOpinions[vertex]
				innateOpinionsSubsampled[vertex] = innateOpinions[vertex]
			
			writeMeasuresResultsToFile(measuresFile, G, expressedOpinionsSubsampled, innateOpinionsSubsampled, numVerticesToSample, paramString, experimentType)


def runExperimentsEstimateOpinions(G,
								  dataset,
								  opinionDistribution,
								  sampledVertices,
								  parameterSet,
								  experimentType,
								  writeOpinions=False):
	filePrefix = f"{experimentsOutputFolderPath}/{dataset}_opinions_{opinionDistribution}_{experimentType}"
	opinionsFilePath = f"{filePrefix}.csv"
	statsFilePath = f"{filePrefix}_stats.csv"

	groundTruthOpinions = None
	estimateOpinionsFunction = None
	if 'givenS' in experimentType:
		groundTruthOpinions = G.z 
		estimateOpinionsFunction = Estimator.estimateExpressedOpinions
	else:
		groundTruthOpinions = G.s
		estimateOpinionsFunction = Estimator.estimateInnateOpinions

	opinions, totalTime = estimateOpinionsFunction(G, sampledVertices, parameterSet)
	
	''' write the stats file '''
	statsFile = open(statsFilePath, 'a')

	if 'givenS' in experimentType:
		statsFile.write(f'numSampledVertices,numSteps,NumWalks,time,numActualVertices\n')
	else:
		statsFile.write(f'numSampledVertices,numSamples,repetitions,time\n')
		
		
	line = f'{len(sampledVertices)},'
	if 'givenS' in experimentType:
		line += f'{parameterSet["numSteps"]},{parameterSet["numWalks"]}'
	else:
		line += f'{parameterSet["numSamples"]},{parameterSet["repetitions"]}'
	line += f',{totalTime},{len(opinions)}\n'
	statsFile.write(line)

	''' write the opinions file if necessary '''
	if writeOpinions:
		opinionsFile = open(opinionsFilePath, 'a')

		if 'givenS' in experimentType:
			opinionsFile.write('vertexId,trueOpinions,estimatedOpinion,numSteps,numWalks\n')
		else:
			opinionsFile.write('vertexId,trueOpinions,estimatedOpinion,numSamples,repetitions\n')

		for u in opinions:
			line = f'{u},{groundTruthOpinions[u]},{opinions[u]},'
			if 'givenS' in experimentType:
				line += f'{parameterSet["numSteps"]},{parameterSet["numWalks"]}\n'
			else:
				line += f'{parameterSet["numSamples"]},{parameterSet["repetitions"]}\n'
				
			opinionsFile.write(line)

	errors = []
	for u in opinions:
		error = numpy.abs(opinions[u] - groundTruthOpinions[u])
		errors.append(error)

	return opinions, errors, totalTime

def writeMeasuresResultsToFile(measuresFile,
							   G,
							   expressedOpinions,
							   innateOpinions,
							   numVerticesToSample,
							   paramString,
							   experimentType):
	''' controversy '''
	ac = Estimator.estimateControversy(G, expressedOpinions)
	measuresFile.write(f'controversy,{G.measures["ac"]},{ac},{paramString},{numVerticesToSample}\n')

	''' sum of opinions
		here we exploit that the sum of innate and expressed opinions is
		the same.
	'''
	sumop = 0
	if 'givenS' in experimentType:
		sumop = Estimator.estimateSumOfExpressedOpinions(G, innateOpinions)
	else:
		sumop = Estimator.estimateSumOfExpressedOpinions(G, expressedOpinions)
	measuresFile.write(f'sumExpOpinions,{G.measures["sumop"]},{sumop},{paramString},{numVerticesToSample}\n')

	''' polarization '''
	avgop = sumop / G.numVertices
	ap = Estimator.estimatePolarization(G, expressedOpinions, avgop)
	measuresFile.write(f'polarization,{G.measures["ap"]},{ap},{paramString},{numVerticesToSample}\n')

	''' internal conflict '''
	aci = Estimator.estimateInternalConflict(G, expressedOpinions, innateOpinions)
	measuresFile.write(f'internalConflict,{G.measures["aci"]},{aci},{paramString},{numVerticesToSample}\n')

	''' disagreement--controversy '''
	aidc = Estimator.estimateDisCon(G, expressedOpinions, innateOpinions)
	measuresFile.write(f'disCon,{G.measures["aidc"]},{aidc},{paramString},{numVerticesToSample}\n')

	''' squared norm innate opinions '''
	norms = Estimator.estimateSquaredNormS(G, innateOpinions)
	measuresFile.write(f'norms,{G.measures["norms"]},{norms},{paramString},{numVerticesToSample}\n')

	''' disagreement '''
	ad = Estimator.estimateDisagreement(G, expressedOpinions, innateOpinions)
	measuresFile.write(f'ad,{G.measures["ad"]},{ad},{paramString},{numVerticesToSample}\n')

def loadGraphForParameters(dataset, opinionDistribution):
	prefix = '../include/OpinionQuantities-mine/outputs'
	graphFile = f'{prefix}/{dataset}_G.txt'
	expressedOpinionsFile = f'{prefix}/{dataset}_{opinionDistribution}_z.txt'
	innateOpinionsFile = f'{prefix}/{dataset}_{opinionDistribution}_s.txt'
	measuresFile = f'{prefix}/{dataset}_{opinionDistribution}_measures.txt'

	G = GraphReader.graphFromSparseCSV(graphFile,
									   expressedOpinionsFile,
									   innateOpinionsFile,
									   measuresFile,
									   separator=' ')
	print(f'	Read graph {dataset} with {G.numVertices} vertices and {G.numEdges} edges.')

	return G

