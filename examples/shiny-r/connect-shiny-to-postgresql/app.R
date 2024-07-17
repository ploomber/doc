library(shiny)
library(DBI)
library(bslib)
library(dplyr)
library(ggplot2)

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

ui <- page_sidebar(
  title = "PostgreSQL with R Shiny Demo",

  sidebar = sidebar(
    accordion(
      accordion_panel(
        "Main Controls",
        selectInput(inputId = "table",
          label = "Select Table in Database",
          choices = tables,
          selected = tables[]),
          accordion_panel(
            "Histogram Controls",
            selectInput(inputId = "hist_x",
              label = "Variable",
              choices = NULL)
          ),
          accordion_panel(
            "Scatterplot Controls",
            selectInput(inputId = "scatter_x",
              label = "X Variable",
              choices = NULL),
            selectInput(inputId = "scatter_y",
              label = "Y Variable",
              choices = NULL)
          )
      )
    )
  ),
  plotOutput(outputId = "hist"),
  plotOutput(outputId = "scatter")
)

server <- function(input, output, session) {

  quant_vars <- reactive({
    query <- sprintf("SELECT * FROM %s LIMIT 1", input$table)
    df <- dbGetQuery(conn, query)
    names(dplyr::select_if(df, is.numeric))
  })

  observe({
    updateSelectInput(session, "hist_x", choices = quant_vars())
    updateSelectInput(session, "scatter_x", choices = quant_vars())
    updateSelectInput(session, "scatter_y", choices = quant_vars())
  })

  output$hist <- renderPlot({
    query <- sprintf("SELECT * FROM %s", input$table)
    df <- dbGetQuery(conn, query)

    ggplot(df, aes_string(x = input$hist_x)) + 
      geom_histogram(fill = "turquoise") +
      labs(title = sprintf("Distribution of %s", input$hist_x), 
            x = input$hist_x,
            y = "Frequency")
  })

  output$scatter <- renderPlot({
    query <- sprintf("SELECT * FROM %s", input$table)
    df <- dbGetQuery(conn, query)

    ggplot(df, aes_string(x = input$scatter_x, y = input$scatter_y)) + 
      geom_point(alpha = 0.5) + 
      labs(title = sprintf("%s vs %s", input$scatter_y, input$scatter_x),
            x = input$scatter_x,
            y = input$scatter_y)
  })
}

shinyApp(ui = ui, server = server)
