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
        s = '\tNumber of Mispredictions: {}\n'.format(self.mispredictions)
        s += '\tNumber of Correct Predictions: {}\n'.format(self.right_predictions)
        s += '\tAccuracy: {}%\n'.format(round(self.accuracy, 2))
        s += '\tMisprediction Rate: {}%\n'.format(round(100 - round(self.accuracy, 2), 2))
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
        self.n = ls_bits

        self.lsb = pow(2, ls_bits) - 1

        self.branch_history_table_size = 2**ls_bits
        self.branch_history_table = [0 for i in range(self.branch_history_table_size)]
    
    def predict(self, target_address):
        index = target_address & self.lsb

        return self.branch_history_table[index]

    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        index = target_address & self.lsb

        self.branch_history_table[index] = actual_outcome
    
    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: One level bimodal predictor using one bit\n'
        s += '\tCounter Bits (n) = {}\n'.format(self.n)
        s += '\tTotal Size = {} bits\n'.format(2**(self.n))
        s += Predictor.print_performance_analysis(self)
        print(s)

class TwoBitPredictor(Predictor):
    def __init__(self, ls_bits):
        super(TwoBitPredictor, self).__init__()
        self.n = ls_bits

        self.lsb = pow(2, ls_bits) - 1

        self.branch_history_table_size = 2**ls_bits
        self.branch_history_table = [0 for i in range(self.branch_history_table_size)] 
    
    def predict(self, target_address):
        index = target_address & self.lsb

        prediction = self.branch_history_table[index]
        if prediction == STRONGLY_TAKEN or prediction == WEAKLY_TAKEN:
            return TAKEN
        if prediction == STRONGLY_NOT_TAKEN or prediction == WEAKLY_NOT_TAKEN:
            return NOT_TAKEN
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        index = target_address & self.lsb

        prediction = self.branch_history_table[index]
        if actual_outcome == TAKEN and prediction != STRONGLY_TAKEN:
            self.branch_history_table[index] += 1
        elif actual_outcome == NOT_TAKEN and prediction != STRONGLY_NOT_TAKEN:
            self.branch_history_table[index] -= 1
    
    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: One level bimodal predictor using two bits\n'
        s += '\tCounter Bits (n) = {}\n'.format(self.n)
        s += '\tTotal Size = {} bits\n'.format(2 * 2**(self.n))
        s += Predictor.print_performance_analysis(self)
        print(s)


class CorrelationPredictor(Predictor):
    def __init__(self, m, n):
        super(CorrelationPredictor, self).__init__()
        self.m = m
        self.n = n

        self.history_length = m
        self.num_counters = n

        self.global_branch_history = 0
        self.history_table = [
            [NOT_TAKEN for j in range(pow(2, n))] for i in range(pow(2, m))
        ]

        self.n_sig_bits = pow(2, n) - 1
        self.m_sig_bits = pow(2, m) - 1

    def predict(self, target_address):
        h_index = self.global_branch_history & self.m_sig_bits
        t_index = target_address & self.n_sig_bits

        prediction = self.history_table[h_index][t_index]

        if prediction == STRONGLY_TAKEN or prediction == WEAKLY_TAKEN:
            return TAKEN
        elif prediction == STRONGLY_NOT_TAKEN or prediction == WEAKLY_NOT_TAKEN:
            return NOT_TAKEN
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        h_index = self.global_branch_history & self.m_sig_bits
        t_index = target_address & self.n_sig_bits

        prediction = self.history_table[h_index][t_index]

        if actual_outcome == TAKEN and prediction != STRONGLY_TAKEN:
            self.history_table[h_index][t_index] += 1
        elif actual_outcome == NOT_TAKEN and prediction != STRONGLY_NOT_TAKEN:
            self.history_table[h_index][t_index] -= 1

        self.global_branch_history = (self.global_branch_history << 1) | actual_outcome
        self.global_branch_history = self.global_branch_history & self.m_sig_bits
    
    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: Two Level Correlation Predictor\n'
        s += '\tHistory Bits (m) = {}, Counter Bits (n) = {}\n'.format(self.m, self.n)
        s += '\tTotal Size = {} bits\n'.format(2 * 2**(self.m + self.n))
        s += Predictor.print_performance_analysis(self)
        print(s)
    

class GSharePredictor(Predictor):
    def __init__(self, m, n):
        super(GSharePredictor, self).__init__()
        self.m = m
        self.n = n

        self.history_length = m
        self.num_counters = n
        self.global_branch_history = 0 # m-bit register
        self.global_history_table = [NOT_TAKEN for i in range(pow(2, n))] # 2 bit each in 2^n entries
        self.n_sig_bits = pow(2, n) - 1
        self.m_sig_bits = pow(2, m) - 1

    def print_table_state(self):
        s = ''
        for t in self.global_history_table:
            if t == STRONGLY_TAKEN:
                s += 'T'
            elif t == WEAKLY_TAKEN:
                s += 't'
            elif t == WEAKLY_NOT_TAKEN:
                s += 'n'
            else:
                s += 'N'
        print(s, end=" | ")

    def predict(self, target_address):
        index = (int(target_address) ^ self.global_branch_history) & self.n_sig_bits

        prediction = self.global_history_table[index]

        if prediction == STRONGLY_TAKEN or prediction == WEAKLY_TAKEN:
            return TAKEN
        elif prediction == STRONGLY_NOT_TAKEN or prediction == WEAKLY_NOT_TAKEN:
            return NOT_TAKEN
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        index = (int(target_address) ^ self.global_branch_history) & self.n_sig_bits

        prediction = self.global_history_table[index]

        if actual_outcome == TAKEN and prediction != STRONGLY_TAKEN:
            self.global_history_table[index] += 1
        elif actual_outcome == NOT_TAKEN and prediction != STRONGLY_NOT_TAKEN:
            self.global_history_table[index] -= 1

        self.global_branch_history = (self.global_branch_history << 1) | actual_outcome
        self.global_branch_history = self.global_branch_history & self.m_sig_bits
    
    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: Two Level Correlating Predictor (GShare)\n'
        s += '\tHistory Bits (m) = {}, Counter Bits (n) = {}\n'.format(self.m, self.n)
        s += '\tTotal Size = {} bits\n'.format(2 * 2**self.n)
        s += Predictor.print_performance_analysis(self)
        print(s)
    
class TournamentPredictor(Predictor):
    def __init__(self, m, n, ls_bits):
        super(TournamentPredictor, self).__init__()
        self.m = m
        self.n = n
        self.ls_bits = ls_bits

        self.lsb = 2**ls_bits - 1
        self.gshare = GSharePredictor(m, n)
        self.two_bit = TwoBitPredictor(n)
        self.chooser = [STRONGLY_BIMODAL for i in range(2**ls_bits)]
    
    def predict(self, target_address):
        index = target_address & self.lsb
        if self.chooser[index] <= WEAKLY_BIMODAL:
            return self.two_bit.predict(target_address)
        else:
            return self.gshare.predict(target_address)
    
    def update_bht(self, target_address, actual_outcome, predicted_outcome):
        gshare_predict = self.gshare.predict(target_address)
        two_bit_predict = self.two_bit.predict(target_address)
        index = target_address & self.lsb
        self.gshare.update_bht(target_address, actual_outcome, gshare_predict)
        self.two_bit.update_bht(target_address, actual_outcome, two_bit_predict)
        if gshare_predict == two_bit_predict:
            return
        if gshare_predict == actual_outcome and self.chooser[index] != 3:
            self.chooser[index] += 1
            return
        if two_bit_predict == actual_outcome and self.chooser[index] != 0:
            self.chooser[index] -= 1

    def print_performance_analysis(self):
        s = 'Dynamic Branch Prediction: Tournament Predictor\n'
        s += '\tHistory Bits (m) = {}, Counter Bits (n) = {}, Tournament Bits (t) = {}\n'.format(self.m, self.n, self.ls_bits)
        s += '\tTotal Size = {} bits\n'.format(2 * 2**self.ls_bits + 4 * 2**self.n)
        s += Predictor.print_performance_analysis(self)
        print(s)