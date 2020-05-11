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

mean_user_cost_by_cluster <- select(results, scenario, strategy, confidence, cost_per_network_user, cluster)

mean_user_cost_by_cluster <- mean_user_cost_by_cluster %>% 
  group_by(scenario, strategy, confidence, cluster) %>%
  summarise(mean_cost_per_user = mean(cost_per_network_user))

results <- merge(clusters, mean_user_cost_by_cluster, x.by='cluster', y.by='cluster', all=TRUE)

gdp <- read.csv(file.path(folder, '..', 'gdp.csv'))
names(gdp)[names(gdp) == 'iso3'] <- 'iso3'
gdp <- select(gdp, iso3, gdp)

results <- merge(results, gdp, by='iso3', all=FALSE)

pop <- read.csv(file.path(folder, 'data_inputs', 'population_2018.csv'))
pop <- select(pop, iso3, population)
pop$iso3 <- as.character(pop$iso3)

results <- merge(results, pop, by='iso3', all=FALSE)

#Not sure if this is right
#Current costs are for a user on a network with 25% market share
#We then multiply the user cost across the whole population?
#check and revise this
results$total_cost <- results$mean_cost_per_user * results$population

results$gdp_percentage <- (results$total_cost / 5) / results$gdp * 100

results$confidence = factor(results$confidence, levels=c('5','50', '95'),
                            labels=c("lower", 'mean', "upper"))

results$scenario = factor(results$scenario, levels=c("S1_25_10_5",
                                                     "S2_200_50_25",
                                                     "S3_400_100_50"),
                          labels=c("S1 (25 Mbps)",
                                   "S2 (200 Mbps)",
                                   "S3 (400 Mbps)"))

results$strategy = factor(results$strategy, levels=c(
  "4G_epc_microwave_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline",
  "5G_nsa_microwave_baseline_baseline_baseline_baseline",
  "5G_sa_fiber_baseline_baseline_baseline_baseline"),
  labels=c(
    "4G (Microwave)",
    "4G (Fiber)",
    "5G NSA (Microwave)",
    "5G SA (Fiber)"))

results <- results[complete.cases(results), ]

raw_num <- select(results, country, cluster, scenario, strategy, confidence, total_cost)
raw_num <- spread(raw_num, confidence, total_cost)

cost_by_strategy <- ggplot(raw_num, aes(x=raw_num$cluster, y=raw_num$mean/1e9, colour=raw_num$cluster)) + 
  geom_boxplot(aes(group=factor(raw_num$cluster))) + 
  # geom_jitter(width = 0.4, height=0.5, size=1.7) + 
  scale_colour_manual(values = c("#F0E442","#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73")) + 
  theme(legend.position = NULL) + 
  labs(colour=NULL,
       title = "Total Investment Cost",
       subtitle = "Boxplot of results by scenario, strategy and cluster",
       x = NULL, y = "Total Investment ($USD Billions)") +
  theme(panel.spacing = unit(0.6, "lines")) +
  expand_limits(x = 0, y = 0) +
  scale_y_continuous(limits=c(0,40), expand=c(0,0)) +
  guides(fill=FALSE, colour=FALSE) + 
  facet_grid(scenario~strategy)

gdp_num <- select(results, country, cluster, scenario, strategy, confidence, gdp_percentage)
gdp_num <- spread(gdp_num, confidence, gdp_percentage)

gdp_perc_by_strategy <- ggplot(gdp_num, aes(x=gdp_num$cluster, y=gdp_num$mean, colour=gdp_num$cluster)) + 
  geom_boxplot(aes(group=factor(gdp_num$cluster))) + 
  # geom_jitter(width = 0.4, height=0.5, size=1.7) + 
  scale_colour_manual(values = c("#F0E442","#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73")) + 
  theme(legend.position = NULL) + 
  labs(colour=NULL,
       title = "Annual Investment Cost as GDP Share Over 5 Years",
       subtitle = "Boxplot of results by scenario, strategy and cluster",
       x = NULL, y = "Annual GDP (% over 5 years)") +
  theme(panel.spacing = unit(0.4, "lines")) + 
  expand_limits(x = 0, y = 0) +
  scale_y_continuous(limits=c(0,10), expand=c(0,0), breaks=seq(0, 9.7, 2)) +
  guides(fill=FALSE, colour=FALSE) + 
  facet_grid(scenario~strategy)

panel <- ggarrange(cost_by_strategy, gdp_perc_by_strategy, ncol = 1, nrow = 2, align = c("hv"))

#export to folder
path = file.path(folder, 'figures', 'cost_by_strategy.png')
ggsave(path, units="cm", width=25, height=35)
print(panel)
dev.off()
