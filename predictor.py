from constants import *

class Predictor(object):
    def __init__(self):
        self.mispredictions = 0
        self.right_predictions = 0
        self.accuracy = 0
    
    def calc_accuracy(self):
        return (1.0 * self.mispredictions) / (self.mispredictions + self.right_predictions) * 100
    
    def increment_misprediction(self):
        self.mispredictions += 1
    
    def increment_right_predictions(self):
        self.right_predictions += 1

class BranchTaken(Predictor):
    def __init__(self):
        super.__init__()
        self.outcome = TAKEN
    
    def predict(self, target_address):
        return self.outcome

class BranchNotTaken(Predictor):
    def __init__(self):
        super.__init__()
        self.outcome = NOT_TAKEN
    
    def predict(self, target_address):
        return self.outcome

class OneBitPredictor(Predictor):
    def __init__(self, ls_bits):
        super.__init__()
        self.ls_bit_size = ls_bits
        self.branch_history_table_size = 2**ls_bits
        self.branch_history_table = [0 for i in self.branch_history_table_size]
    
    def predict(self, target_address):
        lsb = target_address[:-self.ls_bit_size]
        if self.branch_history_table[int(lsb)]:
            return TAKEN
        return NOT_TAKEN

    def update_bht(self, target_address, actual_outcome):
        lsb = target_address[:-self.ls_bit_size]
        self.branch_history_table[int(lsb)] = actual_outcome

class TwoBitPredictor(Predictor):
    def __init__(self, ls_bits):
       self.ls_bit_size = ls_bits
       self.branch_history_table_size = 2**ls_bits
       self.branch_history_table = [0 for i in self.branch_history_table_size] 
    
    def predict(self, target_address):
        lsb = target_address[:-self.ls_bit_size]
        prediction = self.branch_history_table[int(lsb)]
        if prediction == STRONGLY_TAKEN or prediction == WEAKLY_TAKEN:
            return TAKEN
        if prediction == STRONGLY_NOT_TAKEN or prediction == WEAKLY_NOT_TAKEN:
            return NOT_TAKEN
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        lsb = target_address[:-self.ls_bit_size]
        if actual_outcome == TAKEN:
            if predicted_outcome == NOT_TAKEN or self.branch_history_table[lsb] == WEAKLY_TAKEN:
                self.branch_history_table[lsb] = (self.branch_history_table[lsb] + 1) % 4
        elif predicted_outcome == TAKEN or self.branch_history_table[lsb] == WEAKLY_NOT_TAKEN:
            self.branch_history_table[lsb] = (self.branch_history_table[lsb] - 1) % 4


class CorrelatingPredictor(Predictor):
    def __init__(self, m, n, ls_bits):
        super.__init__()
        self.m = m
        self.n = n
        self.max_val = pow(2, n)
        self.global_branch_history = 0 #m-bit register
        self.global_history_table = [0 for i in pow(2, self.m)] # n bit each in 2^m entries

    def predict(self, target_address):
        lsb = target_address[:-self.m]
        index = lsb ^ self.global_branch_history
        if self.global_history_table[index] >= self.max_val / 2:
           return TAKEN
        return NOT_TAKEN
    
    def update_bht(self, target_address, actual_outcome):
        lsb = target_address[:-self.m]
        index = lsb ^ self.global_branch_history
        if actual_outcome == TAKEN and self.global_history_table[index] < self.max_val - 1:
            self.global_history_table[index] += 1
        elif actual_outcome == NOT_TAKEN and self.global_history_table[index] > 0:
            self.global_history_table[index] -= 1
        self.global_branch_history = (self.global_branch_history << 1) | actual_outcome

