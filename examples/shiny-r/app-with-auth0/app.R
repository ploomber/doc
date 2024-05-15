library(shiny)
library(bslib)
library(dplyr)
library(ggplot2)
library(ggExtra)

read_header <- function(session, header_name) {
  if (nchar(header_name) < 1 || !exists(header_name, envir=session$request)) {
    return(NULL)
  }
  return(get(header_name, envir=session$request))
}

penguins_csv <- "https://raw.githubusercontent.com/jcheng5/simplepenguins.R/main/penguins.csv"

df <- readr::read_csv(penguins_csv)
# Find subset of columns that are suitable for scatter plot
df_num <- df |> select(where(is.numeric), -Year)

ui <- page_sidebar(
  title = "Shiny Data Visualization on Ploomber Cloud", # website title

  sidebar = sidebar(
    textOutput("welcome_message"),
    hr(),
    varSelectInput("xvar", "X variable", df_num, selected = "Bill Length (mm)"),
    varSelectInput("yvar", "Y variable", df_num, selected = "Bill Depth (mm)"),
    checkboxGroupInput(
      "species", "Filter by species",
      choices = unique(df$Species),
      selected = unique(df$Species)
    ),
    hr(),
    checkboxInput("by_species", "Show species", TRUE),
    checkboxInput("show_margins", "Show marginal plots", TRUE),
    checkboxInput("smooth", "Add smoother"),
    hr(),
    tags$a(href = "/logout", "Logout")
  ),
  plotOutput("scatter")
)

server <- function(input, output, session) {
  subsetted <- reactive({
    req(input$species)
    df |> filter(Species %in% input$species)
  })

  output$scatter <- renderPlot({
    p <- ggplot(subsetted(), aes(!!input$xvar, !!input$yvar)) + list(
      theme(legend.position = "bottom"),
      if (input$by_species) aes(color = Species),
      geom_point(),
      if (input$smooth) geom_smooth()
    )

    if (input$show_margins) {
      margin_type <- if (input$by_species) "density" else "histogram"
      p <- ggExtra::ggMarginal(p, type = margin_type, margins = "both",
        size = 8, groupColour = input$by_species, groupFill = input$by_species)
    }

    p
  }, res = 100)

  output$welcome_message <- renderText({
    auth_name <- read_header(session, "HTTP_X_AUTH_NAME")
    auth_sub <- read_header(session, "HTTP_X_AUTH_SUB")
    paste("Welcome,", auth_name, "!", "(", auth_sub, ")")
  })
}

shinyApp(ui, server)