import pickle
from collections import defaultdict, OrderedDict

import numpy as np

import hypergrad as omniglot
from funkyyak import grad
from hypergrad import RandomState, dictslice
from hypergrad import make_nn_funs, VectorParser
from hypergrad.optimizers import sgd_meta_only as sgd

# ----- Fixed params -----
layer_sizes = [784, 100, 55]
N_layers = len(layer_sizes) - 1
N_scripts = 1
batch_size = 200
N_scripts_per_iter = 1
N_iters = 100
alpha = 1.0
beta = 0.9
seed = 2
script_corr = 0.0
# ----- Superparameters -----
log_initialization_scale = -2.0
log_L2_init = -4.0

def run(i_run):
    print ".",
    # log_L2_init = np.linspace(-9, -2, 8)[i_run]
    # condition = "log_L2_init = {0}   ".format(log_L2_init)
    # log_initialization_scale = np.linspace(-6, 1, 8)[i_run]
    # condition = "log_initialization_scale = {0}   ".format(log_initialization_scale)
    # alpha = np.exp(np.linspace(-2, 5, 8)[i_run])
    # condition = "alpha = {0}   ".format(alpha)
    beta = 1 - np.exp(np.linspace(-5, -1, 8)[i_run])
    condition = "beta = {0}   ".format(beta)

    """Three different parsers:
    w_parser[('biases', i_layer)] : neural net weights/biases per layer for a single  script
    script_parser[i_script]       : weights vector for each script
    transform_parser[i_layer]     : transform matrix (scripts x scripts) for each alphabet"""
    RS = RandomState((seed, "top_rs"))
    train_data, valid_data, tests_data = omniglot.load_data_split([11, 2, 2], RS, num_alphabets=N_scripts)
    w_parser, pred_fun, loss_fun, frac_err = make_nn_funs(layer_sizes)
    N_weights = w_parser.vect.size

    uncorrelated_mat = np.eye(N_scripts)
    fully_correlated_mat = np.full((N_scripts, N_scripts), 1.0 / N_scripts)
    transform_mat = (1 - script_corr) * uncorrelated_mat + script_corr * fully_correlated_mat
    transform_mat = transform_mat
    transform_parser = VectorParser()
    for i_layer in range(N_layers):
        if i_layer == N_layers - 1:
            transform_parser[i_layer] = uncorrelated_mat
        else:
            transform_parser[i_layer] = transform_mat

    script_parser = VectorParser()
    for i_script in range(N_scripts):
        script_parser[i_script] = np.zeros(N_weights)

    def transform_weights(all_z_vect, transform_vect, i_script_out):
        all_z     =    script_parser.new_vect(    all_z_vect)
        transform = transform_parser.new_vect(transform_vect)
        W = OrderedDict() # Can't use parser because setting plain array ranges with funkyyak nodes not yet supported
        for k in w_parser.idxs_and_shapes.keys():
            W[k] = 0.0
        for i_layer in range(N_layers):
            script_weightings = transform[i_layer][i_script_out, :]
            for i_script in range(N_scripts):
                z_i_script = w_parser.new_vect(all_z[i_script])
                script_weighting = script_weightings[i_script]
                W[('biases', i_layer)]  += z_i_script[('biases',  i_layer)] * script_weighting
                W[('weights', i_layer)] += z_i_script[('weights', i_layer)] * script_weighting
        return np.concatenate([v.ravel() for v in W.values()])

    def loss_from_latents(z_vect, transform_vect, i_script, data):
        w_vect = transform_weights(z_vect, transform_vect, i_script)
        return loss_fun(w_vect, **data)

    def regularization(z_vect):
        return np.dot(z_vect, z_vect) * np.exp(log_L2_init)

    results = defaultdict(list)
    def hyperloss(transform_vect, i_hyper, record_results=False):
        def primal_stochastic_loss(z_vect, transform_vect, i_primal):
            RS = RandomState((seed, i_hyper, i_primal))
            loss = 0.0
            for _ in range(N_scripts_per_iter):
                i_script = RS.randint(N_scripts)
                N_train = train_data[i_script]['X'].shape[0]
                idxs = RS.permutation(N_train)[:batch_size]
                minibatch = dictslice(train_data[i_script], idxs)
                loss += loss_from_latents(z_vect, transform_vect, i_script, minibatch)
            loss /= N_scripts_per_iter
            reg  = regularization(z_vect)
            # if i_primal % 10 == 0:
            #     print "Iter {0}, loss {1}, reg {2}".format(i_primal, getval(loss), getval(reg))
            #     print "Full losses: train: {0}, valid: {1}".format(
            #         total_loss(train_data, getval(z_vect)),
            #         total_loss(valid_data, getval(z_vect)))
            return loss + reg

        def total_loss(data, z_vect):
            return np.mean([loss_from_latents(z_vect, transform_vect, i_script, data[i_script])
                            for i_script in range(N_scripts)])

        z_vect_0 = RS.randn(script_parser.vect.size) * np.exp(log_initialization_scale)
        z_vect_final = sgd(grad(primal_stochastic_loss), transform_vect, z_vect_0, alpha, beta, N_iters, callback=None)
        valid_loss = total_loss(valid_data, z_vect_final)
        if record_results:
            results['valid_loss'].append(valid_loss)
            results['train_loss'].append(total_loss(train_data, z_vect_final))
            # results['tests_loss'].append(total_loss(tests_data, z_vect_final))
        return valid_loss

    hyperloss(transform_parser.vect, 0, record_results=True)

    return condition + "train_loss: {0}, validation_loss {1}".format(results['train_loss'][-1], results['valid_loss'][-1])

def plot():
    with open('results.pkl') as f:
         results = pickle.load(f)

if __name__ == '__main__':
    results = map(run, range(8))
    print globals()
    print "-"*80
    for r in results:
        print r
    # with open('results.pkl', 'w') as f:
    #     pickle.dump(results, f, 1)
    # plot()
