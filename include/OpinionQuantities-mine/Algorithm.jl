include("Graph.jl")
include("Tools.jl")

using SparseArrays
using Laplacians

function Exact(G, s) # Returns ci, d, p, idc
	T = time()
	L = getSparseL(G)
	W = getW(G)
	avgs = sum(s)/G.n
	centeredS = zeros(G.n)
	for i = 1 : G.n
		centeredS[i] = s[i] - avgs
	end
	z = W * s
	centeredZ = W * centeredS
	# calculate C_I(G)
	lz = L * z
	ci = lz' * lz
	# calculate D(G)
	d = centeredZ' * L * centeredZ
	# calculate P(G)
	p = centeredZ' * centeredZ
	# calculate C(G)
	c = z' * z
	# calculate I_dc(G)
	idc = d + c
	# END CALCULATION
	T = time() - T
	return T, ci, d, p, idc
end

function Approx(G, s; eps = 1e-6) # Returns T, z, aci, ad, ap, aidc
	T = time()
	IpL = getSparseIpL(G)
	sparseL = getSparseL(G)
	f = approxchol_sddm(IpL, tol=0.1*eps)
	avgs = sum(s)/G.n
	centeredS = zeros(G.n)
	for i = 1 : G.n
		centeredS[i] = s[i] - avgs
	end
	z = f(s)
	centeredZ = f(centeredS)

	# calculate aC_I(G)
	approxLz = sparseL * z
	aci = approxLz' * approxLz
	# calculate aD(G)
	ad = centeredZ' * sparseL * centeredZ
	# calculate aP(G)
	ap = centeredZ' * centeredZ
	# calculate aC(G)
	ac = z' * z
	# calculate aI_dc(G)
	aidc = ad + ac

	sumop = avgs * G.n
	norms = s' * s

	# END CALCULATION
	T = time() - T
	return T, z, aci, ad, ap, ac, aidc, sumop, avgs, norms
end

function doExp(G, s,  measuresFile, expressedOpinionsFile, numIterationsPageRank, pageRankPlotFile)
	T, z, aci, ad, ap, ac, aidc, sumop, avgop, norms = Approx(G, s)

	println(measuresFile, "time ", T)
	println(measuresFile, "aci ", aci)
	println(measuresFile, "ad ", ad)
	println(measuresFile, "ap ", ap)
	println(measuresFile, "ac ", ac)
	println(measuresFile, "aidc ", aidc)
	println(measuresFile, "sumop ", sumop)
	println(measuresFile, "avgop ", avgop)
	println(measuresFile, "norms ", norms)

	TPR, errorPR = doPageRank(G, s, z, numIterationsPageRank, pageRankPlotFile)

	println(measuresFile, "timePR ", TPR)
	println(measuresFile, "errorPR ", errorPR)

	writeVector(z, expressedOpinionsFile)

	return z
end

function doPageRank(G, s, zTrue, numIterations, errorPlotFile)
	T = time()
	A,d = getSparseAandD(G)
	Mvec = 1 ./ (1 .+ d)
	Ms = Mvec .* s

	# here, we set N = (I-M) * D^(-1)
	X = 1 .- Mvec
	dinv = 1 ./ d
	N = Diagonal(X .* dinv) * A

	diffZs = zeros(numIterations)
	diffIterates = zeros(numIterations)

	avgs = sum(s) / G.n
	zPageRank = fill(avgs, G.n)

	for t in 1:numIterations
		zPageRankOld = zPageRank
		zPageRank = Ms + N*zPageRank

		diffZs[t] = norm(zTrue - zPageRank)
		diffIterates[t] = norm(zPageRank - zPageRankOld)
	end
	T = time() - T

	println("Final error PageRank approximation: ", diffZs[numIterations])

	plot(1:numIterations, [diffZs diffIterates], label=["diffZs" "diffIterates"], xlabel="iteration", ylabel="error",yscale=:log10)
	savefig(errorPlotFile)

	return T,diffZs[numIterations]
end

function doLarge(G, s, lg)
	T2, aci, ad, ap, aidc = Approx(G, s)
	println(lg, "Approx Time : ", T2)
	println(lg)
end
