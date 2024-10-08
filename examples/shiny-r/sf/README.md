# Basic `sf` Shiny app

Basic Shiny app that uses the `sf` package.


*Note:* this must be deployed as a Docker app since it requires installing GDAL.


Test locally:

```sh
docker build --platform linux/amd64 . -t sf-r
```

```sh
docker run -p 8080:80 sf-r
```

Open: http://localhost:8080