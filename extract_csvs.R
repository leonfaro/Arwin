library(readxl)
setwd(getwd())
sheets <- c("POI, n=104", "sPOI mono, n=29", "sPOI combo, n=56")
file_names <- c("POI_n104_raw.csv", "sPOI_mono_n29_raw.csv", "sPOI_combo_n56_raw.csv")
for(i in seq_along(sheets)){
 sheet <- sheets[i]
 n_expected <- as.integer(sub(".*n=([0-9]+).*", "\\1", sheet))
 tmp <- read_excel("data characteristics v3.xlsx", sheet = sheet, col_names = FALSE)
 header_row <- which(grepl("first author", tolower(tmp[[1]])))[1]
 dat <- read_excel("data characteristics v3.xlsx", sheet = sheet, skip = header_row - 1)
 dat <- dat[!is.na(dat[[1]]), ]
 names(dat) <- trimws(names(dat))
 dat[] <- lapply(dat, function(x){if(is.character(x)) trimws(x) else x})
 if(nrow(dat) != n_expected) stop(paste("Row count mismatch", sheet))
 write.csv(dat, file_names[i], row.names = FALSE, fileEncoding = "UTF-8")
 message(file_names[i], " - rows: ", nrow(dat), ", cols: ", ncol(dat))
}
