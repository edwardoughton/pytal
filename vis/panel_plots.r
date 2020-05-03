###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population, total_cost, total_revenue)

# data <- data[(data$confidence == 50),]

data$combined <- paste(data$country, data$scenario, sep="_")


data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             'MWI',
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda",
                               "Malawi",
                               "Kenya",
                               "Senegal",
                               "Pakistan",
                               "Albania",
                               "Peru",
                               "Mexico"))


data$combined = factor(data$combined, levels=c("UGA_S1_25_10_5",
                                             "UGA_S2_200_50_25",
                                             "UGA_S3_400_100_50",
                                             'MWI_S1_25_10_5',
                                             'MWI_S2_200_50_25',
                                             'MWI_S3_400_100_50',
                                             "KEN_S1_25_10_5",
                                             "KEN_S2_200_50_25",
                                             "KEN_S3_400_100_50",
                                             "SEN_S1_25_10_5",
                                             "SEN_S2_200_50_25",
                                             "SEN_S3_400_100_50",
                                             "PAK_S1_25_10_5",
                                             "PAK_S2_200_50_25",
                                             "PAK_S3_400_100_50",
                                             "ALB_S1_25_10_5",
                                             "ALB_S2_200_50_25",
                                             "ALB_S3_400_100_50",
                                             "PER_S1_25_10_5",
                                             "PER_S2_200_50_25",
                                             "PER_S3_400_100_50",
                                             "MEX_S1_25_10_5",
                                             "MEX_S2_200_50_25",
                                             "MEX_S3_400_100_50"),
                                   labels=c("Uganda (C1) 25 Mbps", "Uganda (C1) 200 Mbps", "Uganda (C1) 400 Mbps",
                                            "Malawi (C1) 25 Mbps", "Malawi (C1) 200 Mbps", "Malawi (C1) 400 Mbps",
                                            "Kenya (C2) 25 Mbps", "Kenya (C2) 200 Mbps", "Kenya (C2) 400 Mbps",
                                            "Senegal (C2) 25 Mbps", "Senegal (C2) 200 Mbps", "Senegal (C2) 400 Mbps",
                                            "Pakistan (C3) 25 Mbps", "Pakistan (C3) 200 Mbps", "Pakistan (C3) 400 Mbps",
                                            "Albania (C4) 25 Mbps", "Albania (C4) 200 Mbps", "Albania (C4) 400 Mbps",
                                            "Peru (C5) 25 Mbps", "Peru (C5) 200 Mbps", "Peru (C5) 400 Mbps",
                                            "Mexico (C6) 25 Mbps", "Mexico (C6) 200 Mbps", "Mexico (C6) 400 Mbps" ))

data <- data[order(data$country, data$scenario, data$strategy, data$decile),]

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "4G_epc_microwave_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue" 
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_cost)
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

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(combined, country, scenario, strategy) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

# panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
#   geom_line() +
#   scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
#   theme( legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
#   labs(colour=NULL,
#     title = "Impact of Technology",
#   subtitle = "Results reported by scenario, decile and country",
#   x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
#   scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
#   theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
#   guides(colour=guide_legend(ncol=5)) +
#   facet_grid(country~scenario, scales = "free") 
# 
# path = file.path(folder, 'figures', 'results_technology_options_grid.png')
# ggsave(path, units="in", width=10, height=12, dpi=300)
# print(panel)
# dev.off()

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme( legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
  labs(colour=NULL,
       title = "Viability of Technology Decisions (4G vs 5G & Fiber vs Microwave)",
       subtitle = "Cumulative cost reported by percentage of population covered",
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") + 
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=5)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'results_technology_options_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

##################

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_business_model_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             'MWI',
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda",
                               "Malawi",
                               "Kenya",
                               "Senegal",
                               "Pakistan",
                               "Albania",
                               "Peru",
                               "Mexico"))


data$combined = factor(data$combined, levels=c("UGA_S1_25_10_5",
                                               "UGA_S2_200_50_25",
                                               "UGA_S3_400_100_50",
                                               'MWI_S1_25_10_5',
                                               'MWI_S2_200_50_25',
                                               'MWI_S3_400_100_50',
                                               "KEN_S1_25_10_5",
                                               "KEN_S2_200_50_25",
                                               "KEN_S3_400_100_50",
                                               "SEN_S1_25_10_5",
                                               "SEN_S2_200_50_25",
                                               "SEN_S3_400_100_50",
                                               "PAK_S1_25_10_5",
                                               "PAK_S2_200_50_25",
                                               "PAK_S3_400_100_50",
                                               "ALB_S1_25_10_5",
                                               "ALB_S2_200_50_25",
                                               "ALB_S3_400_100_50",
                                               "PER_S1_25_10_5",
                                               "PER_S2_200_50_25",
                                               "PER_S3_400_100_50",
                                               "MEX_S1_25_10_5",
                                               "MEX_S2_200_50_25",
                                               "MEX_S3_400_100_50"),
                       labels=c("Uganda (C1) 25 Mbps", "Uganda (C1) 200 Mbps", "Uganda (C1) 400 Mbps",
                                "Malawi (C1) 25 Mbps", "Malawi (C1) 200 Mbps", "Malawi (C1) 400 Mbps",
                                "Kenya (C2) 25 Mbps", "Kenya (C2) 200 Mbps", "Kenya (C2) 400 Mbps",
                                "Senegal (C2) 25 Mbps", "Senegal (C2) 200 Mbps", "Senegal (C2) 400 Mbps",
                                "Pakistan (C3) 25 Mbps", "Pakistan (C3) 200 Mbps", "Pakistan (C3) 400 Mbps",
                                "Albania (C4) 25 Mbps", "Albania (C4) 200 Mbps", "Albania (C4) 400 Mbps",
                                "Peru (C5) 25 Mbps", "Peru (C5) 200 Mbps", "Peru (C5) 400 Mbps",
                                "Mexico (C6) 25 Mbps", "Mexico (C6) 200 Mbps", "Mexico (C6) 400 Mbps" ))

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "5G_nsa_microwave_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue" 
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_cost)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)
remove(data1, data2)

data <- data[!(data$value == "NA"),]

data$strategy = factor(data$strategy, levels=c("Revenue",
                                              "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_passive_baseline_baseline_baseline",
                                               "5G_nsa_microwave_active_baseline_baseline_baseline"),
                                      labels=c("Revenue",
                                              "Baseline (No sharing)",
                                              "Passive (Site Sharing)",
                                              "Active (RAN and Site Sharing)"))

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(combined, country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

# panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
#   geom_line() +
#   scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
#   theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
#   labs(title = "Impact of Infrastructure Sharing by scenario, decile and country", colour=NULL,
#        subtitle = "Results reported for 5G NSA using microwave backhaul",
#        x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
#   scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
#   guides(colour=guide_legend(ncol=4)) +
#   facet_grid(country~scenario, scales = "free")
# 
# path = file.path(folder, 'figures', 'results_business_model_options_grid.png')
# ggsave(path, units="in", width=8, height=11.5, dpi=300)
# print(panel)
# dev.off()

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
  labs(title = "Impact of Infrastructure Sharing by Scenario, Decile and Country", colour=NULL,
       subtitle = "Cumulative cost reported by percentage of population covered for 5G NSA (Microwave)",
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") + 
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'results_business_model_options_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

##################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_cost_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- data[(data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline'),]

data$combined <- paste(data$country, data$scenario, sep="_")

data <- select(data, combined, decile, ran, backhaul_fronthaul, 
               civils, core_network, spectrum_cost, tax, profit_margin, 
               used_cross_subsidy, required_state_subsidy, cost_per_sp_user)

data$combined = factor(data$combined, levels=c("UGA_S1_25_10_5",
                                               "UGA_S2_200_50_25",
                                               "UGA_S3_400_100_50",
                                               'MWI_S1_25_10_5',
                                               'MWI_S2_200_50_25',
                                               'MWI_S3_400_100_50',
                                               "KEN_S1_25_10_5",
                                               "KEN_S2_200_50_25",
                                               "KEN_S3_400_100_50",
                                               "SEN_S1_25_10_5",
                                               "SEN_S2_200_50_25",
                                               "SEN_S3_400_100_50",
                                               "PAK_S1_25_10_5",
                                               "PAK_S2_200_50_25",
                                               "PAK_S3_400_100_50",
                                               "ALB_S1_25_10_5",
                                               "ALB_S2_200_50_25",
                                               "ALB_S3_400_100_50",
                                               "PER_S1_25_10_5",
                                               "PER_S2_200_50_25",
                                               "PER_S3_400_100_50",
                                               "MEX_S1_25_10_5",
                                               "MEX_S2_200_50_25",
                                               "MEX_S3_400_100_50"),
                       labels=c("Uganda (C1) 25 Mbps", "Uganda (C1) 200 Mbps", "Uganda (C1) 400 Mbps",
                                "Malawi (C1) 25 Mbps", "Malawi (C1) 200 Mbps", "Malawi (C1) 400 Mbps",
                                "Kenya (C2) 25 Mbps", "Kenya (C2) 200 Mbps", "Kenya (C2) 400 Mbps",
                                "Senegal (C2) 25 Mbps", "Senegal (C2) 200 Mbps", "Senegal (C2) 400 Mbps",
                                "Pakistan (C3) 25 Mbps", "Pakistan (C3) 200 Mbps", "Pakistan (C3) 400 Mbps",
                                "Albania (C4) 25 Mbps", "Albania (C4) 200 Mbps", "Albania (C4) 400 Mbps",
                                "Peru (C5) 25 Mbps", "Peru (C5) 200 Mbps", "Peru (C5) 400 Mbps",
                                "Mexico (C6) 25 Mbps", "Mexico (C6) 200 Mbps", "Mexico (C6) 400 Mbps" ))

data <- gather(data, metric, value, ran:required_state_subsidy)

data$metric = factor(data$metric, levels=c("required_state_subsidy",
                                           "used_cross_subsidy",
                                           "profit_margin",
                                           "tax",
                                           "spectrum_cost",
                                           "ran",
                                           'backhaul_fronthaul',
                                           'civils',
                                           'core_network'
                                          ),
                                          labels=c("Required Subsidy",
                                                   "Cross-Subsidy",
                                                   "Profit",
                                                   "Tax",
                                                   "Spectrum",
                                                   "RAN",
                                                   "Front/Backhaul",
                                                   "Site/Civils",
                                                   'Core'
                                          ))

panel <- ggplot(data, aes(x=decile, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") + 
  labs(title = "Cost Composition by Scenario, Decile and Country", colour=NULL,
       subtitle = "Cumulative cost reported by percentage of population covered for 5G NSA (Microwave)", 
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol =10)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'results_cost_composition_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()


##################Spectrum

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "5G_nsa_microwave_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_cost)
names(data2)[names(data2) == 'total_cost'] <- 'value'
data <- rbind(data1, data2)

data <- data[(
                data$strategy == 'Revenue' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_baseline_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_low_baseline' |
                data$strategy == '5G_nsa_microwave_baseline_baseline_high_baseline'),]

#select desired columns
data <- select(data, combined, country, scenario, strategy, decile, value)

data <- data[!(data$value == "NA"),]

data$scenario = factor(data$scenario, levels=c("S1_25_10_5",
                                               "S2_200_50_25",
                                               "S3_400_100_50"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c("UGA",
                                             'MWI',
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda (C1)",
                               "Malawi (C1)",
                               "Kenya (C2)",
                               "Senegal (C2)",
                               "Pakistan (C3)",
                               "Albania (C4)",
                               "Peru (C5)",
                               "Mexico (C6)"))

data$combined = factor(data$combined, levels=c("UGA_S1_25_10_5",
                                               "UGA_S2_200_50_25",
                                               "UGA_S3_400_100_50",
                                               'MWI_S1_25_10_5',
                                               'MWI_S2_200_50_25',
                                               'MWI_S3_400_100_50',
                                               "KEN_S1_25_10_5",
                                               "KEN_S2_200_50_25",
                                               "KEN_S3_400_100_50",
                                               "SEN_S1_25_10_5",
                                               "SEN_S2_200_50_25",
                                               "SEN_S3_400_100_50",
                                               "PAK_S1_25_10_5",
                                               "PAK_S2_200_50_25",
                                               "PAK_S3_400_100_50",
                                               "ALB_S1_25_10_5",
                                               "ALB_S2_200_50_25",
                                               "ALB_S3_400_100_50",
                                               "PER_S1_25_10_5",
                                               "PER_S2_200_50_25",
                                               "PER_S3_400_100_50",
                                               "MEX_S1_25_10_5",
                                               "MEX_S2_200_50_25",
                                               "MEX_S3_400_100_50"),
                       labels=c("Uganda (C1) 25 Mbps", "Uganda (C1) 200 Mbps", "Uganda (C1) 400 Mbps",
                                "Malawi (C1) 25 Mbps", "Malawi (C1) 200 Mbps", "Malawi (C1) 400 Mbps",
                                "Kenya (C2) 25 Mbps", "Kenya (C2) 200 Mbps", "Kenya (C2) 400 Mbps",
                                "Senegal (C2) 25 Mbps", "Senegal (C2) 200 Mbps", "Senegal (C2) 400 Mbps",
                                "Pakistan (C3) 25 Mbps", "Pakistan (C3) 200 Mbps", "Pakistan (C3) 400 Mbps",
                                "Albania (C4) 25 Mbps", "Albania (C4) 200 Mbps", "Albania (C4) 400 Mbps",
                                "Peru (C5) 25 Mbps", "Peru (C5) 200 Mbps", "Peru (C5) 400 Mbps",
                                "Mexico (C6) 25 Mbps", "Mexico (C6) 200 Mbps", "Mexico (C6) 400 Mbps" ))


data$strategy = factor(data$strategy, levels=c(
                                                "Revenue",
                                                "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_low_baseline",
                                               "5G_nsa_microwave_baseline_baseline_high_baseline"),
                       labels=c(
                                "Revenue",
                                "Low",
                                "Baseline",
                                "High"))

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(combined, country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

# panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
#   geom_line() +
#   scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
#   theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
#   labs(title = "Impact of Spectrum Prices by Scenario, Decile and Country", colour=NULL,
#        subtitle = "Results reported for 5G NSA using microwave backhaul",
#        x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
#   scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
#   guides(fill=guide_legend(ncol =6)) +
#   facet_grid(country~scenario, scales = "free")
# 
# path = file.path(folder, 'figures', 'results_spectrum_costs_grid.png')
# ggsave(path, units="in", width=8, height=11.5, dpi=300)
# print(panel)
# dev.off()

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
  labs(title = "Impact of Spectrum Prices by Scenario, Decile and Country", colour=NULL,
    subtitle = "Cumulative cost reported by percentage of population covered for 5G NSA (Microwave)", 
    x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") +
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol =6)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'results_spectrum_costs_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

##################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data1 <- select(data, combined, country, scenario, strategy, confidence, decile, total_revenue)
data1 <- data1[(data1$strategy == "5G_nsa_microwave_baseline_baseline_baseline_baseline"),]
data1$strategy <- "Revenue"
names(data1)[names(data1) == 'total_revenue'] <- 'value'
data2 <- select(data, combined, country, scenario, strategy, confidence, decile, total_cost)
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
                                             'MWI',
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                      labels=c("Uganda (C1)",
                               "Malawi (C1)",
                               "Kenya (C2)",
                               "Senegal (C2)",
                               "Pakistan (C3)",
                               "Albania (C4)",
                               "Peru (C5)",
                               "Mexico (C6)"))

data$combined = factor(data$combined, levels=c("UGA_S1_25_10_5",
                                               "UGA_S2_200_50_25",
                                               "UGA_S3_400_100_50",
                                               'MWI_S1_25_10_5',
                                               'MWI_S2_200_50_25',
                                               'MWI_S3_400_100_50',
                                               "KEN_S1_25_10_5",
                                               "KEN_S2_200_50_25",
                                               "KEN_S3_400_100_50",
                                               "SEN_S1_25_10_5",
                                               "SEN_S2_200_50_25",
                                               "SEN_S3_400_100_50",
                                               "PAK_S1_25_10_5",
                                               "PAK_S2_200_50_25",
                                               "PAK_S3_400_100_50",
                                               "ALB_S1_25_10_5",
                                               "ALB_S2_200_50_25",
                                               "ALB_S3_400_100_50",
                                               "PER_S1_25_10_5",
                                               "PER_S2_200_50_25",
                                               "PER_S3_400_100_50",
                                               "MEX_S1_25_10_5",
                                               "MEX_S2_200_50_25",
                                               "MEX_S3_400_100_50"),
                       labels=c("Uganda (C1) 25 Mbps", "Uganda (C1) 200 Mbps", "Uganda (C1) 400 Mbps",
                                "Malawi (C1) 25 Mbps", "Malawi (C1) 200 Mbps", "Malawi (C1) 400 Mbps",
                                "Kenya (C2) 25 Mbps", "Kenya (C2) 200 Mbps", "Kenya (C2) 400 Mbps",
                                "Senegal (C2) 25 Mbps", "Senegal (C2) 200 Mbps", "Senegal (C2) 400 Mbps",
                                "Pakistan (C3) 25 Mbps", "Pakistan (C3) 200 Mbps", "Pakistan (C3) 400 Mbps",
                                "Albania (C4) 25 Mbps", "Albania (C4) 200 Mbps", "Albania (C4) 400 Mbps",
                                "Peru (C5) 25 Mbps", "Peru (C5) 200 Mbps", "Peru (C5) 400 Mbps",
                                "Mexico (C6) 25 Mbps", "Mexico (C6) 200 Mbps", "Mexico (C6) 400 Mbps" ))

data$strategy = factor(data$strategy, levels=c('Revenue',
                                               "5G_nsa_microwave_baseline_baseline_baseline_low",
                                              "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_baseline_high"),
                                 labels=c('Revenue', 
                                          "Low (10% Tax Rate)",
                                          "Baseline (25% Tax Rate)",
                                          "High (40% Tax Rate)"))

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(combined, country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

# panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
#   geom_line() +
#   scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
#   theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
#   labs(title = "Impact of Tax Rate by Scenario, Decile and Country", colour=NULL,
#        subtitle = "Results reported for 5G NSA using microwave backhaul",
#        x = NULL, y = "Cost (Billions $USD)") + scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
#   scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
#   guides(fill=guide_legend(ncol =6)) +
#   facet_grid(country~scenario, scales = "free")
# 
# path = file.path(folder, 'figures', 'results_tax_rate_grid.png')
# ggsave(path, units="in", width=8, height=11.5, dpi=300)
# print(panel)
# dev.off()

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
  labs(title = "Impact of Tax Rate by Scenario, Decile and Country", colour=NULL,
       subtitle = "Cumulative cost reported by percentage of population covered for 5G NSA (Microwave)", 
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") +
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol =6)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'results_tax_rate_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()
