# Implementation of Branch Prediction Schemes

The following branch prediction schemes were implemented and tested using the **spec95 gcc int** benchmark. 

## Static Branch Prediction
The outcome of the branch is determined at the compile stage.

### Branch Always Taken
The branch instructions are predicted to be taken at the compile time.

### Branch Always Not Taken
The branch instructions are predicted to be not taken at the compile time.

## Dynamic Branch Prediction
In the case of dynamic branch prediction, the hardware measures the actual branch behavior by recording the recent history of each branch in a **branch prediction buffer**, assumes that the future behavior will continue the same way and make predictions.

### 1-bit Predictor
- The Branch History Table (BHT) or Branch Prediction Buffer stores 1-bit values to indicate whether the branch is predicted to be taken / not taken. 
- **Prediction**: The lower bits of the PC address (here ls_bits) index this table of 1-bit values and get the prediction. 
- **Updation of Table**: If the prediction is wrong, the indexed position is updated with the actual outcome of the branch.

### 2-Bit Predictor
- Two bits are maintained in the prediction buffer and there are four different states namely, **Strongly Taken (11), Weakly Taken (10), Weakly Not-Taken (01) and, Strongly Not Taken (00)**. This predictor changes prediction only on two successive mispredictions (Strongly taken and weakly taken are interpreted as taken).
- Table is initially as strongly not taken(00).
- **Prediction**: The lower bits of the PC address (here ls_bits) index this table of 2-bit values and get the prediction. 
- **Updation of Table**:  Updation of the bits in the indexed position happens according to the state diagram:
        ![img](2bit.png)

### GShare Predictor (GShare)
- When behavior of one branch is dependent on the behavior of other branches, they are said to be correlated.
- Gshare uses a **m-bit** history register to record the taken/not-taken history of the last m branches.
- Table is initially as strongly not taken(00).
- **Prediction**: Gshare uses **xor** of the lowest m of the of the PC the history register as the index. Rest of the prediction happens similar to 2-bit predictor.
- **Updation of table**: Updation of bits in the branch history table happens similar to the 2-bit predictor scheme. The branch history register is updated by shifting in the most recent conditional branch outcome into the low-order bits.

### Correlation Predictor 
- When behavior of one branch is dependent on the behavior of other branches, they are said to be correlated.
- It uses a **m-bit** history register to record the taken/not-taken history of the last m branches.
- Table is initially as strongly not taken(00).
- **Prediction**: Correlating predictor uses the **concatenation** of lowest m / 2 bits of the PC and the history register as the index. Rest of the prediction happens similar to 2-bit predictor.
- **Updation of table**: Updation of bits in the branch history table happens similar to the 2-bit predictor scheme. The branch history register is updated by shifting in the most recent conditional branch outcome into the low-order bits.

### Tournament Predictor
- This predictor uses the concept of _predicting the predictor_ i.e selects the right predictor for a particular branch. In this implementation, three tables are used. 
    - A 2-bit Predictor table to perform 2-bit prediction
    - GShare table to perform gshare prediction
    - Chooser table that predicts whether the 2-bit or gshare predictor will be more accurate

- So, the chooser is a table of two-bit saturating counters indexed by the low-order bits of the PC (ls_bits) that determines which of the other two table's prediction to return. 
- For the chooser, the two-bit counter encodes: **strongly prefer 2-bit (00), weakly prefer 2-bit (01), weakly prefer gshare (10), and strong prefer gshare (11)**.
- Intially, the chooser table is initialized to **strongly prefer 2-bit**.
- **Prediction**: Access the chooser table using the low-order bits of the branch's PC address. In parallel, the 2-bit and gshare tables are accessed just as normal predictors and they both generate an independent prediction. Based on the result of the lookup in the chooser table, the final prediction is either the prediction from the 2-bit predictor or the prediction from the gshare predictor.
- **Updation of Tables**: Both the gshare and 2-bit predictors are trained on every branch using their normal training algorithm. The choose predictor is trained toward which of the two predictors was more accurate on that specific prediction:
    - If the two predictors make the same prediction either both predictors were correct or both predictors were wrong. In both cases, the chooser table isn't updated.
    - If the two predictors made different predictions (thus, one of the predictors was correct and the other incorrect) the chooser counter is updated (incremented or decremented by one) toward preferring that of the predictor that was correct.

## Implementation
Python was used to implement the above branch predictors and analyse it's performance. A trace of spec95 gcc int benchmark comprising 16M instructions along with the output is stored in the ```./sample``` folder along with the IOs. 

| Outcome   |   %  |
|-----------|------|
| Taken     | ~38% |
| Not Taken | ~62% |


## Analysis
### Size vs Mis-prediction rate:
|            | 1-bit | 2-bit | correlation | gshare | tournament |
|:----------|:-----:|:-----:|:-----------:|:------:|:----------:|
|  128 bits  | 28.15 | 27.62 |    29.39    |  31.51 |    30.35   |
|  256 bits  | 25.87 | 24.96 |    27.18    |  30.1  |    28.41   |
|  512 bits  | 22.89 | 22.13 |    25.36    |  28.28 |    25.89   |
|  1024 bits |  19.8 | 18.95 |    21.65    |  25.2  |    22.42   |
|  2048 bits | 17.47 | 15.95 |    18.57    |  21.25 |    19.0    |
|  4096 bits | 15.87 | 13.88 |    14.83    |  17.52 |    15.25   |
|  8192 bits | 15.13 | 12.48 |    12.44    |  13.4  |    12.13   |
| 16394 bits | 14.54 | 11.85 |     9.9     |  10.06 |     9.6    |


### Size vs Accuracy

|          | 1-bit | 2-bit | correlation | gshare | tournament |
|:----------|:-----:|:-----:|:-----------:|:------:|:----------:| 
| 128 bits | 71.85 | 72.38 | 70.61 | 68.49 | 69.65 |
| 256 bits | 74.13 | 75.04 | 72.82 | 69.9 | 71.59 | 
| 512 bits | 77.11 | 77.87 | 74.64 | 71.72 | 74.11 | 
| 1024 bits | 80.2 | 81.05 | 78.35 | 74.8 | 77.58 | 
| 2048 bits | 82.53 | 84.05 | 81.43 | 78.75 | 81.0 | 
| 4096 bits | 84.13 | 86.12 | 85.17 | 82.48 | 84.75 | 
| 8192 bits   | 84.87 | 87.52 | 87.56 | 86.6 | 87.87 | 
| 16394 bits | 85.46 | 88.15 | 90.1 | 89.94 | 90.4 |


## Observation and Inference
- The five schemes have accuracy / mis-prediction curves of similar shape for a given buffer size. The differences between their prediction accuracies are somewhat predictable. Since the performance of static predictor on a program is solely determined by the program's branch behavior, we can conclude that the branch behavior of a program is the most important parameter in determining the prediction accuracy of each scheme.
- The effect of varying the buffer size over five dynamic schemes is given in the graph below. 
    - The curve for the bimodal (1-bit and 2-bit) schemes goes flat when the number of n-bit counters gets above about 6000.  Therefore, for the bimodal scheme, buffer size is not a limiting factor when it is more than 8K bits.
    - The common correlation scheme, GShare and Tournament scheme has noticeable improvement in performance with increased buffer size.

    ![fig](./samples/size-vs-accuracy.png)  
    
    ![fig](./samples/size-vs-misrate.png)

## Conclusion
Different Branch Prediction algorithms were simulated and their performance and accuracy was analysed at different size intervals with respect to each other.