# -*- coding: utf-8 -*-
"""MY!_MATH_170S_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13y4Oas7TDHDFymYxpV-ps5vu0sYTKxa2
"""

pip install setuptools

# Commented out IPython magic to ensure Python compatibility.
#required imports

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import scipy
import scipy.stats as stats
import statsmodels.api as sm
# import theano.tensor as tt
import seaborn as sns
from datetime import datetime

## Get the data:
pd.core.common.is_list_like = pd.api.types.is_list_like # resolves datareader error
from pandas_datareader import data
from IPython.display import Image
from datetime import datetime
# %matplotlib inline

"""## I. Data Processing"""

# Import everyday stock data of Apple Inc. for the latest year
csv_data = pd.read_csv("https://raw.githubusercontent.com/qiiqii77/MATH170S-Project-Stock-Return-Bayesian-Model/refs/heads/main/apple_data.csv")

csv_data.columns

csv_data

returns = csv_data['Close'][-730:].pct_change()
returns = returns.dropna()*100

# subtract the original value from the new value, then divide that difference by the original value and multiply by 100:
# returns <- (diff(csv_data$Adj.Close)/(csv_data$Adj.Close[-(nrow(csv_data))]))*100 # (New Value - Old Value) / Old Value x 100
# head(returns)
# summary(returns)
# plot(returns)

returns.describe()

returns

plt.subplots(1)
returns.hist(color = "lightgreen", edgecolor = "white", bins = 20)
plt.xlabel('Return')
plt.ylabel('Count')
plt.title('Distribution of Return: 10 years')

obs = returns[-300:]

plt.subplots(1)
obs.hist(color = "powderblue", edgecolor = "white", bins = 15)
plt.xlabel('Return')
plt.ylabel('Count')
plt.title('Distribution of Return: Latest 500 days')

"""Since the daily returns histogram shows bell-shaped distribution, we will use the normal distribution for likelihood computation.

##II. Construct Bayesian Models

We implement our Bayesian Estimation models using the Markov Chain Monte Carlo (MCMC) sampling algorithm, which is incorporated in function settings of the PyMC library.

###i. Noninformative Prior

Uniform prior distributions of μ and σ. pdfs h(μ) and h(σ^2) uniform.
"""

with pm.Model() as model_n:

  #Prior
  mu = pm.Uniform("mu", lower=-7, upper=8, initval=0)
  sigma = pm.Uniform("sigma", lower=0, upper=6, initval=0.0001)

  #Likelihood
  likelihood = pm.Normal("likelihood", mu=mu, sigma=sigma, observed = returns.values)

  #Posterior
  start = pm.find_MAP()
  step  = pm.Metropolis()
  trace = pm.sample(20000, chains=3, step=step, start=start, progressbar=True)

trace

# sliced_trace = trace[3000:]
burned_trace = trace.sel(draw=slice(6000, None, 3))

pm.plot_autocorr(trace)

pm.plot_trace(burned_trace)
plt.tight_layout()

pm.plot_posterior(burned_trace)

"""### ii. Try different prior distributions

We shall continue to use normal distribution for the prior distribtution of μ since it allows for a wide range of possible values for the mean, centered around a reasonable guess.

We will investigate into 1) Inverse Gamma and 2) half-normal distributions for σ, both of which ensure the prior only assigns positive probabilities to sigma values.

####ii.a. Uniform prior μ and inverse gamma prior σ
"""

with pm.Model() as model_s:

  #Prior
  mu1 = pm.Uniform("mu1", lower=-7, upper=8, initval=0) # normal prior for mu
  # sigma1 = pm.InverseGamma("sigma1", alpha = 1, initval = 1.5) # initial value taken from the previous posterior sigma
  sigma1 = pm.InverseGamma("sigma1", alpha = 1, initval = 0.0001) # initial value taken from the previous posterior sigma

  #Likelihood
  likelihood1 = pm.Normal("likelihood", mu=mu1, sigma=sigma1, observed = returns.values)

  #Posterior
  start = pm.find_MAP()
  step  = pm.Metropolis()
  trace1 = pm.sample(20000, chains=3, step=step, start=start, progressbar=True)

burned_trace1 = trace1.sel(draw=slice(12000, None, 40)) # a stepsize of 40 is used to reduce noise

pm.plot_autocorr(trace1)

pm.plot_trace(burned_trace1)
plt.tight_layout()

pm.plot_posterior(burned_trace1)

"""####ii.b. Uniform prior μ and half-normal prior σ"""

with pm.Model() as model_g:

  #Prior
  mu2 = pm.Uniform("mu2", lower=-7, upper=8, initval=0) # normal prior for mu
  sigma2 = pm.HalfNormal("sigma2", sigma = 1.5, initval = 0.0001) # initial value taken from the previous posterior sigma

  #Likelihood
  likelihood2 = pm.Normal("likelihood", mu=mu2, sigma=sigma2, observed = returns.values)

  #Posterior
  start = pm.find_MAP()
  step  = pm.Metropolis()
  trace2 = pm.sample(20000, chains=3, step=step, start=start, progressbar=True)

burned_trace2 = trace2.sel(draw=slice(12000, None, 40))

pm.plot_autocorr(trace2)

pm.plot_trace(burned_trace2)
plt.tight_layout()

pm.plot_posterior(burned_trace2)

"""##III. Performance Evaluation and Conclusion

The Bayesian Model using inverse sigma prior distribution for σ gives an estimated μ of -0.032 and σ of 1.50.
The Bayesian Model using hald-normal prior distribution for σ gives an estimated μ of -0.028 and σ of 1.50.
The result of the latter model is better since the estimations are closer to the population 10-year μ of -0.026 and σ of 1.50.

We now generate predicted daily returns using the second model (uniform prior μ and half-normal prior σ) and compare it with the distribution of observed daily returns.
"""

ppc2 = pm.sample_posterior_predictive(burned_trace2, model=model_g)

ppc2

predict_data_2 = ppc2.posterior_predictive.likelihood
# observed_data_2 = ppc2.observed_data.likelihood

plt.hist(predict_data_2[0,0,:], edgecolor = "white", label = "Predicted Data", bins = 15)
plt.hist(observed_data_2, color = "powderblue", edgecolor = "white",
         label = "Observed data", alpha = 0.5, bins = 15)
plt.xlabel('Return')
plt.ylabel('Count')
plt.legend()
plt.title('Comparison of Real data and test data')

"""We can see from the histogram above that the distribution of predicted data is identical to that of the observed data especially in range and location. This confirms that our Bayesian model is reasonably effective in predicting the daily returns.

(We also observe that the actual daily returns are not normally distributed with a intensified concentration near the median. This largely explains why the prediction distribution does not fully overlap with the observed distribution in the middle.)
"""

