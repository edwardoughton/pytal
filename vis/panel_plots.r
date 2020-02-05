###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

#####################
#demand
#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'results_technology_options_6.csv'))

data <- data[!(data$total_cost == "NA"),]

data$scenario = factor(data$scenario, levels=c("S1_30",
                                               "S2_50",
                                               "S3_200"),
                                       labels=c("30 Mbps Per User",
                                                "50 Mbps Per User",
                                                "200 Mbps Per User"))

data$strategy = factor(data$strategy, levels=c("4G_epc_microwave_baseline",
                                               "5G_nsa_microwave_baseline",
                                               "5G_sa_fiber_baseline"),
                                     labels=c("4G (Microwave Backhaul)",
                                              "5G NSA (Microwave Backhaul)",
                                              "5G SA (Fiber Backhaul)"))

#select desired columns
data <- select(data, country, scenario, strategy, decile, area_km2, population, total_cost, revenue)


#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
data <- aggregate( . ~ country + strategy + scenario + decile , FUN=sum, data=data)

data$cost_km2 <- round((data$total_cost / data$area_km2), 2)
data$revenue_km2 <- round((data$revenue / data$area_km2), 2)
data$viability <- round(data$revenue_km2 - data$cost_km2, 2)

revenue_km2 <- ggplot(data, aes(x=decile, y=revenue_km2/1e4, colour=country, group=country)) + 
  geom_point() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Revenue By Population Decile", colour='Country',
       subtitle = "Results reported by scenario, strategy and country",
       x = NULL, y = "Revenue (Thousands $USD per km^2)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0, 100, 10)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=6)) +
  facet_grid(scenario~strategy)

path = file.path(folder, 'figures', 'revenue_km2.png')
ggsave(path, units="in", width=10, height=10)
print(revenue_km2)
dev.off()

viability_km2 <- ggplot(data, aes(x=decile, y=viability/1e4, colour=country, group=country)) + 
  geom_point() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Viability By Population Decile", colour='Country',
       subtitle = "Results reported by scenario, strategy and country",
       x = NULL, y = "Viability Margin (Thousands $USD per km^2)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,10)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=6)) +
  facet_grid(scenario~strategy)

path = file.path(folder, 'figures', 'viability_km2.png')
ggsave(path, units="in", width=10, height=10)
print(viability_km2)
dev.off()

###############
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'results_technology_options_6.csv'))

data <- data[!(data$total_cost == "NA"),]

data$scenario = factor(data$scenario, levels=c("S1_30",
                                               "S2_50",
                                               "S3_200"),
                       labels=c("30 Mbps Per User",
                                "50 Mbps Per User",
                                "200 Mbps Per User"))

data$strategy = factor(data$strategy, levels=c("4G_epc_microwave_baseline",
                                               "5G_nsa_microwave_baseline",
                                               "5G_sa_fiber_baseline"),
                       labels=c("4G (Microwave Backhaul)",
                                "5G NSA (Microwave Backhaul)",
                                "5G SA (Fiber Backhaul)"))

#select desired columns
data <- select(data, country, scenario, strategy, decile, population, total_cost, revenue)

#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
data <- aggregate( . ~ country + strategy + scenario + decile , FUN=sum, data=data)

data$revenue <- round(data$revenue / 1e9, 4)
data$population <- round(data$population / 1e6, 4)

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(revenue_cum_sum = cumsum(revenue))

cumulative_revenue <- ggplot(data, aes(x=decile, y=revenue_cum_sum, colour=country, group=country)) + 
  geom_line() +
    scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Revenue By Population Decile", colour='Country',
       subtitle = "Results reported by scenario, strategy and country",
       x = NULL, y = "Revenue (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,10)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=6)) +
  facet_grid(scenario~strategy)

path = file.path(folder, 'figures', 'cumulative_revenue.png')
ggsave(path, units="in", width=10, height=10)
print(cumulative_revenue)
dev.off()

#####################
#supply
#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'results_technology_options_6.csv'))

data <- data[!(data$total_cost == "NA"),]

data$scenario = factor(data$scenario, levels=c("S1_30",
                                               "S2_50",
                                               "S3_200"),
                                       labels=c("30 Mbps Per User",
                                                "50 Mbps Per User",
                                                "200 Mbps Per User"))

data$strategy = factor(data$strategy, levels=c("4G_epc_microwave_baseline",
                                               "5G_nsa_microwave_baseline",
                                               "5G_sa_fiber_baseline"),
                                       labels=c("4G (Microwave Backhaul)",
                                                "5G NSA (Microwave Backhaul)",
                                                "5G SA (Fiber Backhaul)"))

#select desired columns
data <- select(data, country, scenario, strategy, decile, total_cost, revenue)

#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
data <- aggregate( . ~ country + strategy + scenario + decile , FUN=sum, data=data)

data$total_cost <- round(data$total_cost / 1e9, 4)
data$revenue <- round(data$revenue / 1e9, 4)

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum = cumsum(total_cost))

cumulative_cost <- ggplot(data, aes(x=decile, y=cost_sum, colour=country, group=country)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Cost By Population Decile", colour='Country',
  subtitle = "Results reported by scenario, strategy and country",
  x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,10)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=6)) +
  facet_grid(scenario~strategy)

path = file.path(folder, 'figures', 'results_technology_options.png')
ggsave(path, units="in", width=10, height=10)
print(cumulative_cost)
dev.off()

#load data
data <- read.csv(file.path(folder, '..', 'results', 'results_business_model_options_6.csv'))

#select desired columns
data <- select(data, country, scenario, strategy, decile, total_cost)

data$total_cost <- round(data$total_cost / 1e9, 4)

data <- data[!(data$total_cost == "NA"),]

#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
data <- aggregate( . ~ country + strategy + scenario + decile, FUN=sum, data=data)

data <- data %>% separate('strategy', c('core', 'value', 'backhaul', 'sharing'), "_")

data$scenario = factor(data$scenario, levels=c("S1_30",
                                               "S2_50",
                                               "S3_200"),
                                     labels=c("30 Mbps Per User",
                                              "50 Mbps Per User",
                                              "200 Mbps Per User"))

data$strategy = factor(data$sharing, levels=c("baseline",
                                               "passive",
                                               "active"),
                                      labels=c("Baseline (No sharing)",
                                               "Passive (Site Sharing)",
                                               "Active (RAN and Site Sharing)"))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum = cumsum(total_cost))

panel <- ggplot(data, aes(x=decile, y=cost_sum, colour=country, group=country)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Cost By Population Decile", colour='Country',
       subtitle = "Results reported by scenario, strategy, country and cost type",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,10)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=6)) +
  facet_grid(scenario~strategy)

path = file.path(folder, 'figures', 'results_business_model_options.png')
ggsave(path, units="in", width=10, height=10)
print(panel)
dev.off()
