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

# math <- read.csv("data/student-mat.csv", sep=';')
# por <- read.csv("data/student-por.csv", sep=';')

# print(conn)

# dbWriteTable(conn, "math", math, overwrite=TRUE)
# dbWriteTable(conn, "portuguese", por, overwrite=TRUE)

# res <- dbGetQuery(conn, "SELECT * FROM math LIMIT 5")
# print(res)

query <- sprintf("SELECT * FROM %s", "math")
df <- dbGetQuery(conn, query)

print(df)

