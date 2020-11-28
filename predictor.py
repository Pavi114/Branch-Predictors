from constants import *

class Predictor(object):
    def __init__(self):
        self.mispredictions = 0
        self.right_predictions = 0
        self.accuracy = 0
    
    def calc_accuracy(self):
        self.accuracy = (1.0 * self.right_predictions) / float(self.mispredictions + self.right_predictions) * 100
    
    def increment_misprediction(self):
        self.mispredictions += 1
    
    def increment_right_predictions(self):
        self.right_predictions += 1
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        pass
    
    def update_performance(self, expected_outcome, actual_outcome):
        if int(expected_outcome) != int(actual_outcome):
            self.increment_misprediction()
        else:
            self.increment_right_predictions()
    
    def print_performance_analysis(self):
        s = 'Number of Mispredictions: {}\n'.format(self.mispredictions)
        s += 'Number of Correct Predictions: {}\n'.format(self.right_predictions)
        s += 'Accuracy: {}\n'.format(round(self.accuracy, 2))
        return s

class BranchTaken(Predictor):
    def __init__(self):
        super(BranchTaken, self).__init__()
        self.outcome = TAKEN
    
    def predict(self, target_address):
        return self.outcome
    
    def print_performance_analysis(self):
        s = 'Static Branch Prediction: Always Taken\n'
        s += Predictor.print_performance_analysis(self)
        print(s)

class BranchNotTaken(Predictor):
    def __init__(self):
        super(BranchNotTaken, self).__init__()
        self.outcome = NOT_TAKEN
    
    def predict(self, target_address):
        return self.outcome
    
    def print_performance_analysis(self):
        s = 'Static Branch Prediction: Always Not Taken\n'
        s += Predictor.print_performance_analysis(self)
        print(s)

class OneBitPredictor(Predictor):
    def __init__(self, ls_bits):
        super(OneBitPredictor, self).__init__()
        self.ls_bit_size = ls_bits
        self.branch_history_table_size = 2**ls_bits
        self.branch_history_table = [0 for i in range(self.branch_history_table_size)]
    
    def predict(self, target_address):
        lsb = int(target_address[-self.ls_bit_size:], 2)
        if self.branch_history_table[int(lsb)]:
            return TAKEN
        return NOT_TAKEN

    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        lsb = int(target_address[-self.ls_bit_size:], 2)
        self.branch_history_table[int(lsb)] = actual_outcome
    
    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: One level predictor using one bit\n'
        s += Predictor.print_performance_analysis(self)
        print(s)

class TwoBitPredictor(Predictor):
    def __init__(self, ls_bits):
       super(TwoBitPredictor, self).__init__()
       self.ls_bit_size = ls_bits
       self.branch_history_table_size = 2**ls_bits
       self.branch_history_table = [0 for i in range(self.branch_history_table_size)] 
    
    def predict(self, target_address):
        lsb = int(target_address[-self.ls_bit_size:], 2)        
        prediction = self.branch_history_table[int(lsb)]
        if prediction == STRONGLY_TAKEN or prediction == WEAKLY_TAKEN:
            return TAKEN
        if prediction == STRONGLY_NOT_TAKEN or prediction == WEAKLY_NOT_TAKEN:
            return NOT_TAKEN
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        lsb = int(target_address[-self.ls_bit_size:], 2)
        if actual_outcome == TAKEN:
            if predicted_outcome == NOT_TAKEN or self.branch_history_table[lsb] == WEAKLY_TAKEN:
                self.branch_history_table[lsb] = (self.branch_history_table[lsb] + 1) % 4
        elif predicted_outcome == TAKEN or self.branch_history_table[lsb] == WEAKLY_NOT_TAKEN:
            self.branch_history_table[lsb] = (self.branch_history_table[lsb] - 1) % 4
    
    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: Two Bit\n'
        s += 'Branch History Table size: {}\n'.format(self.branch_history_table_size)
        s += Predictor.print_performance_analysis(self)
        print(s)


class GSharePredictor(Predictor):
    def __init__(self, m, n):
        super(GSharePredictor, self).__init__()
        self.m = m
        self.n = n
        self.max_val = pow(2, n)
        self.global_branch_history = 0 #m-bit register
        self.global_history_table = [0 for i in range(pow(2, self.m))] # n bit each in 2^m entries

    def predict(self, target_address):
        lsb = int(target_address[-self.m:], 2)
        index = lsb ^ self.global_branch_history
        if self.global_history_table[index] >= self.max_val / 2:
           return TAKEN
        return NOT_TAKEN
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        lsb = int(target_address[-self.m:], 2)
        index = lsb ^ self.global_branch_history
        if actual_outcome == TAKEN and self.global_history_table[index] < self.max_val - 1:
            self.global_history_table[index] += 1
        elif actual_outcome == NOT_TAKEN and self.global_history_table[index] > 0:
            self.global_history_table[index] -= 1
        self.global_branch_history = (self.global_branch_history << 1) | actual_outcome
        self.global_branch_history = self.global_branch_history & self.max_val
    
    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: Two Level Correlating Predictor (GShare)\n'
        s += Predictor.print_performance_analysis(self)
        print(s)