from predictor import *
from helpers import start_prediction

import sys

predictor_types = {
    'BranchTaken': BranchTaken(),
    'BranchNotTaken': BranchNotTaken(), 
    'OneBitPredictor': OneBitPredictor(ls_bits=14), 
    'TwoBitPredictor': TwoBitPredictor(ls_bits=13), 
    'CorrelationPredictor': CorrelationPredictor(m=6, n=7),
    'GSharePredictor': GSharePredictor(m=13, n=13),
    'TournamentPredictor': TournamentPredictor(m=11, n=11, ls_bits=12)
}

for predictor_type, predictor in predictor_types.items():
    with open(sys.argv[1], 'r') as f:
        start_prediction(file_object=f, predictor=predictor)
        predictor.print_performance_analysis()