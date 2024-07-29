library(plumber)
pr <- plumb("rest_controller.R")
pr$run(port = 80, host = "0.0.0.0")
