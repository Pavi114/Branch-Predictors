from predictor import *
from helpers import start_prediction

predictor_types = {
    'BranchTaken': BranchTaken(),
    'BranchNotTaken': BranchNotTaken(), 
    'OneBitPredictor': OneBitPredictor(ls_bits=13), 
    'TwoBitPredictor': TwoBitPredictor(ls_bits=12), 
    'CorrelationPredictor': CorrelationPredictor(m=6, n=6),
    'GSharePredictor': GSharePredictor(m=12, n=12),
    'TournamentPredictor': TournamentPredictor(m=4, n=10, ls_bits=11)
}

for predictor_type, predictor in predictor_types.items():
    with open('./data/branch-trace-gcc.trace', 'r') as f:
        start_prediction(file_object=f, predictor=predictor)
        predictor.print_performance_analysis()