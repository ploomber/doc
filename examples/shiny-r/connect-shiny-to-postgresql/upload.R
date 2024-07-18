library(DBI)

db <- "[DATABASE NAME]"
db_host <- "[YOUR HOST ADDRESS]"
db_port <- "[PORT NUMBER]" 
db_user <- "[DATABASE USERNAME]"
db_pass <- "[DATABASE PASSWORD]"

conn <- dbConnect(
  RPostgres::Postgres(),
  dbname = db,
  host = db_host,
  port = db_port,
  user = db_user,
  password = db_pass
)

math <- read.csv("data/student-mat.csv", sep=';')
por <- read.csv("data/student-por.csv", sep=';')

print(conn)

dbWriteTable(conn, "math", math, overwrite=TRUE)
dbWriteTable(conn, "portuguese", por, overwrite=TRUE)

dbDisconnect(conn)
