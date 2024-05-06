include("Graph.jl")

using Random
using LinearAlgebra
using SparseArrays

function powerLaw(n; alp = 2.5, xmin = 1)
    Random.seed!(round(Int, time() * 10000))
    x = rand(n)
    for i = 1 : n
        x[i] = xmin * ((1 - x[i])^(-1.0/(alp - 1.0)))
    end
    xm = x[argmax(x)]
    x ./= xm
    return x
end

function Uniform(n)
    Random.seed!(round(Int, time() * 10000))
    x = rand(n)
    return x
end

function Exponential(n; lmd = 1, xmin = 1)
    Random.seed!(round(Int, time() * 10000))
    x = rand(n)
    for i = 1 : n
        x[i] = xmin - (1.0/lmd)*log(1-x[i])
    end
    xm = x[argmax(x)]
    x ./= xm
    return x
end

function getW(G)
	L = zeros(G.n, G.n)
	for (ID, u, v, w) in G.E
		L[u, u] += w
		L[v, v] += w
		L[u, v] -= w
		L[v, u] -= w
	end
	for i = 1 : G.n
		L[i, i] += 1.0
	end
	return inv(L)
end

function getL(G)
	L = zeros(G.n, G.n)
	for (ID, u, v, w) in G.E
		L[u, u] += w
		L[v, v] += w
		L[u, v] -= w
		L[v, u] -= w
	end
	return L
end

function getSparseIpL(G)
    d = ones(G.n)
    for (ID, u, v, w) in G.E
        d[u] += w
        d[v] += w
    end
    Is = zeros(Int32, G.m*2+G.n)
    Js = zeros(Int32, G.m*2+G.n)
    Vs = zeros(G.m*2+G.n)
    for (ID, u, v, w) in G.E
        Is[ID] = u
        Js[ID] = v
        Vs[ID] = -w
        Is[ID + G.m] = v
        Js[ID + G.m] = u
        Vs[ID + G.m] = -w
    end
    for i = 1 : G.n
        Is[G.m + G.m + i] = i
        Js[G.m + G.m + i] = i
        Vs[G.m + G.m + i] = d[i]
    end
    return sparse(Is, Js, Vs, G.n, G.n)
end

function getSparseAandD(G)
    d = zeros(G.n)
    for (ID, u, v, w) in G.E
        d[u] += w
        d[v] += w
    end
    Is = zeros(Int32, G.m*2)
    Js = zeros(Int32, G.m*2)
    Vs = zeros(G.m*2)
    for (ID, u, v, w) in G.E
        Is[ID] = u
        Js[ID] = v
        Vs[ID] = w
        Is[ID + G.m] = v
        Js[ID + G.m] = u
        Vs[ID + G.m] = w
    end
    return sparse(Is, Js, Vs, G.n, G.n), d
end

function getSparseL(G)
    d = zeros(G.n)
    for (ID, u, v, w) in G.E
        d[u] += w
        d[v] += w
    end
    Is = zeros(Int32, G.m*2+G.n)
    Js = zeros(Int32, G.m*2+G.n)
    Vs = zeros(G.m*2+G.n)
    for (ID, u, v, w) in G.E
        Is[ID] = u
        Js[ID] = v
        Vs[ID] = -w
        Is[ID + G.m] = v
        Js[ID + G.m] = u
        Vs[ID + G.m] = -w
    end
    for i = 1 : G.n
        Is[G.m + G.m + i] = i
        Js[G.m + G.m + i] = i
        Vs[G.m + G.m + i] = d[i]
    end
    return sparse(Is, Js, Vs, G.n, G.n)
end

function writeVector(v, file)
	for i = 1 : length(v)
		println(file, v[i])
	end
end

function myPowerIteration(A, max_iterations, tolerance, v=nothing)
    # Initial guess for the eigenvector
    x = rand(size(A, 1))

    for i in 1:max_iterations
        x_new = A * x

        if v != nothing
            x_new = x_new - dot(x_new, v) * v
        end

        x_new_norm = norm(x_new)
        x_new = x_new / x_new_norm
        if abs(dot(x_new, x)) < tolerance
            break
        end
        x = x_new
    end

    # Compute the largest eigenvalue
    lambda_max = dot(x, A * x) / dot(x, x)

    return lambda_max, x
end

function approximateConditionNumber(A, max_iterations, tolerance)
	lambda_max, x = myPowerIteration(A, max_iterations, tolerance)
	B = A - lambda_max * I
	lambda_min, y = myPowerIteration(B, max_iterations, tolerance)
	conditionNumber = lambda_max / (lambda_min + lambda_max)

	return conditionNumber
end

function eigenvalueOpinions(G)
	L = getSparseL(G)

	max_iterations = 1000
	tolerance = 1e-6

	lambda_max, x = myPowerIteration(L, max_iterations, tolerance)

	B = L - lambda_max * I
	firstEigenvector = ones(size(B, 1)) / sqrt(size(B, 1))
	lambda_min, y = myPowerIteration(B, max_iterations, tolerance, firstEigenvector)
	lambda_min += lambda_max

	y = y .- minimum(y)
	y = y ./ maximum(y)

	return y
end

function plotOpinionHistogram(z, path)
	# Plot a histogram of the data
	histogram(z, bins=20, xlabel="Opinions", ylabel="Frequency")
	savefig(path)
end
