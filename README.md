# Sublinear-Time Opinion Estimation in the Friedkin--Johnsen Model

This is the code for the WebConf'24 paper ``Sublinear-Time Opinion Estimation in
the Friedkin--Johnsen Model'' by Stefan Neumann, Yinhao Dong, and Pan Peng,
which is also available on [arxiv](https://arxiv.org/abs/2404.16464).

When using our code, please cite our paper.

To run our code, proceed with the following steps:
1. Download the datasets from [GitHub](https://github.com/Accelerator950113/OpinionQuantities/tree/main/data) and from the [Network Repository](https://networkrepository.com). Put the datasets into the directory `/include/OpinionQuantities-mine/data/`.
2. Move to the directory `include/OpinionQuantities-mine` and then type `zsh generateDatasets.sh`.
3. Go to `implementation/` and build the C++ oracle by typing `g++-11 -O3 -Wall -fopenmp -std=c++11 oracle.cpp -o oracle`.
4. Now you can run the experiments by typing `python3 main.py`.

