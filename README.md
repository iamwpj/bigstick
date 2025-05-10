Zero-shot Anomaly Detection in System Logs Using LLM

Can you query an LLM with a raw system log and have it tell you if it's an anomaly? Maybe! Can you do that tens of thousands of times? Is it worth it? Does the LLM find anomalies? What are the scaling issues?

Let's find out together!

This is research for my Masters in Cybersecurity, creative component. The research focuses on efficacy of LLMs, specifically using Meta's Llama 3.1 70B model. This will not provide a functional real world application! LLM capabilities are not there yet – but I can analyze where future studies should focus and provide details about how and why it is worthwhile to pursue this application.

* Read more here: [Zero-shot Log-based Anomaly Detection with LLM](paper/Zero-shot%20Log-based%20Anomaly%20Detection%20with%20LLM.pdf)

# Contents

The meat and potatoes are in the `eval_*` files – these contain the workflow that performs each round of queries sent to the LLM.

* [`stats.ipynb`](./stats.ipynb) – shows the basic statistical analysis.
* [`slurm_jobs`](./slurm_jobs/) – contains scritps to run jobs remotely on the cluster.
* [`data`](./data) – The source logs provided in queries.
* [`sample.env`](./sample.env) – You'll need to rename and configure to `.env` to conform with the expected [dotenv](https://configu.com/blog/dotenv-managing-environment-variables-in-node-python-php-and-more/) setup.
