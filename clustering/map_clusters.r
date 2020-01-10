knitr::opts_chunk$set(
  out.width = "100%",
  dpi = 300,
  fig.width = 8,
  fig.height = 6,
  fig.path = 'https://timogrossenbacher.ch/wp-content/uploads/2016/12/tm-',
  strip.white = T,
  dev = "png",
  dev.args = list(png = list(bg = "transparent"))
)

remove(list = ls(all.names = TRUE))

detachAllPackages <- function() {
  basic.packages.blank <-  c("stats", 
                             "graphics", 
                             "grDevices", 
                             "utils", 
                             "datasets", 
                             "methods", 
                             "base")
  basic.packages <- paste("package:", basic.packages.blank, sep = "")
  
  package.list <- search()[ifelse(unlist(gregexpr("package:", search())) == 1, 
                                  TRUE, 
                                  FALSE)]
  
  package.list <- setdiff(package.list, basic.packages)
  
  if (length(package.list) > 0)  for (package in package.list) {
    detach(package, character.only = TRUE)
    print(paste("package ", package, " detached", sep = ""))
  }
}

detachAllPackages()


if (!require(rgeos)) {
  install.packages("rgeos", repos = "http://cran.us.r-project.org")
  require(rgeos)
}
if (!require(rgdal)) {
  install.packages("rgdal", repos = "http://cran.us.r-project.org")
  require(rgdal)
}
if (!require(raster)) {
  install.packages("raster", repos = "http://cran.us.r-project.org")
  require(raster)
}
if(!require(ggplot2)) {
  install.packages("ggplot2", repos="http://cloud.r-project.org")
  require(ggplot2)
}
if(!require(viridis)) {
  install.packages("viridis", repos="http://cloud.r-project.org")
  require(viridis)
}
if(!require(dplyr)) {
  install.packages("dplyr", repos = "https://cloud.r-project.org/")
  require(dplyr)
}
if(!require(gtable)) {
  install.packages("gtable", repos = "https://cloud.r-project.org/")
  require(gtable)
}
if(!require(grid)) {
  install.packages("grid", repos = "https://cloud.r-project.org/")
  require(grid)
}
if(!require(readxl)) {
  install.packages("readxl", repos = "https://cloud.r-project.org/")
  require(readxl)
}
if(!require(magrittr)) {
  install.packages("magrittr", repos = "https://cloud.r-project.org/")
  require(magrittr)
}


theme_map <- function(...) {
  theme_minimal() +
    theme(
      text = element_text(family = "Ubuntu Regular", color = "#22211d"),
      axis.line = element_blank(),
      axis.text.x = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks = element_blank(),
      axis.title.x = element_blank(),
      axis.title.y = element_blank(),
      # panel.grid.minor = element_line(color = "#ebebe5", size = 0.2),
      panel.grid.major = element_line(color = "#ebebe5", size = 0.2),
      panel.grid.minor = element_blank(),
      plot.background = element_rect(fill = "#f5f5f2", color = NA), 
      panel.background = element_rect(fill = "#f5f5f2", color = NA), 
      legend.background = element_rect(fill = "#f5f5f2", color = NA),
      panel.border = element_blank(),
      ...
    )
}

data_input_directory <- "C:\\Users\\edwar\\Dropbox\\Academic Projects\\WB 5G assessment"

data <- read.csv("C:\\Users\\edwar\\Dropbox\\Academic Projects\\WB 5G assessment\\data_clustering_results.csv", stringsAsFactors = F)

# I need to fortify the data AND keep trace of the commune code! (Takes ~2 minutes)
library(rgdal)
library(dplyr)
gde_15 <- readOGR("global_countries.shp", layer = "global_countries")

map_data_fortified <- fortify(gde_15, region = "ISO_3digit") %>% mutate(id = id)

# now we join the thematic data
map_data <- map_data_fortified %>% left_join(data, by = c("id" = "ISO_3digit"))

map_data$fit.cluster[is.na(map_data$fit.cluster)] <- "No Data"

cluster_map <- ggplot() +
  geom_polygon(data = map_data, aes(fill = factor(fit.cluster), 
                                    x = long, 
                                    y = lat, 
                                    group = group), colour='grey', size = 0.4) +
  coord_equal() +
  theme_map() +
  labs(x = NULL, 
       y = NULL, 
       fill = 'Cluster',
       title = "Global Countries by Cluster", 
       subtitle = "Clustering based on GDP Per Capita, Population Density and 4G Coverage") +
  theme(legend.position = "bottom") +
  guides(fill=guide_legend(ncol=8)) 


### EXPORT TO FOLDER
setwd(data_input_directory)
tiff('cluster_map.tiff', units="in", width=10, height=5, res=300)
print(cluster_map)
dev.off()
