###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario = factor(data$scenario, levels=c("S1_30",
                                               "S2_50",
                                               "S3_200"),
                                     labels=c("30 Mbps Per User",
                                              "50 Mbps Per User",
                                              "200 Mbps Per User"))

data$strategy = factor(data$strategy, levels=c("4G_epc_microwave_baseline",
                                               "4G_epc_fiber_baseline",
                                               "5G_nsa_microwave_baseline",
                                               "5G_sa_fiber_baseline"),
                                     labels=c("4G (Microwave Backhaul)",
                                              "4G (Fiber Backhaul)",
                                              "5G NSA (Microwave Backhaul)",
                                              "5G SA (Fiber Backhaul)"))

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population, total_cost, total_revenue)

data <- data[(data$confidence == 50),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum_bn = cumsum(round(total_cost / 1e9)))

cumulative_cost <- ggplot(data, aes(x=decile, y=cost_sum_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Cost By Population Decile", colour='Country',
  subtitle = "Results reported by scenario, strategy and country",
  x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,10)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=6)) +
  facet_grid(scenario~country)

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
