#* @apiTitle Plumber Example API
#* @apiDescription This API allows users to interact with a linear regression model predicting iris petal length based on petal width, and optionally, sepal length, sepal width, and species.
#* It provides endpoints for health checks, petal length predictions, and visualizations comparing actual to predicted lengths.

library(caret)
# Prepare the model
dataset <- iris

# Set seed for reproducibility
set.seed(42)

# Split data into training and testing sets
train_index <- createDataPartition(iris$Petal.Length, p = 0.8, list = FALSE)
train_data <- iris[train_index, ]
test_data <- iris[-train_index, ]

# Train the model using all parameters on the training data
model_all <- lm(Petal.Length ~ Sepal.Length + Sepal.Width + Petal.Width + Species, data = train_data)

# Train the model using only petal width on the training data
model_petal_width <- lm(Petal.Length ~ Petal.Width, data = iris)

#* Health Check - Returns the API status and the current server time
#* @get /health_check
function() {
  list(
    status = "The API is running",
    time = Sys.time()
  )
}

#* Predict Petal Length - Returns a predicted petal length based on available parameters
#* @param petal_width Numeric: Width of the petal (required)
#* @param sepal_length Numeric: Length of the sepal
#* @param sepal_width Numeric: Width of the sepal
#* @param species Character: Species of the iris (setosa, versicolor, virginica)
#* @post /predict_petal_length
function(petal_width, sepal_length = NA, sepal_width = NA, species = NA) {
  # Check which parameters are provided and create the input data frame accordingly
  if (!is.na(sepal_length) && !is.na(sepal_width) && !is.na(species)) {
    input_data <- data.frame(
      Sepal.Length = as.numeric(sepal_length),
      Sepal.Width = as.numeric(sepal_width),
      Petal.Width = as.numeric(petal_width),
      Species = as.factor(species)
    )
    prediction <- predict(model_all, input_data)
  } else {
    input_data <- data.frame(Petal.Width = as.numeric(petal_width))
    prediction <- predict(model_petal_width, input_data)
  }

  list(petal_width = petal_width, predicted_petal_length = prediction)
}

#* Plot Actual vs Predicted - Displays a plot comparing actual vs predicted petal lengths for model_all
#* @serializer png
#* @get /plot_actual_vs_predicted
function() {
  predictions <- predict(model_all, test_data)
  plot(test_data$Petal.Length, predictions,
    xlab = "Actual Petal Length", ylab = "Predicted Petal Length",
    main = "Actual vs Predicted Petal Length"
  )
  abline(0, 1, col = "red") # 1:1 line
}
