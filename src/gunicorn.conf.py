import multiprocessing  # noqa

# Gunicorn configuration file

max_requests = 1000
max_requests_jitter = 50

log_file = "-"

bind = "0.0.0.0:5000"

workers = 1
threads = workers

timeout = 120
