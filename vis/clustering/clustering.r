###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)
library(dplyr)
library(ggrepel)
require(rgdal)
library(ggpubr)

#some data were missing from the world bank
#Sudan had the population density taken from WorldoMeter: https://www.worldometers.info/world-population/sudan-population/
#Countries with missing GDP per capita information were supplemented with WB data. These include:
# Greenland
# New Caledonia
# Venezuela, RB
# Faroe Islands
# Bahamas, The
# Iran, Islamic Rep.
# French Polynesia
# Syrian Arab Republic
# Northern Mariana Islands
# Isle of Man
# Liechtenstein
# Cayman Islands
# Virgin Islands (U.S.)
# Guam
# Aruba
# Barbados
# Bermuda
# Curacao

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#set cluster number
cluster_num <- 6

#read in data
mydata <- read.csv(file.path(folder, 'data_inputs', 'country_data.csv'))

#exclude certain outlier countries
# mydata <- mydata[which(mydata$country != 'Macao SAR, China' & mydata$country != 'Maldives' & mydata$country != 'Bangladesh'),]

#split high income countries
high_income <- mydata[which(mydata$income == 'High income'),]

#drop high income countries
mydata <- mydata[which(mydata$income != 'High income'), ]

#drop countries <1000km
mydata <- mydata[which(mydata$area >= 5000), ]

#drop countries <1000km
mydata <- mydata[which(mydata$pop_density < 500), ]

#get statistical summary
summary(mydata)

#remove missing data
mydata <- na.omit(mydata) 

#allocate country name as row name 
rownames(mydata) <- mydata$country

#subset country info df
country_info <- select(mydata, income, region)

### subset 3 main variables
subset <- select(mydata, coverage_4g, pop_density, gdp_per_cap)

#scale data to be mean centralized 
subset <- scale(subset) 

#set the seed value for reproducible results
#k means uses randomised initial centroids
set.seed(42)

#determine number of clusters
wss <- ''
for (i in 1:20) wss[i] <- sum(kmeans(subset, centers=i)$withinss)

#set export directory and export wgsss
tiff(file.path(folder, 'figures', "clustering_wgsss_variables.tiff"))
plot(1:20, wss, type="b", xlab="Number of Clusters", ylab="Within groups sum of squares")
dev.off()

# K-Means Cluster Analysis
fit <- kmeans(subset, cluster_num) 
data <- data.frame(subset, fit$cluster)

#turn row names into country column
country_info$country <- rownames(country_info)

#turn row names into country column
data$country <- rownames(data)

#merge cluster results with additional country info
data <- merge(data, country_info, by='country')

#omit missing data rows
data <- na.omit(data) # listwise deletion of missing

#country characters to lower format for merging 
data$country <- tolower(data$country)

#remove whitespace for merging
data$country <- gsub(" ", "", data$country)

#read file containing ISO3 country codes
iso3 <- read.csv(file.path(folder, 'data_inputs', 'global_information.csv'))

#lower characters and remove whitespace for merging
iso3$country <- tolower(iso3$country)
iso3$country <- gsub(" ", "", iso3$country)

#merge data
data <- merge(data, iso3, by='country', all=TRUE)

#omit missing rows
data <- na.omit(data) 

#rename variable to cluster
names(data)[names(data) == 'fit.cluster'] <- 'cluster'

cluster_1 <- data$cluster[data$country=='malawi'][1]
cluster_2 <- data$cluster[data$country=='kenya'][1]
cluster_3 <- data$cluster[data$country=='pakistan'][1]
cluster_4 <- data$cluster[data$country=='morocco'][1]
cluster_5 <- data$cluster[data$country=='peru'][1]
cluster_6 <- data$cluster[data$country=='mexico'][1]

data$cluster[data$cluster== cluster_1] <- 'C1'
data$cluster[data$cluster== cluster_2] <- 'C2'
data$cluster[data$cluster== cluster_3] <- 'C3'
data$cluster[data$cluster== cluster_4] <- 'C4'
data$cluster[data$cluster== cluster_5] <- 'C5'
data$cluster[data$cluster== cluster_6] <- 'C6'

#select desired columns
long <- select(data, country, coverage_4g, pop_density, gdp_per_cap, cluster, income, region, ISO_3digit)

#transform from wide to long
long <- gather(long, 'coverage_4g', 'pop_density', 'gdp_per_cap', key='metric', value='value')

#create factor levels/labels
long$metric = factor(long$metric, levels=c("gdp_per_cap", "pop_density", "coverage_4g"),
                                  labels=c("GDP per capita", "Population Density", "4G Coverage"))
long$income = factor(long$income, levels=c("Low income", "Lower middle income", "Upper middle income"),
                                  labels=c("Low income", "Lower middle income", "Upper middle income"))

long$cluster = factor(long$cluster, levels=c('C1', 'C2', 'C3', 'C4', 'C5', 'C6'))
# long$cluster = factor(long$cluster, levels=c(1,2,3,4,5,6))

#rename columns
names(long)[names(long) == 'region'] <- 'Region'
names(long)[names(long) == 'income'] <- 'Income'

boxplot <- ggplot(long, aes(cluster, value, colour=cluster, shape=Income)) + 
  geom_boxplot(aes(group=factor(cluster))) +
  geom_jitter(width = 0.4, height=0.5, size=1.7) + theme(legend.position = "bottom") +
  #green, light_blue, organge, yellow, dark blue, dark organge
  # scale_colour_manual(values = c("#009E73", "#56B4E9", "#E69F00", "#F0E442", "#0072B2", "#D55E00")) + 
  scale_colour_manual(values = c("#F0E442","#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73")) + 
  expand_limits(x = 0, y = 0) + 
  guides(colour=FALSE, shape=FALSE) + #guide_legend(ncol=3, title=NULL), guide_legend(ncol=2, reverse=T, title=NULL 
  scale_y_continuous(breaks = seq(-2, 8, by = 1), limits=c(-2,3)) +
  labs(title = "Summary Statistics by Cluster Number", x='Cluster Number', y='Mean Centred Values',
       subtitle = "Squares indicate Upper Middle Income, Triangles indicate Lower Middle Income, Circles indicate Lower Income") +
  facet_wrap(~metric)

#export to folder
path = file.path(folder, 'figures', 'clustering_boxplot.tiff')
tiff(path, units="in", width=7, height=5, res=300)
print(boxplot)
dev.off()

#subset data for exporting
data <- select(data, ISO_3digit, country, cluster)

#allocate high income group to df
high_income$cluster <- 'High Income'

#remove whitespace and lower for merging
high_income$country <- gsub(" ", "", high_income$country)
high_income$country <- tolower(high_income$country)

#merge on country column
high_income <- merge(high_income, iso3, by='country')

#subset data
high_income <- select(high_income, ISO_3digit, country, cluster)

#concatenate dfs vertically via row bind
data = rbind(data, high_income)

#export data
write.csv(data, file.path(folder, 'results', 'data_clustering_results.csv'))

rm(data, country_info, fit, high_income, iso3, long, mydata, folder, path,
   subset, i, wss, cluster_num)

if (!require(rgeos)) {
  install.packages("rgeos", repos = "http://cran.us.r-project.org")
  require(rgeos)
}
if (!require(rgdal)) {
  install.packages("rgdal", repos = "http://cran.us.r-project.org")
  require(rgdal)
}
# if (!require(raster)) {
#   install.packages("raster", repos = "http://cran.us.r-project.org")
#   require(raster)
# }
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

#set ggplot2 theme for map
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

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#get data
data <- read.csv(file.path(folder,'results','data_clustering_results.csv'), stringsAsFactors = F)

shapes <- file.path(folder, 'data_inputs', "global_countries.shp")

#fortify the data AND keep trace of the commune code! (Takes ~2 minutes)
gde_15 <- readOGR(shapes, layer = "global_countries")

#fortify the data
map_data_fortified <- fortify(gde_15, region = "ISO_3digit") %>% mutate(id = id)

#now join the thematic data
map_data <- map_data_fortified %>% left_join(data, by = c("id" = "ISO_3digit"))

#swap na label for 'no data'
map_data$cluster[is.na(map_data$cluster)] <- "No Data"

#create map
cluster_map <- ggplot() +
  geom_polygon(data = map_data, aes(fill = factor(cluster),
              x = long, y = lat, group = group), colour='grey', size = 0.2) +
  coord_equal() +  theme_map() +
  labs(x = NULL, y = NULL,  fill = 'Cluster', title = "Global Countries by Cluster",
       subtitle = "Clustering based on GDP Per Capita, Population Density and 4G Coverage") +
  theme(legend.position = "bottom") +
  guides(fill=guide_legend(ncol=8)) +
  scale_fill_manual(values = c("#F0E442","#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73", "#999999", "#000000"))

#export to folder
path = file.path(folder, 'figures', 'map.tiff')
tiff(path, units="in", width=12, height=12, res=300)
print(cluster_map)
dev.off()

rm(data, gde_15, map_data, map_data_fortified)

cluster_panel <- ggarrange(boxplot, cluster_map, ncol = 1, nrow = 2, align = c("hv"))

#export to folder
path = file.path(folder, 'figures', 'cluster_panel.png')
ggsave(path, units="in", width=10, height=10)
print(cluster_panel)
dev.off()
