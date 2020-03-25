###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population, total_cost, total_revenue)

data <- data[(data$confidence == 50),]

data$country = factor(data$country, levels=c("PAK",
                                             "MEX",
                                             "PER",
                                             "UGA",
                                             "DZA",
                                             "KEN",
                                             "SEN"),
                       labels=c("Pakistan (C1)",
                                "Mexico (C2)",
                                "Peru (C3)",
                                "Uganda (C4)",
                                "Algeria (C5)",
                                "Kenya (C6)",
                                'Senegal (C6)'))

data$scenario = factor(data$scenario, levels=c("S1_25_5_1",
                                               "S2_100_20_5",
                                               "S3_400_80_20"),
                                     labels=c("S1 (50 Mbps)",
                                              "S2 (100 Mbps)",
                                              "S3 (200 Mbps)"))

data$strategy = factor(data$strategy, levels=c("4G_epc_microwave_baseline_baseline_baseline_baseline",
                                               "4G_epc_fiber_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_sa_fiber_baseline_baseline_baseline_baseline"),
                                     labels=c("4G (Microwave)",
                                              "4G (Fiber)",
                                              "5G NSA (Microwave)",
                                              "5G SA (Fiber)"))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum_bn = cumsum(round(total_cost / 1e9, 2)))

panel <- ggplot(data, aes(x=decile, y=cost_sum_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Technology", colour=NULL,
  subtitle = "Results reported by scenario, decile and country",
  x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(scenario~country, scales = "free_y",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_technology_options.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()
##################

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_business_model_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, decile, total_cost)

data$total_cost <- round(data$total_cost, 4)

data <- data[!(data$total_cost == "NA"),]

# data <- data[(data$country != 'MEX' & data$country != 'GBR' & data$country != 'ZAF' & data$country != 'PAK' & data$country != 'COD'),]

#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
data <- aggregate( . ~ country + strategy + scenario + decile, FUN=sum, data=data)

data <- data %>% separate('strategy', c('gen', 'core', 'backhaul', 'sharing', 'subsidy', 'spectrum', 'tax'), "_")

data$country = factor(data$country, levels=c("PAK",
                                             "MEX",
                                             "PER",
                                             "UGA",
                                             "DZA",
                                             "KEN",
                                             "SEN"),
                      labels=c("Pakistan (C1)",
                               "Mexico (C2)",
                               "Peru (C3)",
                               "Uganda (C4)",
                               "Algeria (C5)",
                               "Kenya (C6)",
                               'Senegal (C6)'))

data$scenario = factor(data$scenario, levels=c("S1_25_5_1",
                                               "S2_100_20_5",
                                               "S3_400_80_20"),
                       labels=c("Scenario 1 (50 Mbps)",
                                "Scenario 2 (100 Mbps)",
                                "Scenario 3 (200 Mbps)"))

data$strategy = factor(data$sharing, levels=c("baseline",
                                               "passive",
                                               "active"),
                                      labels=c("Baseline (No sharing)",
                                               "Passive (Site Sharing)",
                                               "Active (RAN and Site Sharing)"))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum_bn = cumsum(round(total_cost / 1e9, 2)))

panel <- ggplot(data, aes(x=decile, y=cost_sum_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Infrastructure Sharing", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(scenario~country, scales = "free_y",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_business_model_options.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()


##################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data <- data[(data$country != 'MEX' & data$country != 'GBR' & data$country != 'ZAF' & data$country != 'PAK' & data$country != 'COD'),]

#select desired columns
data <- select(data, country, scenario, strategy, decile, total_revenue, total_cost)

data$total_cost <- round(data$total_cost, 4)

data <- data[!(data$total_cost == "NA"),]

data <- data[(data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline' |
              data$strategy == '5G_nsa_microwave_baseline_low_baseline_baseline' |
              data$strategy == '5G_nsa_microwave_baseline_high_baseline_baseline'),]

data <- data %>% separate('strategy', c('gen', 'core', 'backhaul', 'sharing', 'subsidy', 'spectrum', 'tax'), "_")

data$country = factor(data$country, levels=c("PAK",
                                             "MEX",
                                             "PER",
                                             "UGA",
                                             "DZA",
                                             "KEN",
                                             "SEN"),
                      labels=c("Pakistan (C1)",
                               "Mexico (C2)",
                               "Peru (C3)",
                               "Uganda (C4)",
                               "Algeria (C5)",
                               "Kenya (C6)",
                               'Senegal (C6)'))

data$scenario = factor(data$scenario, levels=c("S1_25_5_1",
                                               "S2_100_20_5",
                                               "S3_400_80_20"),
                       labels=c("Scenario 1 (50 Mbps)",
                                "Scenario 2 (100 Mbps)",
                                "Scenario 3 (200 Mbps)"))

data$strategy = factor(data$subsidy, levels=c("baseline",
                                              "low",
                                              "high"),
                                     labels=c("Baseline (No Subsidy)",
                                              "Low (10% Subsidy)",
                                              "High (20% Subsidy)"))

data <- data[order(data$country, data$scenario, data$strategy),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum_bn = cumsum(round(total_cost / 1e9, 2)))

panel <- ggplot(data, aes(x=decile, y=cost_sum_bn, colour=strategy, group=strategy)) +
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Supply-Side Subsidies", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(scenario~country, scales = "free_y",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_supply_subsidy.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()


##################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data <- data[(data$country != 'MEX' & data$country != 'GBR' & data$country != 'ZAF' & data$country != 'PAK' & data$country != 'COD'),]

data <- data[(data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_low' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_high'),]

#select desired columns
data <- select(data, country, scenario, strategy, decile, total_revenue, total_cost)

data$total_cost <- round(data$total_cost, 4)

data <- data[!(data$total_cost == "NA"),]

#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
# data <- aggregate( . ~ country + strategy + scenario + decile, FUN=sum, data=data)

data <- data %>% separate('strategy', c('gen', 'core', 'backhaul', 'sharing', 'subsidy', 'spectrum', 'tax'), "_")

data$country = factor(data$country, levels=c("PAK",
                                             "MEX",
                                             "PER",
                                             "UGA",
                                             "DZA",
                                             "KEN",
                                             "SEN"),
                      labels=c("Pakistan (C1)",
                               "Mexico (C2)",
                               "Peru (C3)",
                               "Uganda (C4)",
                               "Algeria (C5)",
                               "Kenya (C6)",
                               'Senegal (C6)'))

data$scenario = factor(data$scenario, levels=c("S1_25_5_1",
                                               "S2_100_20_5",
                                               "S3_400_80_20"),
                       labels=c("Scenario 1 (50 Mbps)",
                                "Scenario 2 (100 Mbps)",
                                "Scenario 3 (200 Mbps)"))

data$strategy = factor(data$tax, levels=c("baseline",
                                           "low",
                                           "high"),
                                 labels=c("Low (10% Tax Rate)",
                                          "Baseline (25% Tax Rate)",
                                          "High (40% Tax Rate)"))

data <- data[order(data$country, data$scenario, data$strategy),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum_bn = cumsum(round(total_cost / 1e9, 2)))

panel <- ggplot(data, aes(x=decile, y=cost_sum_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Tax Rate", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(scenario~country, scales = "free_y",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_tax_rate.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()



##################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data <- data[(data$country != 'MEX' & data$country != 'GBR' & data$country != 'ZAF' & data$country != 'PAK' & data$country != 'COD'),]

data <- data[(data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_low_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_high_baseline'),]

#select desired columns
data <- select(data, country, scenario, strategy, decile, total_revenue, total_cost)

data$total_cost <- round(data$total_cost, 4)

data <- data[!(data$total_cost == "NA"),]

data <- data %>% separate('strategy', c('gen', 'core', 'backhaul', 'sharing', 'subsidy', 'spectrum', 'tax'), "_")

data$scenario = factor(data$scenario, levels=c("S1_25_5_1",
                                               "S2_100_20_5",
                                               "S3_400_80_20"),
                       labels=c("Scenario 1 (50 Mbps)",
                                "Scenario 2 (100 Mbps)",
                                "Scenario 3 (200 Mbps)"))

data$strategy = factor(data$spectrum, levels=c("low",
                                              "baseline",
                                              "high"),
                       labels=c("Low (-50% of Baseline)",
                                "Baseline (Historical Prices)",
                                "High (+50% of Baseline)"))

data <- data[order(data$country, data$scenario, data$strategy),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum_bn = cumsum(round(total_cost / 1e9, 2)))

panel <- ggplot(data, aes(x=decile, y=cost_sum_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Spectrum Prices", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(scenario~country, scales = "free_y",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_spectrum_costs.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()

