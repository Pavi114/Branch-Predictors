from predictor import *
from helpers import start_prediction

predictor_types = {
    # 'BranchTaken': BranchTaken(),
    # 'BranchNotTaken': BranchNotTaken(), 
    # 'OneBitPredictor': OneBitPredictor(ls_bits=3), 
    'TwoBitPredictor': TwoBitPredictor(ls_bits=3), 
    # 'GSharePredictor': GSharePredictor(m=3, n=4)
}

with open('./data/branch-trace-gcc.trace', 'r') as f:
    for predictor_type, predictor in predictor_types.items():
        start_prediction(file_object=f, predictor=predictor)
        predictor.print_performance_analysis()
        print("hii")