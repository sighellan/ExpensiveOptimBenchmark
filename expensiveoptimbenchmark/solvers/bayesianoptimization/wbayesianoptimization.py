import numpy as np
from ..utils import Monitor
from bayes_opt import BayesianOptimization

def get_variable_domain(problem, varidx):
    # Vartype can be 'cont' or 'int'
    vartype = problem.vartype()[varidx]

    lbs = problem.lbs()
    ubs = problem.ubs()

    return (lbs[varidx], ubs[varidx])

def get_variables(problem):
    return {
        f'v{i}': get_variable_domain(problem, i)
        for i in range(problem.dims())
    }

def optimize_bayesian_optimization(problem, max_evals, log=None):
    variables = get_variables(problem)

    mon = Monitor("bayesianoptimization", problem, log=log)
    def f(**x):
        # As with pyGPGO, bayesianoptimisation does not naturally support integer variables.
        # As such we round them.
        xvec = np.array([v if t == 'cont' else round(v) for (k, v), t in zip(x.items(), problem.vartype())])
        mon.commit_start_eval()
        r = problem.evaluate(xvec)
        mon.commit_end_eval(xvec, r)
        # Negate because bayesianoptimization maximizes by default.
        # And optimizer.minimize does not actually exist.
        return -r

    mon.start()
    optimizer = BayesianOptimization(
        f=f,
        pbounds=get_variables(problem)
    )

    random_init_points = 5
    optimizer.maximize(
        init_points=random_init_points,
        n_iter=max_evals-random_init_points)
    mon.end()

    solX = [v for (k, v) in optimizer.max['params'].items()] 
    solY = optimizer.max['target']

    return solX, solY, mon