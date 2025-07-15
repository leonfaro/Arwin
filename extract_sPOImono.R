# Extract the 'sPOI mono, n=29' sheet (third sheet) from the Excel workbook
# and save it as CSV. Uses base R together with the openxlsx package for
# reading the Excel file.

input_file <- "data characteristics v2.xlsx"
output_file <- "sPOImono.csv"

if (!requireNamespace("openxlsx", quietly = TRUE)) {
  install.packages("openxlsx", repos = "https://cloud.r-project.org")
}

library(openxlsx)

sheet_names <- getSheetNames(input_file)
if (length(sheet_names) < 3) {
  stop("Workbook does not contain a third sheet")
}

# The third sheet is 'sPOI mono, n=29'. The first row in the sheet is blank,
# the second row contains the column names. Hence start reading at row 2 so
# that the names are properly imported.
data <- read.xlsx(input_file, sheet = sheet_names[3], startRow = 2)

write.csv(data, output_file, row.names = FALSE, na = "")

message("Wrote ", nrow(data), " rows to ", output_file)
