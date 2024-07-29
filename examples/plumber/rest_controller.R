#* @apiTitle Plumber Example API
#* @apiDescription This API allows users to interact with a linear regression model predicting iris petal length from petal width.
#* It provides endpoints for health checks, predictions, and visualizations of the model fit.

# Prepare the model
dataset <- iris
model <- lm(Petal.Length ~ Petal.Width, data = dataset)

#* Health Check - Returns the API status and the current server time
#* @get /health-check
function() {
  list(
    status = "The API is running",
    time = Sys.time()
  )
}

#* Predict petal length - Returns a predicted petal length for a given petal width using a linear regression model
#* @param petal_width Numeric: Width of the petal for which length is to be predicted
#* @post /predict_petal_length
function(petal_width) {
  input_data <- data.frame(Petal.Width = as.numeric(petal_width))
  prediction <- predict(model, input_data)
  list(petal_width = petal_width, predicted_petal_length = prediction)
}

#* Plot regression line and data points - Displays a scatter plot of the data and the regression line, illustrating the model fit
#* @serializer png
#* @get /plot_regression
function() {
  plot(dataset$Petal.Width, dataset$Petal.Length,
    xlab = "Petal Width", ylab = "Petal Length",
    main = "Linear Model Fit: Petal Length vs Petal Width"
  )
  abline(model, col = "red") # Adds the regression line in red
}
