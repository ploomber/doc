library(shiny)
library(igraph)
library(highcharter)

ui <- fluidPage(
  titlePanel("Basic Network Graph with igraph and Bar Chart with highcharter"),
  sidebarLayout(
    sidebarPanel(
      actionButton("generate", "Generate New Graph and Chart")
    ),
    mainPanel(
      plotOutput("networkPlot"),
      highchartOutput("barChart")
    )
  )
)

server <- function(input, output) {
  data <- reactiveValues(g = NULL)

  observeEvent(input$generate, {
    data$g <- sample_gnp(10, 0.3)
    V(data$g)$name <- 1:vcount(data$g)  # Set the name attribute for the vertices
  })

  output$networkPlot <- renderPlot({
    req(data$g)
    plot(data$g, vertex.size=10, vertex.label.cex=0.8)
  })

  output$barChart <- renderHighchart({
    req(data$g)
    df <- data.frame(node = V(data$g)$name, degree = degree(data$g))
    hchart(df, "column", hcaes(x = node, y = degree))
  })
}

shinyApp(ui = ui, server = server)