include("Graph.jl")
include("Tools.jl")
include("Algorithm.jl")

using Plots

# Read Graph
buf = split(ARGS[1], ',')
fileName = string("data/", buf[1], ".txt")
networkType = "unweighted"
if size(buf, 1) > 1
	networkType = buf[2]
end

# Find LCC
graphFilePath = string("outputs/", buf[1], "_G.txt")
graphFile = open(graphFilePath, "w")

G0 = readGraph(fileName, networkType)
G = getLCC(G0, graphFile)

opinionsType = ""
if ARGS[2] == "1"
    # Uniform distribution
	opinionsType = "Uniform"
    s = Uniform(G.n)
elseif ARGS[2] == "2"
    # Exponential distribution
	opinionsType = "Exponential"
    s = Exponential(G.n)
elseif ARGS[2] == "3"
    # Power-law distribution
	opinionsType = "PowerLaw"
    s = powerLaw(G.n)
else
    # based on second smallest eigenvalue
	opinionsType = "Eigenvalue"
    s = eigenvalueOpinions(G)
end

for iteration in 1:1
	measuresFilePath = string("outputs/", buf[1], "_", opinionsType, "_measures.txt")
	innateOpinionsFilePath = string("outputs/", buf[1], "_", opinionsType, "_s.txt")
	expressedOpinionsFilePath = string("outputs/", buf[1], "_", opinionsType, "_z.txt")

	measuresFile = open(measuresFilePath, "a")
	innateOpinionsFile = open(innateOpinionsFilePath, "w")
	expressedOpinionsFile = open(expressedOpinionsFilePath, "w")

	writeVector(s, innateOpinionsFile)

	maxIterationsPageRank = 50
	pageRankPlotFile = string("outputs/", buf[1], "_", opinionsType, "_PageRank_plot.pdf")
	z = doExp(G, s, measuresFile, expressedOpinionsFile, maxIterationsPageRank, pageRankPlotFile)
		
	plotOpinionHistogram(s, string("outputs/", buf[1], "_", opinionsType, "_s_plot.pdf"))
	plotOpinionHistogram(z, string("outputs/", buf[1], "_", opinionsType, "_z_plot.pdf"))
end

