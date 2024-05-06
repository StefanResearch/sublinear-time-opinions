struct Graph
    n :: Int32 # |V|
    m :: Int32 # |E|
    V :: Array{Int32, 1} # V[i] = Real Index of node i
    E :: Array{Tuple{Int32, Int32, Int32, Float64}, 1} # (ID, u, v, w) in Edge Set
end

function readGraph(fileName, graphType) # Read graph from a file | graphType = [weighted, unweighted]
    # Initialized
    n = 0
    origin = Dict{Int32, Int32}()
    label = Dict{Int32, Int32}()
    edge = Set{Tuple{Int32, Int32, Float64}}()

    getid(x :: Int32) = haskey(label, x) ? label[x] : label[x] = n += 1

    open(fileName) do f1
        for line in eachline(f1)
            # Read origin data from file
            buf = split(line)
            u = parse(Int32, buf[1])
            v = parse(Int32, buf[2])
            if graphType == "weighted"
                w = parse(Float64, buf[3])
            else
                w = 1.0
            end
            if u == v
                continue
            end
            # Label the node
            u1 = getid(u)
            v1 = getid(v)
            origin[u1] = u
            origin[v1] = v
            # Store the edge
            if u1 > v1
                u1, v1 = v1, u1
            end
            push!(edge, (u1, v1, w))
        end
    end

    # Store data into the struct Graph
    m = length(edge)
    V = Array{Int32, 1}(undef, n)
    E = Array{Tuple{Int32, Int32, Int32, Float64}, 1}(undef, m)

    for i = 1 : n
        V[i] = origin[i]
    end

    ID = 0
    for (u, v, w) in edge 
        ID = ID + 1
        E[ID] = (ID, u, v, w)
    end

    return Graph(n, m, V, E)
end

function BFS(st, g) # Search from the node st
    nodeSet = []
    visited = Array{Int8, 1}(undef, size(g, 1))
    fill!(visited, 0)
    push!(nodeSet, st)
    visited[st] = 1
    front = 1
    rear = 1
    while front <= rear
        u = nodeSet[front]
        front = front + 1
        for v in g[u]
            if visited[v] == 0
                visited[v] = 1
                rear = rear + 1
                push!(nodeSet, v)
            end
        end
    end
    return nodeSet
end

function getLCC(G :: Graph, graphFile) # Find the largest connected component
    # Create the Link Table
    g = Array{Array{Int32, 1}, 1}(undef, G.n)
    for i = 1 : G.n
        g[i] = []
    end
    for (ID, u, v, w) in G.E
        push!(g[u], v)
        push!(g[v], u)
    end

    # Find the nodeSet of the LCC
    n2 = 0
    largestCC = Array{Int32, 1}(undef, G.n)
    visited = Array{Int8, 1}(undef, G.n)
    fill!(visited, 0)
    for i = 1 : G.n
        if visited[i] == 0
            nodeSet = BFS(i, g)
            for x in nodeSet 
                visited[x] = 1
            end
            tn = size(nodeSet, 1)
            if (tn > n2)
                n2 = tn
                for j = 1 : n2
                    largestCC[j] = nodeSet[j]
                end
            end
        end
    end

    # Store the result
    label = Array{Int32, 1}(undef, G.n)
    fill!(label, 0)
    V2 = Array{Int32, 1}(undef, n2)
    for i = 1 : n2
        label[largestCC[i]] = i
        V2[i] = G.V[largestCC[i]]
    end
	println(graphFile, string(n2))
    E2 = []
    nID = 0
    for (ID, u, v, w) in G.E
        if (label[u] > 0) && (label[v] > 0)
            nID += 1
            push!(E2, (nID, label[u], label[v], w))

			# we are subtracting 1 from the labels to ensure that everything is
			# 0-indexed
			if graphFile != ""
				println(graphFile, string(label[u]-1, " ", label[v]-1, " ", w))
			end
        end
    end
    m2 = size(E2, 1)

    return Graph(n2, m2, V2, E2)
end
