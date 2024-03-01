# Scheduled functions

```{important}
The document processing API is experimental and only available for certain customers,
if you want to get on the waitlist, send us an email
[contact@ploomber.io](mailto:contact@ploomber.io)
```

You can schedule functions to execute at certain times or days.

## Use case: pre-compute results

Many applications don't require constant data updates, in such cases, you can
pre-compute the results to reduce the workload in your app:

```python
"""
scheduled.py
"""
from ploomber_cloud import scheduled

# pass cron-style schedule (time in UTC), resources needed and pip packages
@scheduled(schedule="0 0 * * *", n_cpus=0.5, memory="1GB", requirements=["pandas"])
def predict_and_upload():
    from my_project import download_data, predict, upload_predictions

    df = download_data()
    predictions = predict(df)
    upload_predictions(df)
```

Add the function:

```sh
ploomber-cloud scheduled --add scheduled.predict_and_upload
```

```
Function has been scheduled.
```

List functions:

```sh
ploomber-cloud scheduled --list
```

```
+---------------------------------+-----------------+
| Scheduled functions             | Schedule        |
+---------------------------------+-----------------+
| scheduled.predict_and_upload    | 0 0 * * *       |
| scheduled.update_dashboard_data | 30 1 * * 1-5    |
+---------------------------------+-----------------+
```

Remove function:

```sh
ploomber-cloud scheduled --remove scheduled.update_data
```

```
Function scheduled.update_data has been removed.
```

## Secrets

If your scheduled function requires secrets, you can manage them from the CLI.
They are available to your function via `os.environ`

```bash
ploomber-cloud secrets --list
ploomber-cloud secrets --add NAME=VALUE
ploomber-cloud secrets --remove NAME
```