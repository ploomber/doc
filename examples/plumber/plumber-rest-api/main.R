library(plumber)
pr <- plumb("plumber.R")
pr$run(port = 80, host = "0.0.0.0")
