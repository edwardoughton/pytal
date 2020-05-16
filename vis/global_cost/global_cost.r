library(tidyverse)
# library(dplyr)
# library(ggrepel)
require(rgdal)
library(ggpubr)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

results <- read.csv(file.path(folder, '..', '..', 'results', 'national_results_technology_options.csv'))
names(results)[names(results) == 'GID_0'] <- 'iso3'

clusters <- read.csv(file.path(folder, '..', 'clustering', 'results', 'data_clustering_results.csv'))
names(clusters)[names(clusters) == 'ISO_3digit'] <- 'iso3'
clusters <- select(clusters, iso3, cluster, country)

results <- merge(results, clusters, x.by='iso3', y.by='iso3', all=FALSE)

results <- select(results, scenario, strategy, confidence, cost_per_network_user, cluster)

results <- results %>% 
           group_by(scenario, strategy, confidence, cluster) %>%
           summarise(mean_cost_per_user = mean(cost_per_network_user))

all_data <- merge(clusters, results, by='cluster', all=FALSE)

pop <- read.csv(file.path(folder, 'data_inputs', 'population_2018.csv'))
pop <- select(pop, iso3, population)
pop$iso3 <- as.character(pop$iso3)

all_data <- merge(all_data, pop, by='iso3', all=FALSE)

#Not sure if this is right
#Current costs are for a user on a network with 25% market share
#We then multiply the user cost across the whole population?
#check and revise this
all_data$total_cost <- all_data$mean_cost_per_user * all_data$population 

all_data$confidence = factor(all_data$confidence, levels=c('5','50', '95'),
                            labels=c("lower", 'mean', "upper"))

all_data$scenario = factor(all_data$scenario, levels=c("S1_25_10_5",
                                                     "S2_200_50_25",
                                                     "S3_400_100_50"),
                          labels=c("S1 (25 Mbps)",
                                   "S2 (200 Mbps)",
                                   "S3 (400 Mbps)"))

scenario_200_mbps <- all_data[(all_data$scenario == 'S2 (200 Mbps)'),]

scenario_200_mbps$strategy = factor(scenario_200_mbps$strategy, levels=c(
                                               "4G_epc_microwave_baseline_baseline_baseline_baseline",
                                               "4G_epc_fiber_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_sa_fiber_baseline_baseline_baseline_baseline"),
                       labels=c(
                                "4G (Microwave)",
                                "4G (Fiber)",
                                "5G NSA (Microwave)",
                                "5G SA (Fiber)"))

wide <- select(scenario_200_mbps, country, cluster, scenario, strategy, confidence, total_cost)
wide <- spread(wide, confidence, total_cost)

cost_by_strategy <- ggplot(wide, aes(x=wide$cluster, y=wide$mean/1e9, colour=wide$cluster)) + 
  geom_boxplot(aes(group=factor(wide$cluster))) + geom_jitter(width = 0.4, height=0.5, size=1.7) + 
  scale_colour_manual(values = c("#F0E442","#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73")) + 
  theme(legend.position = NULL) + 
  labs(colour=NULL,
       title = "Total Investment Cost",
       subtitle = "Results reported by scenario, strategy and country for 95% confidence",
       x = NULL, y = "Total Investment ($USD Billions)") +
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(x = 0, y = 0) +
  scale_y_continuous(limits=c(0,40), expand=c(0,0)) +
  guides(fill=FALSE, colour=FALSE) + 
  facet_grid(scenario~strategy)

#export to folder
path = file.path(folder, 'figures', 'cost_by_strategy.png')
ggsave(path, units="in", width=7, height=5)
print(cost_by_strategy)
dev.off()


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
data <- read.csv(file.path(folder,'..','clustering','results','data_clustering_results.csv'), stringsAsFactors = F)

shapes <- file.path(folder, '..','clustering','data_inputs', "global_countries.shp")

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

# #export to folder
# path = file.path(folder, 'figures', 'map.tiff')
# tiff(path, units="in", width=12, height=12, res=300)
# print(cluster_map)
# dev.off()

rm(data, gde_15, map_data, map_data_fortified)

cost_by_strategy_vis <- ggarrange(cost_by_strategy, cluster_map, ncol = 1, nrow = 2, align = c("hv"))

#export to folder
path = file.path(folder, 'figures', 'cost_by_strategy_panel.png')
ggsave(path, units="in", width=10, height=10)
print(cost_by_strategy_vis)
dev.off()
