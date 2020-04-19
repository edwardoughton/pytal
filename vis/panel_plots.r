###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population, total_cost, total_revenue)

data <- data[(data$confidence == 95),]
data <- data[!(data$country == 'SEN'),]

data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             # "KHM",
                                             "PER",
                                             "MEX"),
                                   labels=c("Uganda (C1)",
                                            "Kenya (C2)",
                                            "Senegal (C2)",
                                            "Pakistan (C3)",
                                            # "Cambodia (C4)",
                                            "Peru (C5)",
                                            "Mexico (C6)"))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data1 <- select(data, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "4G_epc_microwave_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue" 
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, country, scenario, strategy, confidence, decile, total_cost)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)
remove(data1, data2)

data$strategy = factor(data$strategy, levels=c("Revenue",
                                              "4G_epc_microwave_baseline_baseline_baseline_baseline",
                                               "4G_epc_fiber_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_sa_fiber_baseline_baseline_baseline_baseline"),
                                       labels=c("Revenue",
                                                "4G (Microwave)",
                                                "4G (Fiber)",
                                                "5G NSA (Microwave)",
                                                "5G SA (Fiber)"))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  # geom_line(aes(linetype=strategy)) +
  # scale_linetype_manual(values=c("twodash", "dotted", "twodash", "dotted", "twodash"))+
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(colour=NULL,
    title = "Impact of Technology",
  subtitle = "Results reported by scenario, decile and country",
  x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=6)) +
  facet_wrap(country~scenario, scales = "free",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_technology_options.png')
ggsave(path, units="in", width=10, height=12, dpi=300)
print(panel)
dev.off()

##################

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_business_model_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data$value <- round(data$value, 4)

data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda (C1)",
                               "Kenya (C2)",
                               "Senegal (C2)",
                               "Pakistan (C3)",
                               "Peru (C5)",
                               "Mexico (C6)"))

data1 <- select(data, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "5G_sa_fiber_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue" 
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, country, scenario, strategy, confidence, decile, total_cost)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)

remove(data1, data2)

data <- data[!(data$value == "NA"),]

data$strategy = factor(data$strategy, levels=c("Revenue",
                                              "5G_sa_fiber_baseline_baseline_baseline_baseline",
                                               "5G_sa_fiber_passive_baseline_baseline_baseline",
                                               "5G_sa_fiber_active_baseline_baseline_baseline"),
                                      labels=c("Revenue",
                                              "Baseline (No sharing)",
                                              "Passive (Site Sharing)",
                                              "Active (RAN and Site Sharing)"))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Infrastructure Sharing", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(country~scenario, scales = "free",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_business_model_options.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()

##################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_cost_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- data[(data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline'),]

data <- select(data, country, strategy, scenario, decile, network_cost, spectrum_cost, tax, profit_margin, 
              used_cross_subsidy, required_state_subsidy)

data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda (Cluster 1)",
                               "Kenya (Cluster 2)",
                               "Senegal (Cluster 2)",
                               "Pakistan (Cluster 3)",
                               "Peru (Cluster 5)",
                               "Mexico (Cluster 6)"))
data <- gather(data, metric, value, network_cost:required_state_subsidy)

data$metric = factor(data$metric, levels=c("network_cost",
                                             "spectrum_cost",
                                             "tax",
                                             "profit_margin",
                                             "used_cross_subsidy",
                                             "required_state_subsidy"),
                      labels=c("Network Cost",
                               "Spectrum Cost",
                               "Tax",
                               "Profit Margin",
                               "Cross-Subsidy",
                               "Required State Subsidy"))


panel <- ggplot(data, aes(x=decile, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Cost Composition", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol =6)) +
  facet_wrap(country~scenario, scales = "free",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_cost_composition.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()



##################Spectrum
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data1 <- select(data, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "5G_nsa_microwave_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue" 
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, country, scenario, strategy, confidence, decile, total_cost)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)

data <- data[(data$strategy == 'Revenue' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_low_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_high_baseline'),]

#select desired columns
data <- select(data, country, scenario, strategy, decile, value)

data <- data[!(data$value == "NA"),]

data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda (C1)",
                               "Kenya (C2)",
                               "Senegal (C2)",
                               "Pakistan (C3)",
                               "Peru (C5)",
                               "Mexico (C6)"))

data$strategy = factor(data$strategy, levels=c("Revenue",
                                                "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_low_baseline",
                                               "5G_nsa_microwave_baseline_baseline_high_baseline"),
                       labels=c("Revenue",
                                "Low (-50% of Baseline)",
                                "Baseline (Historical Prices)",
                                "High (+50% of Baseline)"))

data <- data[order(data$country, data$scenario, data$strategy),]

data <- data %>%
  group_by(country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Spectrum Prices", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(country~scenario, scales = "free_y",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_spectrum_costs.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()


##################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data1 <- select(data, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "5G_nsa_microwave_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue" 
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, country, scenario, strategy, confidence, decile, total_cost)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)

remove(data1, data2)

data <- data[(data$strategy == 'Revenue' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_low' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_high'),]

data <- data[!(data$value == "NA"),]

data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda (C1)",
                               "Kenya (C2)",
                               "Senegal (C2)",
                               "Pakistan (C3)",
                               "Peru (C5)",
                               "Mexico (C6)"))

data$strategy = factor(data$strategy, levels=c('Revenue',
                                               "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_baseline_low",
                                               "5G_nsa_microwave_baseline_baseline_baseline_high"),
                                 labels=c('Revenue', 
                                          "Low (10% Tax Rate)",
                                          "Baseline (25% Tax Rate)",
                                          "High (40% Tax Rate)"))

data <- data[order(data$country, data$scenario, data$strategy),]

data <- data %>%
  group_by(country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Impact of Tax Rate", colour=NULL,
       subtitle = "Results reported by scenario, decile and country",
       x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(country~scenario, scales = "free_y",  ncol = 3) #facet_grid(scenario~country)#

path = file.path(folder, 'figures', 'results_tax_rate.png')
ggsave(path, units="in", width=8, height=11.5, dpi=300)
print(panel)
dev.off()
