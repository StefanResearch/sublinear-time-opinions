import Eval
import Disagreement

datasets = ['Advogato','GooglePlus','TwitterFollows','YouTube','Flickr','Pokec','Flixster','LiveJournal']

opinionDistributions = ['Uniform','Eigenvalue','Exponential']

Eval.runExperiments(datasets, opinionDistributions)
Eval.runExperimentsWithDegreeBuckets(datasets, opinionDistributions)
Disagreement.runExperimentsDisagreement(datasets, opinionDistributions)

