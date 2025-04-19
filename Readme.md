# Fetch SRE Exercise

This tools allows user to monitor >1000 endpoints health and report availability percentage (\*) every 15s.

\* availability percentage = number of up / (number of down + number of up)

## Quick start

Prepare a yaml file containing endpoints (see sample.yaml). Then run the following commands to start the app

```bash
# skip these two commands, if you don't want to run it in a virtual python env
python -m venv test_env
source test_env/bin/activate

# install dependency and start the app
pip install -r requirements.txt
python main.py sample.yaml
```

## Sample output

```bash
$ python main.py sample.yaml
dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com has 50% availability percentage
---
dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com has 50% availability percentage
---
```

## Major changes to the code:

1. use package `time` to calculate the endpoint response time, to determine of the endpoint is DOWN or UP.
2. use `xxx.split(":")[0]` to ignore port numbers when determining domain.
3. use `json.loads(body)` to convert JSON string (which is loaded from yaml file) into a Python dict in `check_health`, as `json=` in the request expects a Python `dict` object
4. use `aiohttp` & `asyncio` to fire multiple HTTP request concurrently. The original `for endpoint in config:` implements serial http requests. Since we need to query every endpoint exactly every 15 seconds, we need make those request concurrent.
5. update sleep time to `15 - endpoint response time`. This way we query every endpoint exactly every 15 mintutes.
6. add `'GET'` in `method = endpoint.get('method', 'GET')` to make sure default is GET.
