def convert_hex_to_bin(hex):
    scale = 16
    num_of_bits = 32
    return bin(int(hex, scale))[2:].zfill(num_of_bits)

def start_prediction(file_object, predictor):
    i = 0
    while True:
        x = file_object.readline()
        x = x.rstrip()
        if not x:
            break
        i = i + 1

        (target_address, actual_outcome) = x.split(' ')
        actual_outcome = 1 if actual_outcome == 'T' else 0

        target_address = int(target_address)

        prediction = predictor.predict(target_address)

        predictor.update_bht(target_address=target_address, actual_outcome=actual_outcome, predicted_outcome=prediction)

        predictor.update_performance(prediction, actual_outcome)
    
    predictor.calc_accuracy()