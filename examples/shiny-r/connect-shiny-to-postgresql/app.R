library(shiny)
library(DBI)

db <- "demo"
db_host <- "ep-lively-credit-a52udj7x.us-east-2.aws.neon.tech"
db_port <- "5432"
db_user <- "demo_owner"
db_pass <- "7iAYbGmr8eOJ"

conn <- dbConnect(
  RPostgres::Postgres(),
  dbname = db,
  host = db_host,
  port = db_port,
  user = db_user,
  password = db_pass
)

tables <- dbListTables(conn)

# Define UI for app that draws a histogram ----
ui <- bootstrapPage(
  titlePanel("PostgreSQL with R Shiny Demo"),

  selectInput(inputId = "table",
              label = "Select Table in Database",
              choices = tables,
              selected = tables[0]),

  # Input: Slider for the number of bins ----
  sliderInput(inputId = "bins",
              label = "Number of bins:",
              min = 1,
              max = 50,
              value = 30),
  # Output: Histogram ----
  plotOutput(outputId = "main_plot")
)

server <- function(input, output) {

  output$main_plot <- renderPlot({
    query <- sprintf("SELECT * FROM %s", input$table)
    df <- dbGetQuery(conn, query)

    x    <- df$studytime
    bins <- seq(min(x), max(x), length.out = input$bins + 1)

    hist(x, breaks = bins, col = "#007bc2", border = "white",
         xlab = "Waiting time to next eruption (in mins)",
         main = "Histogram of waiting times")
  })
}

shinyApp(ui = ui, server = server)