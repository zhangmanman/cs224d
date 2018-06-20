import numpy as np
import random

from q1_softmax import softmax
from q2_gradcheck import gradcheck_naive
from q2_sigmoid import sigmoid, sigmoid_grad

def normalizeRows(x):
    """ Row normalization function """
    # Implement a function that normalizes each row of a matrix to have unit length
    
    ### YOUR CODE HERE
    temp = np.copy(x)
    temp = np.square(temp)
    temp = np.sum(temp, axis=1)
    temp = np.sqrt(temp)
    shape = temp.shape
    if (len(shape) == 1) :
        temp = np.resize(temp, (shape[0],1))

    x = np.divide(x, temp)
    # raise NotImplementedError
    ### END YOUR CODE
    
    return x

def test_normalize_rows():
    print "Testing normalizeRows..."
    x = normalizeRows(np.array([[3.0,4.0],[1, 2]])) 
    # the result should be [[0.6, 0.8], [0.4472, 0.8944]]
    print x
    assert (x.all() == np.array([[0.6, 0.8], [0.4472, 0.8944]]).all())
    print ""

def softmaxCostAndGradient(predicted, target, outputVectors, dataset):
    """ Softmax cost function for word2vec models """
    
    # Implement the cost and gradients for one predicted word vector  
    # and one target word vector as a building block for word2vec     
    # models, assuming the softmax prediction function and cross      
    # entropy loss.                                                   
    
    # Inputs:                                                         
    # - predicted: numpy ndarray, predicted word vector (\hat{v} in 
    #   the written component or \hat{r} in an earlier version)
    # - target: integer, the index of the target word               
    # - outputVectors: "output" vectors (as rows) for all tokens     
    # - dataset: needed for negative sampling, unused here.         
    
    # Outputs:                                                        
    # - cost: cross entropy cost for the softmax word prediction    
    # - gradPred: the gradient with respect to the predicted word   
    #        vector                                                
    # - grad: the gradient with respect to all the other word        
    #        vectors                                               
    
    # We will not provide starter code for this function, but feel    
    # free to reference the code you previously wrote for this        
    # assignment!                                                  
    
    ### YOUR CODE HERE
    gradPred = np.zeros(outputVectors.shape)
    grad = np.zeros(outputVectors.shape)

    temp = np.dot(predicted, outputVectors.T) ###1*5
    pxc = softmax(temp) ###1*5
    pxc.resize(5,1) ### 5*1
    pxc[target] -= 1  ###5*1
    expected = np.dot(pxc.T, outputVectors)  ###1*3

    cost = -np.log(pxc[target])
    gradPred = expected.flatten()
    grad = np.dot(pxc.T, outputVectors).flatten()

    # raise NotImplementedError
    ### END YOUR CODE
    
    return cost, gradPred, grad

def negSamplingCostAndGradient(predicted, target, outputVectors, dataset, 
    K=10):
    """ Negative sampling cost function for word2vec models """

    # Implement the cost and gradients for one predicted word vector  
    # and one target word vector as a building block for word2vec     
    # models, using the negative sampling technique. K is the sample  
    # size. You might want to use dataset.sampleTokenIdx() to sample  
    # a random word index. 
    # 
    # Note: See test_word2vec below for dataset's initialization.
    #                                       
    # Input/Output Specifications: same as softmaxCostAndGradient     
    # We will not provide starter code for this function, but feel    
    # free to reference the code you previously wrote for this        
    # assignment!
    
    ### YOUR CODE HERE
    # gradPred = np.zeros(outputVectors.shape)
    # grad = np.zeros(outputVectors.shape)
    #
    # uk = outputVectors[:K,:]   ###k*3
    # temp = np.dot(predicted, outputVectors.T).T ###5,
    # temp.resize(5,1)
    # sigmoidTemp = sigmoid(temp) ###5*1
    # tempK = temp[:K,:]     ###K*1
    # negTempK = np.multiply(temp[:K,:], -1)  ###K*1
    # sigmoidTempK = sigmoid(tempK)   ###K*1
    # sigmoidNegTempK = sigmoid(negTempK)  ###K*1
    # implementTempK = 1 - sigmoidNegTempK ###K*1
    #
    # cost = -np.log(sigmoidTemp[target]) - np.sum(np.log(sigmoidNegTempK))
    # gradPred = np.multiply((sigmoidTemp[target] - 1), outputVectors[target, :]) +  np.dot(implementTempK.T, uk).flatten()
    #
    # predicted2 = np.reshape(predicted, (1, 3))
    # grad[target, :] = np.multiply((1 - sigmoidTempK[target]), predicted)
    # # grad[target, :] = np.dot((sigmoidTempK - sigmoidNegTempK), predicted2)
    # grad[:K, :] = -np.dot((sigmoidNegTempK - 1), predicted2)

    cost = 0.0
    grad = np.zeros_like(outputVectors)
    gradPred = np.zeros_like(predicted)

    a_target = sigmoid(np.dot(predicted.reshape(-1), outputVectors[target].T))
    cost += -np.log(a_target)  # cost for target value
    grad[target:target + 1] = (a_target - 1) * predicted  # gradient for target value
    gradPred += (a_target - 1) * outputVectors[target]

    neg_samples = []

    for i in range(K):
        j = dataset.sampleTokenIdx()
        if j == target or (j in neg_samples):
            i -= 1  # if negative sample is same with target or already sampled, then resample.
            continue
        neg_samples.append(j)

        a_neg = sigmoid(-np.dot(predicted.reshape(-1), outputVectors[j].T))
        cost += -np.log(a_neg)  # cost for negative sample
        grad[j:j + 1] = (1 - a_neg) * predicted  # gradient for negative sample
        gradPred += (1 - a_neg) * outputVectors[j]
    # raise NotImplementedError
    ### END YOUR CODE
    
    return cost, gradPred, grad


def skipgram(currentWord, C, contextWords, tokens, inputVectors, outputVectors, 
    dataset, word2vecCostAndGradient = softmaxCostAndGradient):
    """ Skip-gram model in word2vec """

    # Implement the skip-gram model in this function.

    # Inputs:                                                         
    # - currrentWord: a string of the current center word           
    # - C: integer, context size                                    
    # - contextWords: list of no more than 2*C strings, the context words                                               
    # - tokens: a dictionary that maps words to their indices in    
    #      the word vector list                                
    # - inputVectors: "input" word vectors (as rows) for all tokens           
    # - outputVectors: "output" word vectors (as rows) for all tokens         
    # - word2vecCostAndGradient: the cost and gradient function for 
    #      a prediction vector given the target word vectors,  
    #      could be one of the two cost functions you          
    #      implemented above

    # Outputs:                                                        
    # - cost: the cost function value for the skip-gram model       
    # - grad: the gradient with respect to the word vectors         
    # We will not provide starter code for this function, but feel    
    # free to reference the code you previously wrote for this        
    # assignment!

    ### YOUR CODE HERE
    gradIn = np.zeros(inputVectors.shape)
    gradOut = np.zeros(outputVectors.shape)

    vcPos = tokens[currentWord]
    vc = inputVectors[vcPos, :]

    logCount = 0
    for contextWord in contextWords :
        uoPos = tokens[contextWord]
        tempCost,tempGradIn, tempGradOut = word2vecCostAndGradient(vc, uoPos, outputVectors, dataset)

        logCount += tempCost
        gradIn[vcPos, :] += tempGradIn
        gradOut += tempGradOut

    cost = logCount
    # cost = logCount / np.size(inputVectors, axis=0)



    # raise NotImplementedError
    ### END YOUR CODE
    
    return cost, gradIn, gradOut

def cbow(currentWord, C, contextWords, tokens, inputVectors, outputVectors, 
    dataset, word2vecCostAndGradient = softmaxCostAndGradient):
    """ CBOW model in word2vec """

    # Implement the continuous bag-of-words model in this function.            
    # Input/Output specifications: same as the skip-gram model        
    # We will not provide starter code for this function, but feel    
    # free to reference the code you previously wrote for this        
    # assignment!

    #################################################################
    # IMPLEMENTING CBOW IS EXTRA CREDIT, DERIVATIONS IN THE WRIITEN #
    # ASSIGNMENT ARE NOT!                                           #  
    #################################################################
    
    cost = 0
    gradIn = np.zeros(inputVectors.shape)
    gradOut = np.zeros(outputVectors.shape)

    ### YOUR CODE HERE
    for contextWord in contextWords:
        idx = tokens[contextWord]  # tokens['a'] = 1
        input_vector = inputVectors[idx:idx + 1]
        c, g_in, g_out = word2vecCostAndGradient(input_vector, tokens[currentWord], outputVectors, dataset)
        cost += c
        gradIn[idx:idx + 1, :] += g_in
        gradOut += g_out
    # raise NotImplementedError
    ### END YOUR CODE
    
    return cost, gradIn, gradOut

#############################################
# Testing functions below. DO NOT MODIFY!   #
#############################################

def word2vec_sgd_wrapper(word2vecModel, tokens, wordVectors, dataset, C, word2vecCostAndGradient = softmaxCostAndGradient):
    batchsize = 50
    cost = 0.0
    grad = np.zeros(wordVectors.shape)
    N = wordVectors.shape[0]
    inputVectors = wordVectors[:N/2,:]
    outputVectors = wordVectors[N/2:,:]
    for i in xrange(batchsize):
        C1 = random.randint(1,C)
        centerword, context = dataset.getRandomContext(C1)

        if word2vecModel == skipgram:
            denom = 1
        else:
            denom = 1
        
        c, gin, gout = word2vecModel(centerword, C1, context, tokens, inputVectors, outputVectors, dataset, word2vecCostAndGradient)
        cost += c / batchsize / denom
        grad[:N/2, :] += gin / batchsize / denom
        grad[N/2:, :] += gout / batchsize / denom
        
    return cost, grad

def test_word2vec():
    # Interface to the dataset for negative sampling
    dataset = type('dummy', (), {})()
    def dummySampleTokenIdx():
        return random.randint(0, 4)

    def getRandomContext(C):
        tokens = ["a", "b", "c", "d", "e"]
        return tokens[random.randint(0,4)], [tokens[random.randint(0,4)] \
           for i in xrange(2*C)]
    dataset.sampleTokenIdx = dummySampleTokenIdx
    dataset.getRandomContext = getRandomContext

    random.seed(31415)
    np.random.seed(9265)
    dummy_vectors = normalizeRows(np.random.randn(10,3))
    dummy_tokens = dict([("a",0), ("b",1), ("c",2),("d",3),("e",4)])
    print "==== Gradient check for skip-gram ===="
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(skipgram, dummy_tokens, vec, dataset, 5), dummy_vectors)
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(skipgram, dummy_tokens, vec, dataset, 5, negSamplingCostAndGradient), dummy_vectors)
    print "\n==== Gradient check for CBOW      ===="
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(cbow, dummy_tokens, vec, dataset, 5), dummy_vectors)
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(cbow, dummy_tokens, vec, dataset, 5, negSamplingCostAndGradient), dummy_vectors)

    print "\n=== Results ==="
    print skipgram("c", 3, ["a", "b", "e", "d", "b", "c"], dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset)
    print skipgram("c", 1, ["a", "b"], dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset, negSamplingCostAndGradient)
    print cbow("a", 2, ["a", "b", "c", "a"], dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset)
    print cbow("a", 2, ["a", "b", "a", "c"], dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset, negSamplingCostAndGradient)

if __name__ == "__main__":
    test_normalize_rows()
    test_word2vec()