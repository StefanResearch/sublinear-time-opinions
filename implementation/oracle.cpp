/*
 * compile with
 * 		g++-11 -O3 -Wall -fopenmp -std=c++11 oracle.cpp -o oracle
 */
#include <fstream>
#include <iostream>

#include <map>
#include <string>
#include <tuple>
#include <queue>
#include <vector>

#include <algorithm>
#include <random>

#include <cstring>
#include <math.h>
#include <stdlib.h>
#include <time.h>
#include <chrono>

#include <omp.h>

typedef long vertexId;
class Graph {
	public:
		std::vector<double> degrees;
		std::vector< std::vector<vertexId> > neighbors;
		std::vector< std::vector<double> > cumulativeDegrees;
};


long numSteps;
long numWalks;
long numEstNorm;

Graph readGraph(std::string graphfile);
void addEdge(Graph& G, vertexId u, vertexId v, double weight);
void addVertexIfNotExisting(Graph& G, vertexId u);
std::vector<double> readOpinions(std::string filepath);

double estExpressedOpinion(Graph& G, vertexId u, std::vector<double>& s);
std::map<vertexId,double> estExpressedOpinions(Graph& G, std::vector< vertexId > vertices, std::vector<double>&s);
std::map<vertexId,double> estAllExpressedOpinions(Graph& G, std::vector<double>&s);

vertexId uniformlyRandomNeighbor(Graph& G, vertexId u, double moveToTake);

std::default_random_engine generator;

Graph readGraph(std::string graphfile) {
	Graph G;

	std::ifstream inputfile(graphfile);
	if (inputfile.fail()) {
		std::cout << "ERROR: Could not open input file: " << graphfile << std::endl;
		return G;
	}

	vertexId n;
	inputfile >> n;

	G.degrees = std::vector<double>(n,1);
	G.neighbors = std::vector< std::vector<vertexId> >(n, std::vector<vertexId>() );

	vertexId u, v;
	double weight;
	while (inputfile >> u >> v >> weight) {
		addEdge(G, u, v, weight);
	}

	return G;
}

void addEdge(Graph& G, vertexId u, vertexId v, double weight) {
	G.neighbors[u].push_back(v);
	G.neighbors[v].push_back(u);

	G.degrees[u] += weight;
	G.degrees[v] += weight;
}

std::vector<double> readOpinions(std::string filepath)
{
	std::vector<double> opinions;

	std::ifstream inputfile(filepath);
	if (inputfile.fail()) {
		std::cout << "ERROR: Could not open input file: " << filepath << std::endl;
		return opinions;
	}

	double opinion;
	while (inputfile >> opinion) {
		opinions.push_back(opinion);
	}

	return opinions;
}

int
main(int argc, char** argv) {
	// parse the command line input
	std::string graphFilePath(argv[1]);
	numSteps = strtol(argv[2],NULL,10);
	numWalks = strtol(argv[3],NULL,10);
	std::string innateOpinionsFilePath(argv[4]);

	Graph G = readGraph(graphFilePath);
	std::vector<double> s = readOpinions(innateOpinionsFilePath);

	generator.seed(std::chrono::system_clock::now().time_since_epoch().count());

	auto startTime = std::chrono::high_resolution_clock::now();

	std::map<vertexId,double> opinions;
	if (strcmp(argv[5], "--estAllOpinions") == 0) {
		opinions = estAllExpressedOpinions(G, s);
	} else {
		std::vector< vertexId > vertices;

		for (long i=5; i<argc; i++) {
			vertexId u = (vertexId)strtol(argv[i],NULL,10);
			vertices.push_back(u);
		}

		opinions = estExpressedOpinions(G, vertices, s);
	}

	auto endTime = std::chrono::high_resolution_clock::now();
	auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endTime - startTime);
	std::cout << (double)duration.count()/1000000 << std::endl;

	for (auto vertexOpinion : opinions) {
		vertexId u = vertexOpinion.first;
		double opinion = vertexOpinion.second;

		std::cout << u << " " << opinion << std::endl;
	}

	return 0;
}

std::map<vertexId,double> estAllExpressedOpinions(Graph& G, std::vector<double>&s) {
	std::vector< vertexId > vertices;
	for (long unsigned int i = 0; i < G.neighbors.size(); i++) {
		vertices.push_back(i);
	}

	return estExpressedOpinions(G, vertices, s);
}

std::map<vertexId,double> estExpressedOpinions(Graph& G,
										 std::vector< vertexId > vertices,
										 std::vector<double>&s) {
	std::map<vertexId,double> opinions;
	for (auto vertex : vertices) {
		opinions[vertex] = 0;
	}

	#pragma omp parallel for
	for (auto vertex : vertices) {
		opinions[vertex] = estExpressedOpinion(G, vertex, s);
	}

	return opinions;
}

double estExpressedOpinion(Graph& G, vertexId u, std::vector<double>& s) {
	double x_u = 0;

	std::uniform_real_distribution<double> uniformDistribution(0.0,1.0);

	// perform all random walks
	for (long i=0; i<numWalks; i++) {
		vertexId currentVertex = u;
		long remainingSteps = numSteps;
		double x_walk = 0;

		while (remainingSteps > 0) {
			// update x_walk for the vertex we are currently at
			x_walk += (s[currentVertex] / G.degrees[currentVertex]);

			double moveToTake = uniformDistribution(generator);

			remainingSteps -= 1;
			if (moveToTake > 0.5) { // perform a self loop
				continue;
			} else { // go to a random neighbor
				currentVertex = uniformlyRandomNeighbor(G, currentVertex, moveToTake);
				if (currentVertex == -1) {
					remainingSteps = 0;
					break;
				}
			}
		}

		x_u += x_walk;
	}

	x_u = x_u / (2*numWalks);

	return x_u;
}

vertexId uniformlyRandomNeighbor(Graph& G, vertexId u, double moveToTake) {
	vertexId n = G.neighbors[u].size();

	moveToTake = 2*moveToTake;
	vertexId neighborIndex = (vertexId)std::floor(moveToTake*(n+1));

	if (neighborIndex >= n) {
		return -1;
	} else {
		return G.neighbors[u][neighborIndex];
	}
}

