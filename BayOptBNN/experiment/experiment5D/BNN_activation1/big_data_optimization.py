# Copyright (c) 2015, Javier Gonzalez
# Copyright (c) 2015, the GPy Authors (see GPy AUTHORS.txt)
# Licensed under the BSD 3-clause license (see LICENSE.txt)


"""
This is a simple demo to demonstrate the use of Bayesian optimization with BO_BNN with using sparse GPs. Run the example by writing:

import BO_BNN
BO_demo_big_data = BO_BNN.demos.big_data_optimization()

As a result you should see:

- A plot with the model and the current acquisition function
- A plot with the diagnostic plots of the optimization.
- An object call BO_demo_auto that contains the results of the optimization process (see reference manual for details). Among the available results you have access to the GP model via

>> BO_demo_big_data.model

and to the location of the best found location writing.

BO_demo_big_data.x_opt

"""
import os
import sys
# project_dir = os.environ['EXPERI_PROJECT_PATH']
sys.path.append("/home/jie/d2")
sys.path.append("/home/jie/d2/hyperParam")
sys.path.append("/home/jie/d2/hyperParam/BayOptBNN")
sys.path.append("/home/jie/d2/hyperParam/bayesianneuralnetwork")

def big_data_optimization(plots=True):
    import BayOptBNN
    from numpy.random import seed
    seed(12345)
    
    # --- Objective function
    objective_noisy = BayOptBNN.fmodels.experimentsNd.alpine2(5,sd = 0.1)     # Alpine2 function in dimension 5.
    bounds = objective_noisy.bounds                                         # problem constrains 

    # --- Problem definition and optimization
    BO_demo_big_data = BayOptBNN.methods.BayesianOptimizationBNN(f=objective_noisy.f,  # function to optimize
                                            bounds=bounds,                 # box-constrains of the problem
                                            acquisition='LCB',             # Selects the Lower Confidence Bound criterion
                                            acquisition_par = 2,           # parameter of the acquisition function
                                            normalize = True,              # normalized acquisition function
                                            layer_sizes =[5, 20, 20, 1],
                                            numdata_initial_design = 10)        # Initialize the model with 1000 points



    # Run the optimization:
    #it will generate one new training sample using the function every mate-iteration
    max_iter = 1000

    print '-----'
    print '----- Running demo. It may take a few seconds.'
    print '-----'
    
    # --- Run the optimization                                              # evaluation budget
    BO_demo_big_data.run_optimization(max_iter,                             # Number of iterations
                                acqu_optimize_method = 'fast_random',       # method to optimize the acq. function
                                acqu_optimize_restarts = 30,                # number of local optimizers
                                eps = 10e-6,                                # secondary stop criteria (apart from the number of iterations) 
                                true_gradients = False)                     # The gradients of the acquisition function are approximated (faster)
    # --- Plots
    if plots:
        BO_demo_big_data.plot_convergence("bnn_covergence_final_inputdim1000.pdf",full=True)
    BO_demo_big_data.save_report("bnn_report_final_inputdim1000.pdf")
    BO_demo_big_data.save_result()
    return BO_demo_big_data


if __name__=='__main__':
    big_data_optimization()