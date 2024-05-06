import os

def getInitCommand(graphFile,
				   numSteps,
				   numWalks, 
				   innateOpinionsFile):
	command = './oracle '
	command += f'{graphFile} '
	command += f'{str(numSteps)} '
	command += f'{str(numWalks)} '
	command += f'{innateOpinionsFile} '

	return command

def estimateAllOpinions(graphFile,
						numSteps,
						numWalks,
						innateOpinionsFile):
	command = getInitCommand(graphFile, numSteps, numWalks, innateOpinionsFile)

	command += '--estAllOpinions '

	return estimateOpinionsWithCommand(command)

def estimateOpinionsOfGivenVertices(verticesToClassify,
									graphFile,
									numSteps,
									numWalks,
									innateOpinionsFile):
	command = getInitCommand(graphFile, numSteps, numWalks, innateOpinionsFile)

	uniqueVerticesToClassify = set(verticesToClassify)
	for vtx in uniqueVerticesToClassify:
		command += f'{str(vtx)} '

	return estimateOpinionsWithCommand(command)

def estimateOpinionsWithCommand(command):
	stream = os.popen(command)

	opinions = {}

	lines = stream.readlines()
	t = float(lines[0])
	for i in range(1,len(lines)):
		line = lines[i]
		split = line.strip().split(' ')
		u = int(split[0])
		opinion = float(split[1])

		opinions[u] = opinion

	return opinions, t

