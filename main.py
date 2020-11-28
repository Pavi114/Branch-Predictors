from predictor import *
from helpers import start_prediction

predictor_types = {
    'BranchTaken': BranchTaken(),
    'BranchNotTaken': BranchNotTaken(), 
    'OneBitPredictor': OneBitPredictor(ls_bits=3), 
    'TwoBitPredictor': TwoBitPredictor(ls_bits=3), 
    'GSharePredictor': GSharePredictor(m=2, n=2)
}

for predictor_type, predictor in predictor_types.items():
    f = open('./samples/branch-trace-gcc', 'r')
    start_prediction(file_object=f, predictor=predictor)
    predictor.print_performance_analysis()
    print("hii")