include("Graph.jl")
include("Tools.jl")
include("Algorithm.jl")

# Read Graph
buf = split(ARGS[1], ',')
fileName = string("data/", buf[1], ".txt")
networkType = "unweighted"
if size(buf, 1) > 1
	networkType = buf[2]
end
# Find LLC
G0 = readGraph(fileName, networkType)
G = getLLC(G0)

lg = open("log.txt", "a")
println(lg, buf[1])
println(lg, G.n, " ", G.m)
println(lg)

if ARGS[2] == "1"
    # Uniform distribution
    println(lg, "Uniform")
    s = Uniform(G.n)
    doLarge(G, s, lg)
elseif ARGS[2] == "2"
    # Exponential distribution
    println(lg, "Exponential")
    s = Exponential(G.n)
    doLarge(G, s, lg)
else
    # Power-law distribution
    println(lg, "Power-law")
    s = powerLaw(G.n)
    doLarge(G, s, lg)
end

println(lg, "--------------- END ---------------")
println(lg)
