library(shiny)
library(sf)

ui <- fluidPage(
  titlePanel("Simple SF Map Viewer"),
  sidebarLayout(
    sidebarPanel(
      selectInput("shape_type", "Select Shape Type",
                  choices = c("Point", "Line", "Polygon"))
    ),
    mainPanel(
      plotOutput("sfPlot")
    )
  )
)

server <- function(input, output) {
  
  # Create reactive SF object based on user input
  sf_object <- reactive({
    switch(input$shape_type,
           "Point" = st_sfc(st_point(c(0, 0))),
           "Line" = st_sfc(st_linestring(matrix(c(0,0,1,1), ncol=2))),
           "Polygon" = st_sfc(st_polygon(list(matrix(c(0,0,1,0,1,1,0,1,0,0), ncol=2, byrow=TRUE))))
    )
  })
  
  # Render the SF plot
  output$sfPlot <- renderPlot({
    plot(sf_object(), main = paste(input$shape_type, "Shape"))
  })
}

shinyApp(ui = ui, server = server)