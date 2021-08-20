###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)
library(dplyr)
library(ggrepel)
require(rgdal)
library(ggpubr)

##################CLUSTER COSTS
#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

results <- read.csv(file.path(folder, '..', '..', 'results', 'national_market_results_technology_options.csv'))
names(results)[names(results) == 'GID_0'] <- 'iso3'
results$metric = 'Baseline'

clusters <- read.csv(file.path(folder, '..', 'clustering', 'results', 'data_clustering_results.csv'))
names(clusters)[names(clusters) == 'ISO_3digit'] <- 'iso3'
clusters <- select(clusters, iso3, cluster, country)

results <- merge(results, clusters, x.by='iso3', y.by='iso3', all=FALSE)

results$cost_per_pop = results$total_market_cost / results$population

mean_pop_cost_by_cluster <- select(results, scenario, strategy, confidence, metric,
                                   cluster, cost_per_pop)

mean_pop_cost_by_cluster <- mean_pop_cost_by_cluster %>%
  group_by(scenario, strategy, confidence, metric, cluster) %>%
  summarise(mean_cost_per_pop = round(mean(cost_per_pop)))

results <- merge(clusters, mean_pop_cost_by_cluster, x.by='cluster', y.by='cluster', all=TRUE)

gdp <- read.csv(file.path(folder, '..', 'gdp.csv'))
names(gdp)[names(gdp) == 'iso3'] <- 'iso3'
gdp <- select(gdp, iso3, gdp, income_group)

results <- merge(results, gdp, by='iso3', all=FALSE)

pop <- read.csv(file.path(folder, '..', 'population_2018.csv'))
pop <- select(pop, iso3, population)
pop$iso3 <- as.character(pop$iso3)

results <- merge(results, pop, by='iso3', all=FALSE)

results$total_market_cost <- results$mean_cost_per_pop * results$population

results <- results[(results$confidence == 50),]
results <- results[(results$scenario == 'S2_200_50_5'),]
results <- results[(results$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline'),]

results <- results[complete.cases(results),]

results$gdp_perc <- round((results$total_market_cost/10) / results$gdp * 100, 2)

results <- select(results, iso3, country, gdp_perc)

#################read in data
mydata <- read.csv(file.path(folder,'..','clustering','data_inputs', 'country_data.csv'))

#make country var lower case
mydata$country <- lapply(mydata$country, tolower)

#split high income countries
high_income <- mydata[which(mydata$income == 'High income'),]
# 
# #drop high income countries
# mydata <- mydata[which(mydata$income != 'High income'), ]
# 
# #drop countries <1000km
# mydata <- mydata[which(mydata$area >= 5000), ]
# 
# #drop countries <1000km
# mydata <- mydata[which(mydata$pop_density < 500), ]
# 
# #remove missing data
# mydata <- na.omit(mydata) 
# 
# #allocate country name as row name 
# rownames(mydata) <- mydata$country
# 
# #subset country info df
# country_info <- select(mydata, income, region)
# 
# #turn row names into country column
# country_info$country <- rownames(country_info)
# 
# #merge cluster results with additional country info
# data <- merge(results, country_info, by='country')
# 
# #omit missing data rows
# data <- na.omit(data) # listwise deletion of missing

data <- results

#remove whitespace for merging
data$country <- gsub(" ", "", data$country)

data$gdp_perc <- as.numeric(data$gdp_perc)

data$gdp_perc <- cut(x = data$gdp_perc, 
                    breaks = c(
                      0,
                      0.25,
                      0.5,
                      0.75,
                      1,
                      1.25,
                      1.5,
                      1.75
                      # 2,2.25,20
                      ))

#read file containing ISO3 country codes
iso3 <- read.csv(file.path(folder, '..','clustering','data_inputs', 'global_information.csv'))

#lower characters and remove whitespace for merging
iso3$country <- tolower(iso3$country)
iso3$country <- gsub(" ", "", iso3$country)

#subset data for exporting
data <- select(data, iso3, country, gdp_perc)

#allocate high income group to df
high_income$gdp_perc <- 'High Income'

#remove whitespace and lower for merging
high_income$country <- gsub(" ", "", high_income$country)
high_income$country <- tolower(high_income$country)

#merge on country column
high_income <- merge(high_income, iso3, by='country')

#subset data
high_income <- select(high_income, ISO_3digit, country, gdp_perc)

names(data)[names(data) == 'iso3'] <- 'ISO_3digit'

#concatenate dfs vertically via row bind
data = rbind(data, high_income)

#export data
write.csv(data, file.path(folder, 'gdp_perc_results.csv'))

remove(clusters, country_info, gdp, high_income, 
       iso3, mean_pop_cost_by_cluster, mixed, mydata, pop, results)

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
data <- read.csv(file.path(folder, 'gdp_perc_results.csv'), stringsAsFactors = F)

shapes <- file.path(folder, '..','clustering','data_inputs', "DisputedAreasWGS84.shp")

#fortify the data AND keep trace of the commune code! (Takes ~2 minutes)
gde_15 <- readOGR(shapes, layer = "global_countries")

#fortify the data
map_data_fortified <- fortify(gde_15, region = "ISO_3digit") %>% mutate(id = id)

#now join the thematic data
map_data <- map_data_fortified %>% left_join(data, by = c("id" = "ISO_3digit"))

#swap na label for 'no data'
map_data$gdp_perc[is.na(map_data$gdp_perc)] <- "No Data"

map_data$gdp_perc = factor(map_data$gdp_perc, 
                           levels=c(
                             "(0,0.25]",
                             "(0.25,0.5]",
                             "(0.5,0.75]",
                             "(0.75,1]",
                             "(1,1.25]",
                             "(1.25,1.5]",
                             "(1.5,1.75]",
                             "High Income",
                             "No Data"),
                            labels=c(
                              "<0.25%",
                              "<0.5%",
                              "<0.75%",
                              "<1%",
                              "<1.25%",
                              "<1.5%",
                              "<1.75%",
                              "High Income",
                              "No Data"
                              ))

# palette <- c(
#   "#F0E442", #yellow
#   "#E69F00", #orange
#   "#D55E00", #dark orange
#   "#CC79A7", #pink
#   "#0072B2", #dark blue
#   "#56B4E9", #light blue 
#   "#66FF33", #light green
#   '#999999',#"#009E73", #dark green
#   "#000000"
# )

palette <- c(
  # "#FFFFCC", 
  "#FFFF66", 
  "#FFCC33", 
  "#FF9900", 
  "#FF6600",
  "#FF3300", 
  "#990000", 
  '#660000',
  # "#330000",
  "#333333",
  "#CCCCCC"
)

#create map
gdp_map <-ggplot() +
  geom_polygon(data = map_data, aes(fill = gdp_perc,
      x = long, y = lat, group = group), colour='grey', size = 0.2) +
  coord_equal() +  theme_map() +
  labs(x = NULL, y = NULL,  fill = 'Percentage of GDP ', title = "Investment Requirement by Percentage of GDP",
     subtitle = "Using 5G NSA with a wireless backhaul to deliver up to 200 Mbps per user") +
  theme(legend.position = "bottom") +
  guides(fill=guide_legend(ncol=10)) + 
  scale_fill_manual(values=palette)

#export to folder
path = file.path(folder, 'figures', 'map.tiff')
tiff(path, units="in", width=12, height=12, res=300)
print(gdp_map)
dev.off()
