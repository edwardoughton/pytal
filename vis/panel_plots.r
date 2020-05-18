###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)
library(ggpubr)

####################SUPPLY-DEMAND METRICS
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, #population, area_km2, 
               population_km2, sites_estimated_total, existing_network_sites,
               sites_estimated_total_km2, existing_network_sites_km2,
               phone_density_on_network_km2, sp_density_on_network_km2, 
               total_revenue, total_cost, cost_per_network_user, 
               # cost_per_sp_user
               )

data <- data[(data$confidence == 50),]

data$combined <- paste(data$country, data$scenario, sep="_")

data$country = factor(data$country, levels=c('MWI',
                                             "UGA",
                                             "SEN",
                                             "KEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                      labels=c("Malawi","Uganda",
                               "Senegal","Kenya",
                               "Pakistan",
                               "Albania",
                               "Peru",
                               "Mexico"))

demand = data[(
  data$scenario == 'S1_25_10_2' &
  data$strategy == '4G_epc_fiber_baseline_baseline_baseline_baseline'
    ),]

demand <- select(demand, country, decile, population_km2, 
                 phone_density_on_network_km2, sp_density_on_network_km2)

demand <- gather(demand, metric, value, population_km2:sp_density_on_network_km2)

demand$metric = factor(demand$metric, 
                     levels=c("population_km2",
                             "phone_density_on_network_km2",
                             "sp_density_on_network_km2"),
                       labels=c("Population Density",
                                "Phone Density",
                                "Smartphone Density"))

demand_densities <- ggplot(demand, aes(x=decile, y=value, colour=metric, group=metric)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme( legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
  labs(colour=NULL,
       title = "Demand-Side Density Metrics by Population Decile",
       # subtitle = "Population and user densities",
       x = "Population Decile", y = "Density (per km^2)") + 
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(~country, scales = "free", ncol=4) 

supply = data[(
  data$scenario == 'S1_25_10_2' &
    data$strategy == '4G_epc_fiber_baseline_baseline_baseline_baseline'
),]

supply <- select(supply, country, decile, sites_estimated_total_km2, existing_network_sites_km2)

supply <- gather(supply, metric, value, sites_estimated_total_km2:existing_network_sites_km2)

supply$metric = factor(supply$metric, 
                       levels=c("sites_estimated_total_km2",
                                "existing_network_sites_km2"),
                       labels=c("Total Site Density",
                                "Modeled Network Site Density"))

supply_densities <- ggplot(supply, aes(x=decile, y=value, colour=metric, group=metric)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme( legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
  labs(colour=NULL,
       title = "Supply-Side Density Metrics by Population Decile",
       # subtitle = "Cumulative cost reported by percentage of population covered",
       x = "Population decile", y = "Density (per km^2)") + 
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(~country, scales = "free", ncol=4) 

demand_supply <- ggarrange(demand_densities, supply_densities, ncol = 1, nrow = 2, align = c("hv"))

#export to folder
path = file.path(folder, 'figures', 'a_demand_supply_panel.png')
ggsave(path,  units="in", width=8, height=9, dpi=300)
print(demand_supply)
dev.off()

####################TECHNOLOGIES BY DECILE
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, area_km2, population, 
               total_cost, total_revenue)

data <- data[(data$confidence == 50),]

data$combined <- paste(data$country, data$scenario, sep="_")

data$scenario = factor(data$scenario, levels=c("S1_25_10_2",
                                               "S2_200_50_5",
                                               "S3_400_100_10"),
                       labels=c("S1 (25 Mbps)",
                                "S2 (200 Mbps)",
                                "S3 (400 Mbps)"))

data$country = factor(data$country, levels=c('MWI',
                                             "UGA",
                                             "SEN",
                                             "KEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                      labels=c("Malawi","Uganda",
                               "Senegal","Kenya",
                               "Pakistan",
                               "Albania",
                               "Peru",
                               "Mexico"))


data$combined = factor(data$combined, levels=c('MWI_S1_25_10_2',
                                               'MWI_S2_200_50_5',
                                               'MWI_S3_400_100_10',
                                               "UGA_S1_25_10_2",
                                               "UGA_S2_200_50_5",
                                               "UGA_S3_400_100_10",
                                               "SEN_S1_25_10_2",
                                               "SEN_S2_200_50_5",
                                               "SEN_S3_400_100_10",
                                               "KEN_S1_25_10_2",
                                               "KEN_S2_200_50_5",
                                               "KEN_S3_400_100_10",
                                               "PAK_S1_25_10_2",
                                               "PAK_S2_200_50_5",
                                               "PAK_S3_400_100_10",
                                               "ALB_S1_25_10_2",
                                               "ALB_S2_200_50_5",
                                               "ALB_S3_400_100_10",
                                               "PER_S1_25_10_2",
                                               "PER_S2_200_50_5",
                                               "PER_S3_400_100_10",
                                               "MEX_S1_25_10_2",
                                               "MEX_S2_200_50_5",
                                               "MEX_S3_400_100_10"),
labels=c("Malawi (C1) (S1: 25 Mbps)", "Malawi (C1) (S2: 200 Mbps)", "Malawi (C1) (S3: 400 Mbps)",
         "Uganda (C1) (S1: 25 Mbps)", "Uganda (C1) (S2: 200 Mbps)", "Uganda (C1) (S3: 400 Mbps)",
         "Senegal (C2) (S1: 25 Mbps)", "Senegal (C2) (S2: 200 Mbps)", "Senegal (C2) (S3: 400 Mbps)",
          "Kenya (C2) (S1: 25 Mbps)", "Kenya (C2) (S2: 200 Mbps)", "Kenya (C2) (S3: 400 Mbps)",
          "Pakistan (C3) (S1: 25 Mbps)", "Pakistan (C3) (S2: 200 Mbps)", "Pakistan (C3) (S3: 400 Mbps)",
          "Albania (C4) (S1: 25 Mbps)", "Albania (C4) (S2: 200 Mbps)", "Albania (C4) (S3: 400 Mbps)",
          "Peru (C5) (S1: 25 Mbps)", "Peru (C5) (S2: 200 Mbps)", "Peru (C5) (S3: 400 Mbps)",
          "Mexico (C6) (S1: 25 Mbps)", "Mexico (C6) (S2: 200 Mbps)", "Mexico (C6) (S3: 400 Mbps)" ))

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

path = file.path(folder, 'figures', 'b_results_technology_options_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

##################BUSINESS MODELS BY DECILE
#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_business_model_options.csv'))

data <- data[!(data$total_cost == "NA"),]

data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data$scenario = factor(data$scenario, levels=c("S1_25_10_2",
                                               "S2_200_50_5",
                                               "S3_400_100_10"),
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


data$combined = factor(data$combined, levels=c('MWI_S1_25_10_2',
                                               'MWI_S2_200_50_5',
                                               'MWI_S3_400_100_10',
                                               "UGA_S1_25_10_2",
                                               "UGA_S2_200_50_5",
                                               "UGA_S3_400_100_10",
                                               "SEN_S1_25_10_2",
                                               "SEN_S2_200_50_5",
                                               "SEN_S3_400_100_10",
                                               "KEN_S1_25_10_2",
                                               "KEN_S2_200_50_5",
                                               "KEN_S3_400_100_10",
                                               "PAK_S1_25_10_2",
                                               "PAK_S2_200_50_5",
                                               "PAK_S3_400_100_10",
                                               "ALB_S1_25_10_2",
                                               "ALB_S2_200_50_5",
                                               "ALB_S3_400_100_10",
                                               "PER_S1_25_10_2",
                                               "PER_S2_200_50_5",
                                               "PER_S3_400_100_10",
                                               "MEX_S1_25_10_2",
                                               "MEX_S2_200_50_5",
                                               "MEX_S3_400_100_10"),
                       labels=c("Malawi (C1) (S1: 25 Mbps)", "Malawi (C1) (S2: 200 Mbps)", "Malawi (C1) (S3: 400 Mbps)",
                                "Uganda (C1) (S1: 25 Mbps)", "Uganda (C1) (S2: 200 Mbps)", "Uganda (C1) (S3: 400 Mbps)",
                                "Senegal (C2) (S1: 25 Mbps)", "Senegal (C2) (S2: 200 Mbps)", "Senegal (C2) (S3: 400 Mbps)",
                                "Kenya (C2) (S1: 25 Mbps)", "Kenya (C2) (S2: 200 Mbps)", "Kenya (C2) (S3: 400 Mbps)",
                                "Pakistan (C3) (S1: 25 Mbps)", "Pakistan (C3) (S2: 200 Mbps)", "Pakistan (C3) (S3: 400 Mbps)",
                                "Albania (C4) (S1: 25 Mbps)", "Albania (C4) (S2: 200 Mbps)", "Albania (C4) (S3: 400 Mbps)",
                                "Peru (C5) (S1: 25 Mbps)", "Peru (C5) (S2: 200 Mbps)", "Peru (C5) (S3: 400 Mbps)",
                                "Mexico (C6) (S1: 25 Mbps)", "Mexico (C6) (S2: 200 Mbps)", "Mexico (C6) (S3: 400 Mbps)" ))

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
                                               "5G_nsa_microwave_active_baseline_baseline_baseline",
                                               "5G_nsa_microwave_shared_baseline_baseline_baseline"),
                                      labels=c("Revenue",
                                              "Baseline (No sharing)",
                                              "Passive (Site Sharing)",
                                              "Active (RAN and Site Sharing)",
                                              "Single Wholesale Network"))

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(combined, country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

panel <- ggplot(data, aes(x=decile, y=cumulative_value_bn, colour=strategy, group=strategy)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(legend.position = "bottom") + #axis.text.x = element_text(angle = 45, hjust = 1), 
  labs(title = "Impact of Infrastructure Sharing by Scenario, Decile and Country", colour=NULL,
       subtitle = "Cumulative cost reported by percentage of population covered for 5G NSA (Microwave)",
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") + 
  scale_x_continuous(expand = c(0, 0), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=5)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'c_results_business_model_options_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

##################SPECTRUM BY DECILE

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$confidence == 50),]

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

data$scenario = factor(data$scenario, levels=c("S1_25_10_2",
                                               "S2_200_50_5",
                                               "S3_400_100_10"),
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

data$combined = factor(data$combined, levels=c('MWI_S1_25_10_2',
                                               'MWI_S2_200_50_5',
                                               'MWI_S3_400_100_10',
                                               "UGA_S1_25_10_2",
                                               "UGA_S2_200_50_5",
                                               "UGA_S3_400_100_10",
                                               "SEN_S1_25_10_2",
                                               "SEN_S2_200_50_5",
                                               "SEN_S3_400_100_10",
                                               "KEN_S1_25_10_2",
                                               "KEN_S2_200_50_5",
                                               "KEN_S3_400_100_10",
                                               "PAK_S1_25_10_2",
                                               "PAK_S2_200_50_5",
                                               "PAK_S3_400_100_10",
                                               "ALB_S1_25_10_2",
                                               "ALB_S2_200_50_5",
                                               "ALB_S3_400_100_10",
                                               "PER_S1_25_10_2",
                                               "PER_S2_200_50_5",
                                               "PER_S3_400_100_10",
                                               "MEX_S1_25_10_2",
                                               "MEX_S2_200_50_5",
                                               "MEX_S3_400_100_10"),
                       labels=c("Malawi (C1) (S1: 25 Mbps)", "Malawi (C1) (S2: 200 Mbps)", "Malawi (C1) (S3: 400 Mbps)",
                                "Uganda (C1) (S1: 25 Mbps)", "Uganda (C1) (S2: 200 Mbps)", "Uganda (C1) (S3: 400 Mbps)",
                                "Senegal (C2) (S1: 25 Mbps)", "Senegal (C2) (S2: 200 Mbps)", "Senegal (C2) (S3: 400 Mbps)",
                                "Kenya (C2) (S1: 25 Mbps)", "Kenya (C2) (S2: 200 Mbps)", "Kenya (C2) (S3: 400 Mbps)",
                                "Pakistan (C3) (S1: 25 Mbps)", "Pakistan (C3) (S2: 200 Mbps)", "Pakistan (C3) (S3: 400 Mbps)",
                                "Albania (C4) (S1: 25 Mbps)", "Albania (C4) (S2: 200 Mbps)", "Albania (C4) (S3: 400 Mbps)",
                                "Peru (C5) (S1: 25 Mbps)", "Peru (C5) (S2: 200 Mbps)", "Peru (C5) (S3: 400 Mbps)",
                                "Mexico (C6) (S1: 25 Mbps)", "Mexico (C6) (S2: 200 Mbps)", "Mexico (C6) (S3: 400 Mbps)" ))


data$strategy = factor(data$strategy, levels=c(
                                                "Revenue",
                                                "5G_nsa_microwave_baseline_baseline_low_baseline",
                                                "5G_nsa_microwave_baseline_baseline_baseline_baseline",
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

path = file.path(folder, 'figures', 'd_results_spectrum_costs_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

##################TAX BY DECILE

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_results_policy_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$confidence == 50),]

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

data$scenario = factor(data$scenario, levels=c("S1_25_10_2",
                                               "S2_200_50_5",
                                               "S3_400_100_10"),
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

data$combined = factor(data$combined, levels=c('MWI_S1_25_10_2',
                                               'MWI_S2_200_50_5',
                                               'MWI_S3_400_100_10',
                                               "UGA_S1_25_10_2",
                                               "UGA_S2_200_50_5",
                                               "UGA_S3_400_100_10",
                                               "SEN_S1_25_10_2",
                                               "SEN_S2_200_50_5",
                                               "SEN_S3_400_100_10",
                                               "KEN_S1_25_10_2",
                                               "KEN_S2_200_50_5",
                                               "KEN_S3_400_100_10",
                                               "PAK_S1_25_10_2",
                                               "PAK_S2_200_50_5",
                                               "PAK_S3_400_100_10",
                                               "ALB_S1_25_10_2",
                                               "ALB_S2_200_50_5",
                                               "ALB_S3_400_100_10",
                                               "PER_S1_25_10_2",
                                               "PER_S2_200_50_5",
                                               "PER_S3_400_100_10",
                                               "MEX_S1_25_10_2",
                                               "MEX_S2_200_50_5",
                                               "MEX_S3_400_100_10"),
                       labels=c("Malawi (C1) (S1: 25 Mbps)", "Malawi (C1) (S2: 200 Mbps)", "Malawi (C1) (S3: 400 Mbps)",
                                "Uganda (C1) (S1: 25 Mbps)", "Uganda (C1) (S2: 200 Mbps)", "Uganda (C1) (S3: 400 Mbps)",
                                "Senegal (C2) (S1: 25 Mbps)", "Senegal (C2) (S2: 200 Mbps)", "Senegal (C2) (S3: 400 Mbps)",
                                "Kenya (C2) (S1: 25 Mbps)", "Kenya (C2) (S2: 200 Mbps)", "Kenya (C2) (S3: 400 Mbps)",
                                "Pakistan (C3) (S1: 25 Mbps)", "Pakistan (C3) (S2: 200 Mbps)", "Pakistan (C3) (S3: 400 Mbps)",
                                "Albania (C4) (S1: 25 Mbps)", "Albania (C4) (S2: 200 Mbps)", "Albania (C4) (S3: 400 Mbps)",
                                "Peru (C5) (S1: 25 Mbps)", "Peru (C5) (S2: 200 Mbps)", "Peru (C5) (S3: 400 Mbps)",
                                "Mexico (C6) (S1: 25 Mbps)", "Mexico (C6) (S2: 200 Mbps)", "Mexico (C6) (S3: 400 Mbps)" ))


data$strategy = factor(data$strategy, levels=c('Revenue',
                                               "5G_nsa_microwave_baseline_baseline_baseline_low",
                                              "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                               "5G_nsa_microwave_baseline_baseline_baseline_high"),
                                 labels=c('Revenue', 
                                          "Low (10% Tax Rate)",
                                          "Baseline (30% Tax Rate)",
                                          "High (40% Tax Rate)"))

data <- data[order(data$combined, data$country, data$scenario, data$strategy, data$decile),]

data <- data %>%
  group_by(combined, country, strategy, scenario) %>%
  mutate(cumulative_value_bn = cumsum(round(value / 1e9, 3)))

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

path = file.path(folder, 'figures', 'e_results_tax_rate_wrap.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

###################NATIONAL COST PROFILE FOR BASELINE
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'national_cost_results_technology_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data$combined <- paste(data$country, data$scenario, sep="_")

data <- select(data, strategy, combined, ran, backhaul_fronthaul,
               civils, core_network, ops_and_acquisition, spectrum_cost, tax, profit_margin,
               used_cross_subsidy, required_state_subsidy)

data$combined = factor(data$combined, levels=c('MWI_S1_25_10_2',
                                               'MWI_S2_200_50_5',
                                               'MWI_S3_400_100_10',
                                               "UGA_S1_25_10_2",
                                               "UGA_S2_200_50_5",
                                               "UGA_S3_400_100_10",
                                               "SEN_S1_25_10_2",
                                               "SEN_S2_200_50_5",
                                               "SEN_S3_400_100_10",
                                               "KEN_S1_25_10_2",
                                               "KEN_S2_200_50_5",
                                               "KEN_S3_400_100_10",
                                               "PAK_S1_25_10_2",
                                               "PAK_S2_200_50_5",
                                               "PAK_S3_400_100_10",
                                               "ALB_S1_25_10_2",
                                               "ALB_S2_200_50_5",
                                               "ALB_S3_400_100_10",
                                               "PER_S1_25_10_2",
                                               "PER_S2_200_50_5",
                                               "PER_S3_400_100_10",
                                               "MEX_S1_25_10_2",
                                               "MEX_S2_200_50_5",
                                               "MEX_S3_400_100_10"),
                       labels=c("Malawi (C1) (S1: 25 Mbps)", "Malawi (C1) (S2: 200 Mbps)", "Malawi (C1) (S3: 400 Mbps)",
                                "Uganda (C1) (S1: 25 Mbps)", "Uganda (C1) (S2: 200 Mbps)", "Uganda (C1) (S3: 400 Mbps)",
                                "Senegal (C2) (S1: 25 Mbps)", "Senegal (C2) (S2: 200 Mbps)", "Senegal (C2) (S3: 400 Mbps)",
                                "Kenya (C2) (S1: 25 Mbps)", "Kenya (C2) (S2: 200 Mbps)", "Kenya (C2) (S3: 400 Mbps)",
                                "Pakistan (C3) (S1: 25 Mbps)", "Pakistan (C3) (S2: 200 Mbps)", "Pakistan (C3) (S3: 400 Mbps)",
                                "Albania (C4) (S1: 25 Mbps)", "Albania (C4) (S2: 200 Mbps)", "Albania (C4) (S3: 400 Mbps)",
                                "Peru (C5) (S1: 25 Mbps)", "Peru (C5) (S2: 200 Mbps)", "Peru (C5) (S3: 400 Mbps)",
                                "Mexico (C6) (S1: 25 Mbps)", "Mexico (C6) (S2: 200 Mbps)", "Mexico (C6) (S3: 400 Mbps)" ))

data$strategy = factor(data$strategy, levels=c(
  "4G_epc_microwave_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline",
  "5G_nsa_microwave_baseline_baseline_baseline_baseline",
  "5G_sa_fiber_baseline_baseline_baseline_baseline"),
  labels=c("4G (MW)",
           "4G (FB)",
           "5G NSA (MW)",
           "5G SA (FB)"))

required_subsidy <- select(data, combined, strategy, (used_cross_subsidy/1e9), (required_state_subsidy/1e9))
path = file.path(folder, '..','results', 'required_subsidy.csv')
write.csv(required_subsidy, path)

data <- gather(data, metric, value, ran:required_state_subsidy)

data$metric = factor(data$metric, levels=c("required_state_subsidy",
                                           "used_cross_subsidy",
                                           "profit_margin",
                                           "tax",
                                           "spectrum_cost",
                                           "ops_and_acquisition",
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
         "Ops",
         "RAN",
         "FH/BH",
         "Sites",
         'Core/Regional Fiber'
))

panel <- ggplot(data, aes(x=strategy, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") +
  labs(title = "Aggregate Cost Composition by Scenario, Strategy and Country", colour=NULL,
       subtitle = "Illustrates required state subsidy under baseline conditions",
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol =10, reverse = TRUE)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'f_cost_composition_baseline_national.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()


##############NATIONAL COST PROFILE FOR MIXED OPTIONS
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'national_cost_results_mixed_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

# data$confidence = factor(data$confidence, levels=c('5','50', '95'),
#                             labels=c("lower", 'mean', "upper"))

data$combined <- paste(data$country, data$scenario, sep="_")

data <- select(data, confidence, strategy, combined, ran, backhaul_fronthaul, 
               civils, core_network, ops_and_acquisition, spectrum_cost, tax, profit_margin, 
               used_cross_subsidy, required_state_subsidy)

data <- gather(data, metric, value, ran:required_state_subsidy)
# 
# lower_data <- data[(data$confidence == 'lower'),]
# mean_data <- data[(data$confidence == 'mean'),]
# upper_data <- data[(data$confidence == 'upper'),]
# 
# names(lower_data)[names(lower_data) == 'value'] <- 'lower'
# names(mean_data)[names(upper_data) == 'value'] <- 'mean'
# names(upper_data)[names(upper_data) == 'value'] <- 'upper'
# 
# lower_data <- select(lower_data, strategy, combined, metric, lower)
# mean_data <- select(mean_data, strategy, combined, metric, mean)
# upper_data <- select(upper_data, strategy, combined, metric, upper)
# 
# data <- merge(mean_data, lower_data, by=c('strategy', 'combined', 'metric'))
# data <- merge(data, upper_data, by=c('strategy', 'combined', 'metric'))
# 
# rm(lower_data, mean_data, upper_data)

data$combined = factor(data$combined, levels=c('MWI_S1_25_10_2',
                                               'MWI_S2_200_50_5',
                                               'MWI_S3_400_100_10',
                                               "UGA_S1_25_10_2",
                                               "UGA_S2_200_50_5",
                                               "UGA_S3_400_100_10",
                                               "SEN_S1_25_10_2",
                                               "SEN_S2_200_50_5",
                                               "SEN_S3_400_100_10",
                                               "KEN_S1_25_10_2",
                                               "KEN_S2_200_50_5",
                                               "KEN_S3_400_100_10",
                                               "PAK_S1_25_10_2",
                                               "PAK_S2_200_50_5",
                                               "PAK_S3_400_100_10",
                                               "ALB_S1_25_10_2",
                                               "ALB_S2_200_50_5",
                                               "ALB_S3_400_100_10",
                                               "PER_S1_25_10_2",
                                               "PER_S2_200_50_5",
                                               "PER_S3_400_100_10",
                                               "MEX_S1_25_10_2",
                                               "MEX_S2_200_50_5",
                                               "MEX_S3_400_100_10"),
                       labels=c("Malawi (C1) (S1: 25 Mbps)", "Malawi (C1) (S2: 200 Mbps)", "Malawi (C1) (S3: 400 Mbps)",
                                "Uganda (C1) (S1: 25 Mbps)", "Uganda (C1) (S2: 200 Mbps)", "Uganda (C1) (S3: 400 Mbps)",
                                "Senegal (C2) (S1: 25 Mbps)", "Senegal (C2) (S2: 200 Mbps)", "Senegal (C2) (S3: 400 Mbps)",
                                "Kenya (C2) (S1: 25 Mbps)", "Kenya (C2) (S2: 200 Mbps)", "Kenya (C2) (S3: 400 Mbps)",
                                "Pakistan (C3) (S1: 25 Mbps)", "Pakistan (C3) (S2: 200 Mbps)", "Pakistan (C3) (S3: 400 Mbps)",
                                "Albania (C4) (S1: 25 Mbps)", "Albania (C4) (S2: 200 Mbps)", "Albania (C4) (S3: 400 Mbps)",
                                "Peru (C5) (S1: 25 Mbps)", "Peru (C5) (S2: 200 Mbps)", "Peru (C5) (S3: 400 Mbps)",
                                "Mexico (C6) (S1: 25 Mbps)", "Mexico (C6) (S2: 200 Mbps)", "Mexico (C6) (S3: 400 Mbps)" ))



data$metric = factor(data$metric, levels=c("required_state_subsidy",
                                           "used_cross_subsidy",
                                           "profit_margin",
                                           "tax",
                                           "spectrum_cost",
                                           "ops_and_acquisition",
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
         "Ops",
         "RAN",
         "FH/BH",
         "Sites",
         'Core/Regional Fiber'
))

data$strategy = factor(data$strategy, levels=c(
  "4G_epc_microwave_shared_baseline_low_low",
  "4G_epc_fiber_shared_baseline_low_low",
  "5G_nsa_microwave_shared_baseline_low_low",
  "5G_sa_fiber_shared_baseline_low_low"),
  labels=c("4G (MW)",
           "4G (FB)",
           "5G NSA (MW)",
           "5G SA (FB)"))

panel <- ggplot(data, aes(x=strategy, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +  
  coord_flip() +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") + 
  labs(title = "Aggregate Cost Composition by Scenario, Strategy and Country", colour=NULL,
       subtitle = "Illustrates required state subsidy after exhausting all other policy options", 
       x = NULL, y = "Total Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol =10, reverse = TRUE)) +
  facet_wrap(~combined, scales = "free", ncol=3)

path = file.path(folder, 'figures', 'g_cost_composition_mixed_national.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()


##############DECILE COST PROFILE FOR BASELINE OPTIONS

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'decile_cost_results_mixed_options.csv'))

data <- data[!(data$total_cost == "NA"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- data[(data$strategy == '5G_nsa_microwave_shared_baseline_low_low'),]

data$combined <- paste(data$country, data$scenario, sep="_")

data <- select(data, combined, decile, ran, backhaul_fronthaul, 
               civils, core_network, ops_and_acquisition, spectrum_cost, tax, profit_margin, 
               used_cross_subsidy, required_state_subsidy)

data <- gather(data, metric, value, ran:required_state_subsidy)

data$combined = factor(data$combined, levels=c('MWI_S1_25_10_2',
                                               'MWI_S2_200_50_5',
                                               'MWI_S3_400_100_10',
                                               "UGA_S1_25_10_2",
                                               "UGA_S2_200_50_5",
                                               "UGA_S3_400_100_10",
                                               "SEN_S1_25_10_2",
                                               "SEN_S2_200_50_5",
                                               "SEN_S3_400_100_10",
                                               "KEN_S1_25_10_2",
                                               "KEN_S2_200_50_5",
                                               "KEN_S3_400_100_10",
                                               "PAK_S1_25_10_2",
                                               "PAK_S2_200_50_5",
                                               "PAK_S3_400_100_10",
                                               "ALB_S1_25_10_2",
                                               "ALB_S2_200_50_5",
                                               "ALB_S3_400_100_10",
                                               "PER_S1_25_10_2",
                                               "PER_S2_200_50_5",
                                               "PER_S3_400_100_10",
                                               "MEX_S1_25_10_2",
                                               "MEX_S2_200_50_5",
                                               "MEX_S3_400_100_10"),
                       labels=c("Malawi (C1) (S1: 25 Mbps)", "Malawi (C1) (S2: 200 Mbps)", "Malawi (C1) (S3: 400 Mbps)",
                                "Uganda (C1) (S1: 25 Mbps)", "Uganda (C1) (S2: 200 Mbps)", "Uganda (C1) (S3: 400 Mbps)",
                                "Senegal (C2) (S1: 25 Mbps)", "Senegal (C2) (S2: 200 Mbps)", "Senegal (C2) (S3: 400 Mbps)",
                                "Kenya (C2) (S1: 25 Mbps)", "Kenya (C2) (S2: 200 Mbps)", "Kenya (C2) (S3: 400 Mbps)",
                                "Pakistan (C3) (S1: 25 Mbps)", "Pakistan (C3) (S2: 200 Mbps)", "Pakistan (C3) (S3: 400 Mbps)",
                                "Albania (C4) (S1: 25 Mbps)", "Albania (C4) (S2: 200 Mbps)", "Albania (C4) (S3: 400 Mbps)",
                                "Peru (C5) (S1: 25 Mbps)", "Peru (C5) (S2: 200 Mbps)", "Peru (C5) (S3: 400 Mbps)",
                                "Mexico (C6) (S1: 25 Mbps)", "Mexico (C6) (S2: 200 Mbps)", "Mexico (C6) (S3: 400 Mbps)" ))


data$decile = factor(data$decile, levels=c(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100))

data$metric = factor(data$metric, levels=c("required_state_subsidy",
                                           "used_cross_subsidy",
                                           "profit_margin",
                                           "tax",
                                           "spectrum_cost",
                                           "ops_and_acquisition",
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
         "Ops",
         "RAN",
         "FH/BH",
         "Sites",
         'Core/Regional Fiber'
))

panel <- ggplot(data, aes(x=decile, y=(value/1e9), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom") + 
  labs(title = "Cost Composition by Scenario, Decile and Country", colour=NULL,
       subtitle = "Cumulative cost reported by percentage of population covered for 5G NSA (Microwave)", 
       x = "Population Covered (%)", y = "Cumulative Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0)) +  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol =10, reverse = TRUE)) +
  facet_wrap(~combined, scales = "free", ncol=3) 

path = file.path(folder, 'figures', 'h_cost_composition_mixed_decile.png')
ggsave(path, units="in", width=10, height=14.5, dpi=300)
print(panel)
dev.off()

####################################TOTAL COST AS % OF GDP

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

results <- read.csv(file.path(folder, '..', 'results', 'national_results_technology_options.csv'))
names(results)[names(results) == 'GID_0'] <- 'iso3'

gdp <- read.csv(file.path(folder, 'gdp.csv'))
names(gdp)[names(gdp) == 'iso3'] <- 'iso3'

results <- merge(results, gdp, by='iso3', all=FALSE)

results$gdp_percentage <- (results$total_cost / 5) / results$gdp * 100

results$combined <- paste(results$iso3, results$scenario, sep="_")

results$scenario = factor(results$scenario, levels=c("S1_25_10_2",
                                                     "S2_200_50_5",
                                                     "S3_400_100_10"),
                          labels=c("S1 (25 Mbps)",
                                   "S2 (200 Mbps)",
                                   "S3 (400 Mbps)"))

results$country = factor(results$iso3, levels=c('MWI',
                                             "UGA",
                                             "SEN",
                                             "KEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                      labels=c("Malawi","Uganda",
                               "Senegal","Kenya",
                               "Pakistan",
                               "Albania",
                               "Peru",
                               "Mexico"))

results$strategy = factor(results$strategy, levels=c("Revenue",
                                                     "4G_epc_microwave_baseline_baseline_baseline_baseline",
                                                     "4G_epc_fiber_baseline_baseline_baseline_baseline",
                                                     "5G_nsa_microwave_baseline_baseline_baseline_baseline",
                                                     "5G_sa_fiber_baseline_baseline_baseline_baseline"),
                          labels=c("Revenue",
                                   "4G (Microwave)",
                                   "4G (Fiber)",
                                   "5G NSA (Microwave)",
                                   "5G SA (Fiber)"))

results$confidence = factor(results$confidence, levels=c('5','50', '95'),
                            labels=c("lower", 'mean', "upper"))

wide <- select(results, country, scenario, strategy, confidence, gdp_percentage)
wide <- spread(wide, confidence, gdp_percentage)

gdp_percentage_ci <- ggplot(wide, aes(x=strategy, y=mean, fill=strategy)) +
  coord_flip() +
  geom_bar(stat="identity") +
  geom_errorbar(aes(ymin = lower, ymax = upper),width = 0.25) +
  theme( legend.position = NULL) +
  labs(colour=NULL,
       title = "Total Investment Cost as a Percentage of GDP Over 5 Years",
       subtitle = "Results reported by scenario, strategy and country for 95% confidence",
       x = NULL, y = "Percent of Annual GDP Over 5 Years") +
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(fill=FALSE) +
  facet_grid(country~scenario)

path = file.path(folder, 'figures', 'i_country_costs_by_gpd.png')
ggsave(path, units="in", width=8, height=10)
print(gdp_percentage_ci)
dev.off()

##################CLUSTER COSTS

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

results <- read.csv(file.path(folder, '..', 'results', 'national_results_technology_options.csv'))
names(results)[names(results) == 'GID_0'] <- 'iso3'

clusters <- read.csv(file.path(folder, 'clustering', 'results', 'data_clustering_results.csv'))
names(clusters)[names(clusters) == 'ISO_3digit'] <- 'iso3'
clusters <- select(clusters, iso3, cluster, country)

results <- merge(results, clusters, x.by='iso3', y.by='iso3', all=FALSE)

mean_user_cost_by_cluster <- select(results, scenario, strategy, confidence, cost_per_network_user, cluster)

mean_user_cost_by_cluster <- mean_user_cost_by_cluster %>% 
  group_by(scenario, strategy, confidence, cluster) %>%
  summarise(mean_cost_per_user = mean(cost_per_network_user))

results <- merge(clusters, mean_user_cost_by_cluster, x.by='cluster', y.by='cluster', all=TRUE)

gdp <- read.csv(file.path(folder, 'gdp.csv'))
names(gdp)[names(gdp) == 'iso3'] <- 'iso3'
gdp <- select(gdp, iso3, gdp)

results <- merge(results, gdp, by='iso3', all=FALSE)

pop <- read.csv(file.path(folder, 'population_2018.csv'))
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

results$scenario = factor(results$scenario, levels=c("S1_25_10_2",
                                                     "S2_200_50_5",
                                                     "S3_400_100_10"),
                          labels=c("S1 (25 Mbps)",
                                   "S2 (200 Mbps)",
                                   "S3 (400 Mbps)"))

results$strategy = factor(results$strategy, levels=c(
  "4G_epc_microwave_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline",
  "5G_nsa_microwave_baseline_baseline_baseline_baseline",
  "5G_sa_fiber_baseline_baseline_baseline_baseline"),
  labels=c(
    "4G (MW)",
    "4G (FB)",
    "5G NSA (MW)",
    "5G SA (FB)"))

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
  facet_grid(strategy~scenario)

gdp_num <- select(results, country, cluster, scenario, strategy, confidence, gdp_percentage)
gdp_num <- spread(gdp_num, confidence, gdp_percentage)

gdp_mean_summary_stats <- gdp_num %>% 
  group_by(cluster, scenario, strategy) %>% 
  summarize(Mean = mean(mean))

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
  facet_grid(strategy~scenario)

panel <- ggarrange(cost_by_strategy, gdp_perc_by_strategy, ncol = 1, nrow = 2, align = c("hv"))

#export to folder
path = file.path(folder, 'figures', 'j_cluster_costs_by_strategy.png')
ggsave(path, units="cm", width=22, height=33)
print(panel)
dev.off()

######GLOBAL COST

raw_mean_summary_stats <- raw_num %>% 
  group_by(cluster, scenario, strategy) %>% 
  summarize(Mean = mean(mean)/1e9)

raw_total_summary_stats <- raw_num %>% 
  group_by(scenario, strategy) %>% 
  summarize(lower = sum(lower)/1e9,
            mean = sum(mean)/1e9,
            upper = sum(upper)/1e9,)

unique(raw_num$country)

global_cost <- ggplot(raw_total_summary_stats, aes(x=strategy, y=mean/1e3, fill=strategy)) +
  coord_flip() +
  geom_bar(stat="identity") +
  geom_errorbar(aes(ymin = lower/1e3, ymax = upper/1e3),width = 0.25) +
  theme( legend.position = NULL) +
  labs(colour=NULL,
       title = "Global Investment Cost: Low- and Middle-Income Countries (N=173)",
       subtitle = "Results reported by scenario and strategy at 95% confidence",
       x = NULL, y = "Investment Cost ($USD Trillions)") +
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(fill=FALSE) +
  facet_grid(~scenario)

#export to folder
path = file.path(folder, 'figures', 'k_global_costs_by_strategy.png')
ggsave(path, units="cm", width=18, height=8)
print(global_cost)
dev.off()
