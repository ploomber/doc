# Deploy a dashboard

## 1. Click on "Dashboards" -> "New"

![](../static/dashboards-new.png)


## 2. Fill out the form


![](../static/dashboards-form.png)

## 3. Wait for the deployment to finish

You'll see two tabs. First, you'll see the `DOCKER LOGS`, which show the progress of installing your dashboards's dependencies:

![](../static/dashboards-logs.png)

After 1-2 minutes (depends on the number of dependencies), you'll see a message like this:

```
[INFO] : Pushing image to XYZ ","podName":"ABC"
[INFO] : Pushed XYZ ","podName":"ABC"
```

Which means the Docker image has been built. After a few seconds you'll see that the `VIEW DASHBOARD` button in the top right becomes available:

![](../static/dashboards-view.png)

Click on it to see your dashboard!

```{important}
If you see a `Service not available` error when clicking on `VIEW DASHBOARD`, wait for a few seconds and try again (remember to remove your browser's cache)
```