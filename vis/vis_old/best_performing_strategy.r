###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)
library(ggpubr)
# install.packages('kableExtra')
library(kableExtra)
# install.packages("magick")
library(magick)
# install.packages("webshot")
# webshot::install_phantomjs()

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#technology
data_tech <- read.csv(file.path(folder, '..', 'results', 'national_market_results_technology_options.csv'))
data_tech <- select(data_tech, GID_0, scenario, strategy, confidence, total_market_cost)

data_tech <- data_tech[(data_tech$confidence == 50),]

baseline <- data_tech %>%
  filter(str_detect(strategy, "_baseline_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
baseline$strategy_summary = 'baseline'

#business model
data_bus_mod <- read.csv(file.path(folder, '..', 'results', 'national_market_results_business_model_options.csv'))
data_bus_mod <- select(data_bus_mod, GID_0, scenario, strategy, confidence, total_market_cost)
data_bus_mod <- data_bus_mod[(data_bus_mod$confidence == 50),]

passive <- data_bus_mod %>%
  filter(str_detect(strategy, "_passive_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
passive$strategy_summary = 'passive'

active <- data_bus_mod %>%
  filter(str_detect(strategy, "_active_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
active$strategy_summary = 'active'

shared <- data_bus_mod %>%
  filter(str_detect(strategy, "_shared_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
shared$strategy_summary = 'shared'

#policy options
data_policy <- read.csv(file.path(folder, '..', 'results', 'national_market_results_policy_options.csv'))
data_policy <- select(data_policy, GID_0, scenario, strategy, confidence, total_market_cost)
data_policy <- data_policy[(data_policy$confidence == 50),]

spectrum_low <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_low_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
spectrum_low$strategy_summary = 'spectrum_low'

spectrum_high <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_high_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
spectrum_high$strategy_summary = 'spectrum_high'

tax_low <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_low")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
tax_low$strategy_summary = 'tax_low'

tax_high <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_high")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
tax_high$strategy_summary = 'tax_high'

#Mixed options
data_mixed <- read.csv(file.path(folder, '..', 'results', 'decile_market_results_mixed_options.csv'))
data_mixed <- data_mixed[(data_mixed$confidence == 50),]
data_mixed <- select(data_mixed, GID_0, scenario, strategy, decile, total_market_cost)

mixed <- data_mixed %>%
  filter(str_detect(strategy, "_shared_baseline_low_low")) %>% 
  group_by(GID_0, scenario) %>%
  filter(total_market_cost == min(total_market_cost)) 
mixed$strategy_summary = 'mixed'

####################
#Aggregate results
results = rbind(baseline, passive, active, shared, 
                spectrum_low, spectrum_high,
                tax_low, tax_high, mixed)

results$tech = sapply(strsplit(results$strategy, "_"), "[", 1)
results$backhaul = sapply(strsplit(results$strategy, "_"), "[", 3)

rm(data_tech, data_bus_mod, data_policy, baseline, passive, active, shared, 
   spectrum_low, spectrum_high, tax_low, tax_high)

results$GID_0 = factor(results$GID_0,
         levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
         labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 'Pakistan', 'Albania', 'Peru', 'Mexico'))
results$strategy_summary = factor(results$strategy_summary,
        levels=c('baseline', 'passive', 'active', 'shared', 
                 'spectrum_low', 'spectrum_high', 'tax_low', 'tax_high', 'mixed'),
        labels = c('Baseline', 'Passive', 'Active', 'Neutral',
                   'Low P.', 'High P.', 'Low T.', 'High T.', 'Mixed'))
results$scenario = factor(results$scenario,
        levels=c('S1_25_10_2', 'S2_200_50_5', 'S3_400_100_10'),
        labels=c('S1', 'S2', 'S3'))

results = with(results, results[order(GID_0, scenario, strategy_summary),])

results$tech_strategy = with(results, paste0(tech, '_', backhaul))
results$tech_strategy[results$tech_strategy == '4G_microwave'] <- '4G (W)'
results$tech_strategy[results$tech_strategy == '5G_microwave'] <- '5G NSA (W)'

results = select(results, GID_0, scenario, strategy_summary, tech_strategy)

# path = file.path(folder, 'vis_results', 'a_cheapest_strategies.csv')
# write.csv(results, path, row.names=FALSE)

names(results)[names(results)=="GID_0"] <- "Country"
names(results)[names(results)=="scenario"] <- "Scenario"

results = results %>%
  pivot_wider(names_from = strategy_summary, values_from = tech_strategy)

results = kbl(results, 'html',
  caption = "Best performing technology for each country under all scenarios and strategies") %>%
  kable_classic("striped",full_width = F, html_font = "Cambria") %>%
  add_header_above(
    c(" "= 3, 
      "Infrastructure Sharing" = 3, 
      "Spectrum Pricing" = 2, 
      "Taxation" = 2,
      " " = 1)) 

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(results, file = 'a_best_performing_technology.png', zoom = 1.5)

#################
#viability
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#technology
data_revenue <- read.csv(file.path(folder, '..', 'results', 'national_market_results_technology_options.csv'))
data_revenue <- data_revenue[(data_revenue$confidence == 50),]
data_revenue <- select(data_revenue, GID_0, scenario, strategy,  total_market_revenue)

data_tech <- read.csv(file.path(folder, '..', 'results', 'decile_market_results_technology_options.csv'))
data_tech <- data_tech[(data_tech$confidence == 50),]
data_tech <- select(data_tech, GID_0, scenario, strategy,  decile, total_market_cost)

data_tech <- merge(data_tech, data_revenue, by=c('GID_0', 'strategy', 'scenario'))

data_tech <- data_tech[order(data_tech$GID_0, data_tech$scenario, data_tech$strategy, data_tech$decile),]

data_tech <- data_tech %>%
  group_by(GID_0, strategy, scenario) %>%
  mutate(
    total_market_revenue = round(total_market_revenue / 1e9,3),
    cumulative_cost_bn = cumsum(round(total_market_cost / 1e9, 3)))

data_tech <- data_tech %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_market_revenue >= cumulative_cost_bn)

data_tech <- data_tech %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(decile == max(decile)) 

data_tech$strategy_summary = 'baseline'
data_tech$strategy <- as.character(data_tech$strategy)
data_tech$tech = sapply(strsplit(data_tech$strategy, "_"), "[", 1)
data_tech$core = sapply(strsplit(data_tech$strategy, "_"), "[", 2)
data_tech$backhaul = sapply(strsplit(data_tech$strategy, "_"), "[", 3)

data_tech = data_tech[!(data_tech$backhaul == 'fiber' & data_tech$core == "nsa"), ]
data_tech = data_tech[!(data_tech$backhaul == 'microwave' & data_tech$core == "sa"), ]

data_tech$tech = NULL
data_tech$core = NULL
data_tech$backhaul = NULL

#business model
data_revenue <- read.csv(file.path(folder, '..', 'results', 'national_market_results_business_model_options.csv'))
data_revenue <- data_revenue[(data_revenue$confidence == 50),]
data_revenue <- select(data_revenue, GID_0, scenario, strategy, total_market_revenue)

data_bus_mod <- read.csv(file.path(folder, '..', 'results', 'decile_market_results_business_model_options.csv'))
data_bus_mod <- data_bus_mod[(data_bus_mod$confidence == 50),]
data_bus_mod <- select(data_bus_mod, GID_0, scenario, strategy, decile, total_market_cost)

data_bus_mod <- merge(data_bus_mod, data_revenue, by=c('GID_0', 'strategy', 'scenario'))

data_bus_mod <- data_bus_mod[order(data_bus_mod$GID_0, data_bus_mod$scenario, data_bus_mod$strategy, data_bus_mod$decile),]

data_bus_mod <- data_bus_mod %>%
  group_by(GID_0, strategy, scenario) %>%
  mutate(
    total_market_revenue = total_market_revenue/1e9,
    cumulative_cost_bn = cumsum(round(total_market_cost / 1e9, 3)))

data_bus_mod <- data_bus_mod %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_market_revenue >= cumulative_cost_bn)

data_bus_mod <- data_bus_mod %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(decile == max(decile)) 

data_bus_mod$strategy <- as.character(data_bus_mod$strategy)

data_bus_mod$strategy_summary = sapply(strsplit(data_bus_mod$strategy, "_"), "[", 4)

data_bus_mod = data_bus_mod[!(data_bus_mod$strategy_summary == 'baseline'), ]

#policy
data_revenue <- read.csv(file.path(folder, '..', 'results', 'national_market_results_policy_options.csv'))
data_revenue <- data_revenue[(data_revenue$confidence == 50),]
data_revenue <- select(data_revenue, GID_0, scenario, strategy, total_market_revenue)

data_policy <- read.csv(file.path(folder, '..', 'results', 'decile_market_results_policy_options.csv'))
data_policy <- data_policy[(data_policy$confidence == 50),]
data_policy <- select(data_policy, GID_0, scenario, strategy, decile, total_market_cost)

data_policy <- merge(data_policy, data_revenue, by=c('GID_0', 'strategy', 'scenario'))

data_policy <- data_policy[order(data_policy$GID_0, data_policy$scenario, data_policy$strategy, data_policy$decile),]

data_policy <- data_policy %>%
  group_by(GID_0, strategy, scenario) %>%
  mutate(
    total_market_revenue = total_market_revenue/1e9,
    cumulative_cost_bn = cumsum(round(total_market_cost / 1e9, 3)))

data_policy <- data_policy %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_market_revenue >= cumulative_cost_bn)

data_policy <- data_policy %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(decile == max(decile)) 

spectrum_low = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_low_baseline")) 
spectrum_low$strategy_summary = 'spectrum_low'

spectrum_high = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_high_baseline")) 
spectrum_high$strategy_summary = 'spectrum_high'

tax_low = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_low")) 
tax_low$strategy_summary = 'tax_low'

tax_high = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_high")) 
tax_high$strategy_summary = 'tax_high'

#mixed
data_revenue <- read.csv(file.path(folder, '..', 'results', 'national_market_results_mixed_options.csv'))
data_revenue <- data_revenue[(data_revenue$confidence == 50),]
data_revenue <- select(data_revenue, GID_0, scenario, strategy, total_market_revenue)

data_mixed <- read.csv(file.path(folder, '..', 'results', 'decile_market_results_mixed_options.csv'))
data_mixed <- data_mixed[(data_mixed$confidence == 50),]
data_mixed <- select(data_mixed, GID_0, scenario, strategy, decile, total_market_cost)

data_mixed <- merge(data_mixed, data_revenue, by=c('GID_0', 'strategy', 'scenario'))

data_mixed <- data_mixed[order(data_mixed$GID_0, data_mixed$scenario, data_mixed$strategy, data_mixed$decile),]

data_mixed <- data_mixed %>%
  group_by(GID_0, strategy, scenario) %>%
  mutate(
    total_market_revenue = total_market_revenue/1e9,
    cumulative_cost_bn = cumsum(round(total_market_cost / 1e9, 3)))

data_mixed <- data_mixed %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_market_revenue >= cumulative_cost_bn)
data_mixed$strategy_summary = 'mixed'

data_mixed <- data_mixed %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(decile == max(decile)) 

########
results = rbind(data_tech, data_bus_mod, data_mixed,
                spectrum_low, spectrum_high,
                tax_low, tax_high)

results$tech = sapply(strsplit(results$strategy, "_"), "[", 1)
results$core = sapply(strsplit(results$strategy, "_"), "[", 2)
results$backhaul = sapply(strsplit(results$strategy, "_"), "[", 3)

results = results[!(results$backhaul == 'fiber' & results$core == "nsa"), ]
results = results[!(results$backhaul == 'microwave' & results$core == "sa"), ]

results$tech_strategy = with(results, paste0(
  tech, '_', core, '_',backhaul))

rm(data_tech, data_bus_mod, data_policy, data_mixed, data_revenue,
   spectrum_low, spectrum_high, tax_low, tax_high)

results = select(results, GID_0, scenario, strategy_summary, tech_strategy, decile)

results$GID_0 = factor(results$GID_0,
                       levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
                       labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 'Pakistan', 'Albania', 'Peru', 'Mexico'))
results$scenario = factor(results$scenario,
                      levels=c('S1_25_10_2', 'S2_200_50_5', 'S3_400_100_10'),
                      #labels=c('S1 (25 Mbps)', 'S2 (200 Mbps)', 'S3 (400 Mbps)'))
                      labels=c('S1', 'S2', 'S3'))
results$tech_strategy = factor(results$tech_strategy,
                       levels=c('4G_epc_microwave', '4G_epc_fiber', 
                                '5G_nsa_microwave', '5G_sa_fiber'),
                       labels=c('4G (W)', '4G (F)', '5G NSA (W)', '5G SA (F)'))

results = with(results, results[order(GID_0, scenario, strategy_summary, tech_strategy),])
results$strategy = NULL
results$Metric = 'Viability'

names(results)[names(results)=="GID_0"] <- "Country"
names(results)[names(results)=="scenario"] <- "Scenario"
names(results)[names(results)=="tech_strategy"] <- "Strategy"

results_viability = results %>%
  pivot_wider(names_from = strategy_summary, values_from = decile)

results_viability = results_viability %>% complete(Scenario, nesting(Country, Strategy, Metric), 
                            fill = list(baseline = 0,
                                        passive = 0, 
                                        active = 0, 
                                        shared = 0,
                                        spectrum_low = 0, 
                                        spectrum_high = 0, 
                                        tax_low = 0, 
                                        tax_high = 0,
                                        mixed = 0
                            ))

col_order <- c('Country', 'Scenario', 'Strategy', 'Metric', 'baseline', 
               'passive', 'active', 'shared', 'spectrum_low', 'spectrum_high', 
               'tax_low', 'tax_high', 'mixed')
results_viability <- results_viability[, col_order]

names(results_viability)[names(results_viability)=="baseline"] <- "Baseline"
names(results_viability)[names(results_viability)=="passive"] <- "Passive"
names(results_viability)[names(results_viability)=="active"] <- "Active"
names(results_viability)[names(results_viability)=="shared"] <- "Neutral"
names(results_viability)[names(results_viability)=="spectrum_low"] <- "Low P."
names(results_viability)[names(results_viability)=="spectrum_high"] <- "High P."
names(results_viability)[names(results_viability)=="tax_low"] <- "Low T."
names(results_viability)[names(results_viability)=="tax_high"] <- "High T."
names(results_viability)[names(results_viability)=="mixed"] <- "Mixed"

rm(results)

results_viability[is.na(results_viability)] <- 0

#create plotting function
viability_table <- function(x, df, y){

  df = df[(df$Country == x),]

  df = kbl(df, 'html',
    caption = "Percentage coverage by population decile that can be achieved on a commercially viable basis") %>%
    kable_classic('striped', full_width = F, html_font = "Cambria") %>%
    add_header_above(
      c(" "= 5, 
        "Infrastructure Sharing" = 3, 
        "Spectrum Pricing" = 2, 
        "Taxation" = 2,
        ' ' = 1)) 
  
  folder <- dirname(rstudioapi::getSourceEditorContext()$path)
  path = file.path(folder, 'tables')
  setwd(path)
  kableExtra::save_kable(df, file=y, zoom = 1.5)
}

viability_table('Malawi', results_viability, 'b_viability_a_malawi.png')
viability_table('Uganda', results_viability, 'b_viability_b_uganda.png')
viability_table('Senegal', results_viability, 'b_viability_c_senegal.png')
viability_table('Kenya', results_viability, 'b_viability_d_kenya.png')
viability_table('Pakistan', results_viability, 'b_viability_e_pakistan.png')
viability_table('Albania', results_viability, 'b_viability_f_albania.png')
viability_table('Peru', results_viability, 'b_viability_g_peru.png')
viability_table('Mexico', results_viability, 'b_viability_h_mexico.png')

path = file.path(folder,'vis_results', 'b_viability_of_strategies.csv')
write.csv(results_viability, path, row.names=FALSE)

#################
#societal cost = MNO cost + govt cost
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#technology
data_tech <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))
data_tech <- data_tech[(data_tech$confidence == 50),]

# data_tech$private_cost = data_tech$total_market_cost
# data_tech$government_cost = (data_tech$total_required_state_subsidy - data_tech$total_spectrum_cost) - data_tech$total_tax
# data_tech$societal_cost = data_tech$total_market_cost + data_tech$total_government_cost
# data_tech$private_cost = data_tech$private_cost
# data_tech$government_cost = (data_tech$total_required_state_subsidy - data_tech$total_spectrum_cost) - data_tech$total_tax
# data_tech$societal_cost = data_tech$total_market_cost + data_tech$total_government_cost

data_tech$strategy_summary = 'baseline'
data_tech$strategy <- as.character(data_tech$strategy)
data_tech$tech = sapply(strsplit(data_tech$strategy, "_"), "[", 1)
data_tech$core = sapply(strsplit(data_tech$strategy, "_"), "[", 2)
data_tech$backhaul = sapply(strsplit(data_tech$strategy, "_"), "[", 3)

data_tech = data_tech[!(data_tech$backhaul == 'fiber' & data_tech$core == "nsa"), ]
data_tech = data_tech[!(data_tech$backhaul == 'microwave' & data_tech$core == "sa"), ]

data_tech$tech = NULL
data_tech$core = NULL
data_tech$backhaul = NULL

#bus_mod
data_bus_mod <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_business_model_options.csv'))
data_bus_mod <- data_bus_mod[(data_bus_mod$confidence == 50),]

# data_bus_mod$private_cost = data_bus_mod$total_market_cost
# data_bus_mod$government_cost = (data_bus_mod$total_required_state_subsidy - 
#                                   data_bus_mod$total_spectrum_cost - 
#                                   data_bus_mod$total_tax)
# data_bus_mod$societal_cost = data_bus_mod$private_cost + data_bus_mod$government_cost

data_bus_mod$strategy <- as.character(data_bus_mod$strategy)

data_bus_mod$strategy_summary = sapply(strsplit(data_bus_mod$strategy, "_"), "[", 4)

data_bus_mod = data_bus_mod[!(data_bus_mod$strategy_summary == 'baseline'), ]

#policy
data_policy <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_policy_options.csv'))
data_policy <- data_policy[(data_policy$confidence == 50),]

# data_policy$private_cost = data_policy$total_market_cost
# data_policy$government_cost = (data_policy$total_required_state_subsidy - 
#                                  data_policy$total_spectrum_cost - 
#                                  data_policy$total_tax)
# # data_policy$government_cost[data_policy$government_cost < 0 ] <- 0
# data_policy$societal_cost = data_policy$total_market_cost + data_policy$government_cost

spectrum_low = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_low_baseline")) 
spectrum_low$strategy_summary = 'spectrum_low'

spectrum_high = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_high_baseline")) 
spectrum_high$strategy_summary = 'spectrum_high'

tax_low = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_low")) 
tax_low$strategy_summary = 'tax_low'

tax_high = data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_high")) 
tax_high$strategy_summary = 'tax_high'

#mixed
data_mixed <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_mixed_options.csv'))
data_mixed <- data_mixed[(data_mixed$confidence == 50),]
# data_mixed$private_cost = data_mixed$total_market_cost
# data_mixed$government_cost = (data_mixed$total_required_state_subsidy - 
#                                 (data_mixed$total_spectrum_cost + 
#                                 data_mixed$total_tax))
# data_mixed$societal_cost = data_mixed$private_cost + data_mixed$government_cost

data_mixed$strategy <- as.character(data_mixed$strategy)

data_mixed$strategy_summary = 'mixed'

data_mixed = data_mixed[!(data_mixed$strategy_summary == 'baseline'), ]

#combine
results = rbind(data_tech, data_bus_mod, data_mixed, 
                spectrum_low, spectrum_high,
                tax_low, tax_high)

results$strategy = as.character(results$strategy)
results$tech = sapply(strsplit(results$strategy, "_"), "[", 1)
results$core = sapply(strsplit(results$strategy, "_"), "[", 2)
results$backhaul = sapply(strsplit(results$strategy, "_"), "[", 3)

results = results[!(results$backhaul == 'fiber' & results$core == "nsa"), ]
results = results[!(results$backhaul == 'microwave' & results$core == "sa"), ]

results$tech_strategy = with(results, paste0(
  tech, '_', core, '_',backhaul))

rm(data_tech, data_bus_mod, data_policy, data_revenue,
   spectrum_low, spectrum_high, tax_low, tax_high)

results = select(results, GID_0, scenario, tech_strategy, strategy_summary,
                societal_cost, private_cost, government_cost,
                )

results$private_cost = round(results$private_cost/1e6)
results$government_cost = round(results$government_cost/1e6)
results$societal_cost = round(results$societal_cost/1e6)

results$GID_0 = factor(results$GID_0,
                       levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
                       labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 'Pakistan', 'Albania', 'Peru', 'Mexico'))
results$strategy_summary = factor(results$strategy_summary,
                                  levels=c('baseline', 'passive', 'active', 'shared', 
                                   'spectrum_low', 'spectrum_high', 'tax_low', 'tax_high', 'mixed'),
                                  labels = c('Baseline', 'Passive', 'Active', 'Neutral',
                                       'Low P.', 'High P.', 'Low T.', 'High T.', 'Mixed'))
results$scenario = factor(results$scenario,
                          levels=c('S1_25_10_2', 'S2_200_50_5', 'S3_400_100_10'),
                          labels=c('S1', 'S2', 'S3'))
results$tech_strategy = factor(results$tech_strategy,
                               levels=c('4G_epc_microwave', '4G_epc_fiber', 
                                        '5G_nsa_microwave', '5G_sa_fiber'),
                               labels=c('4G (W)', '4G (F)', '5G NSA (W)', '5G SA (F)'))

names(results)[names(results)=="GID_0"] <- "Country"
names(results)[names(results)=="scenario"] <- "Scenario"
names(results)[names(results)=="tech_strategy"] <- "Strategy"

path = file.path(folder, 'vis_results', 'c_societal_costs.csv')
write.csv(results, path, row.names=FALSE)

#create plotting function
cost_table <- function(df, x, y, z, a){
  
  df = select(df, Country, Scenario, Strategy, strategy_summary, y)
  df = df[(df$Country == x),]
  
  df = df %>%
    pivot_wider(names_from = strategy_summary, values_from = y)

  df = select(df, 'Country', 'Scenario', 'Strategy', 'Baseline', 'Passive', 'Active', 'Neutral',
              'Low P.', 'High P.', 'Low T.', 'High T.', 'Mixed')
  
  df[is.na(df)] <- 0

  df = kbl(df, 'html',
    caption = a) %>%
    kable_classic("striped", full_width = F, html_font = "Cambria") %>%

        add_header_above(
      c(" "= 4, 
        "Infrastructure Sharing" = 3, 
        "Spectrum Pricing" = 2, 
        "Taxation" = 2,
        " " = 1))

  folder <- dirname(rstudioapi::getSourceEditorContext()$path)
  path = file.path(folder, 'tables')
  setwd(path)
  kableExtra::save_kable(df, file=z, zoom = 1.5)
}

a = 'Total societal cost ($m) of reaching universal access (operator cost plus net cost to government)'
cost_table(results, 'Malawi', 'societal_cost', 'c_societal_cost_a_malawi.png', a)
cost_table(results, 'Uganda', 'societal_cost', 'c_societal_cost_b_uganda.png', a)
cost_table(results, 'Senegal', 'societal_cost', 'c_societal_cost_c_senegal.png', a)
cost_table(results, 'Kenya', 'societal_cost', 'c_societal_cost_d_kenya.png', a)
cost_table(results, 'Pakistan', 'societal_cost', 'c_societal_cost_e_pakistan.png', a)
cost_table(results, 'Albania', 'societal_cost', 'c_societal_cost_f_albania.png', a)
cost_table(results, 'Peru', 'societal_cost', 'c_societal_cost_g_peru.png', a)
cost_table(results, 'Mexico', 'societal_cost', 'c_societal_cost_h_mexico.png', a)

a = 'Total cost ($m) of reaching universal access to operators'
cost_table(results, 'Malawi', 'private_cost', 'd_private_cost_a_malawi.png', a)
cost_table(results, 'Uganda', 'private_cost', 'd_private_cost_b_uganda.png', a)
cost_table(results, 'Senegal', 'private_cost', 'd_private_cost_c_senegal.png', a)
cost_table(results, 'Kenya', 'private_cost', 'd_private_cost_d_kenya.png', a)
cost_table(results, 'Pakistan', 'private_cost', 'd_private_cost_e_pakistan.png', a)
cost_table(results, 'Albania', 'private_cost', 'd_private_cost_f_albania.png', a)
cost_table(results, 'Peru', 'private_cost', 'd_private_cost_g_peru.png', a)
cost_table(results, 'Mexico', 'private_cost', 'd_private_cost_h_mexico.png', a)

a = 'Total net cost ($m) of reaching universal access to government (subsidy outlay minus revenues from spectrum fees and taxes)'
cost_table(results, 'Malawi', 'government_cost', 'e_government_cost_a_malawi.png', a)
cost_table(results, 'Uganda', 'government_cost', 'e_government_cost_b_uganda.png', a)
cost_table(results, 'Senegal', 'government_cost', 'e_government_cost_c_senegal.png', a)
cost_table(results, 'Kenya', 'government_cost', 'e_government_cost_d_kenya.png', a)
cost_table(results, 'Pakistan', 'government_cost', 'e_government_cost_e_pakistan.png', a)
cost_table(results, 'Albania', 'government_cost', 'e_government_cost_f_albania.png', a)
cost_table(results, 'Peru', 'government_cost', 'e_government_cost_g_peru.png', a)
cost_table(results, 'Mexico', 'government_cost', 'e_government_cost_h_mexico.png', a)






#TABLE1
results_wide <- gather(results, Metric, value, societal_cost:government_cost)

results_wide = results_wide %>%
  pivot_wider(names_from = strategy_summary, values_from = value) 

results_wide = select(results_wide, Country, Scenario, Strategy, Metric, Baseline)

results_wide = results_wide %>%
  pivot_wider(names_from = Country, values_from = Baseline) 

results_wide = with(results_wide, results_wide[order(Scenario, Strategy, Metric),])

results_wide$Metric = factor(results_wide$Metric,
   levels=c('private_cost', 'government_cost', 'societal_cost'),
   labels=c('Private Cost ($m)', 'Government Cost ($m)','Societal Cost ($m)'))

table1 = kbl(results_wide, 'html', caption = 'Baseline Technology Results by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria")

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table1, file='table1_baseline_tech_country_costs.png', zoom = 1.5)

#TABLE2
results_wide <- gather(results, Metric, value, societal_cost:government_cost)

results_wide = results_wide[(results_wide$Strategy == '5G NSA (W)'),]

results_wide = results_wide[
  (results_wide$strategy_summary == "Baseline" | 
   results_wide$strategy_summary == "Passive" |
     results_wide$strategy_summary == "Active" | 
     results_wide$strategy_summary == "Neutral" ), ]

results_wide = results_wide %>%
  pivot_wider(names_from = Country, values_from = value) 

results_wide$Strategy = NULL
# names(results_wide)[names(results_wide)=="Strategy"] <- "Technology"
names(results_wide)[names(results_wide)=="strategy_summary"] <- "Strategy"

results_wide$Metric = factor(results_wide$Metric,
                   levels=c('private_cost', 'government_cost', 'societal_cost'),
                   labels=c('Private Cost ($m)', 'Government Cost ($m)','Societal Cost ($m)'))


results_wide = with(results_wide, results_wide[order(Scenario, Strategy),])

table2 = kbl(results_wide, 'html', caption = 'Infrastructure Sharing Results by Country') %>%
    kable_classic("striped", full_width = F, html_font = "Cambria")
  
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table2, file='table2_infra_sharing_country_costs.png', zoom = 1.5)


#TABLE3
results_wide <- gather(results, Metric, value, societal_cost:government_cost)

results_wide = results_wide[(results_wide$Strategy == '5G NSA (W)'),]

results_wide = results_wide[
  (results_wide$strategy_summary == "Baseline" | 
     results_wide$strategy_summary == "Low P." |
     results_wide$strategy_summary == "High P."), ]

results_wide = results_wide %>%
  pivot_wider(names_from = Country, values_from = value) 

results_wide$Strategy = NULL

names(results_wide)[names(results_wide)=="strategy_summary"] <- "Strategy"

results_wide$Metric = factor(results_wide$Metric,
                             levels=c('private_cost', 'government_cost', 'societal_cost'),
                             labels=c('Private Cost ($m)', 'Government Cost ($m)','Societal Cost ($m)'))

results_wide$Strategy = factor(results_wide$Strategy,
                   levels=c('Low P.', 'Baseline', 'High P.'),
                   labels=c('Low Prices (-50%)', 'Baseline','High Prices (+50%)'))

results_wide = with(results_wide, results_wide[order(Scenario, Strategy),])

table3 = kbl(results_wide, 'html', caption = 'Spectrum Pricing Results by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria")

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table3, file='table3_spectrum_pricing_country_costs.png', zoom = 1.5)








results_costs = with(results, results[order(Country, Scenario, strategy_summary, Strategy),])
results_costs$strategy = NULL

path = file.path(folder, 'vis_results', 'd_results_costs.csv')
write.csv(results_costs, path, row.names=FALSE)

results_by_country <- gather(results_costs, Metric, value, societal_cost:government_cost)

results_by_country = results_by_country %>%
  pivot_wider(names_from = strategy_summary, values_from = value) 

results_by_country = rbind(results_by_country, results_viability)

results_by_country$Metric = factor(results_by_country$Metric,
         levels=c('Viability', 'private_cost', 'government_cost', 'societal_cost'),
         labels=c('Viability (Decile)', 'Private Cost ($m)', 'Government Cost ($m)',
                  'Societal Cost ($m)'
         ))

path = file.path(folder, 'vis_results', 'd_all_results.csv')
write.csv(results_by_country, path, row.names=FALSE)

#create plotting function
cost_by_country <- function(df, x, y, z){
  
  df = df[(df$Country == x),]

  df = with(df, df[order(Country, Scenario, Strategy, Metric),])
  
  df = kbl(df, 'html',
           caption = z) %>%
    kable_classic("striped", full_width = F, html_font = "Cambria") %>%
    add_header_above(
      c(" "= 5, 
        "Infrastructure Sharing" = 3, 
        "Spectrum Pricing" = 2, 
        "Taxation" = 2,
        " " = 1))
  
  folder <- dirname(rstudioapi::getSourceEditorContext()$path)
  path = file.path(folder, 'tables')
  setwd(path)
  kableExtra::save_kable(df, file=y, zoom = 1.5)
}

a = 'Results by Country'
cost_by_country(results_by_country, 'Malawi', 'f_country_costs_a_malawi.png', a)
cost_by_country(results_by_country, 'Uganda', 'f_country_costs_b_uganda.png', a)
cost_by_country(results_by_country, 'Senegal', 'f_country_costs_c_senegal.png', a)
cost_by_country(results_by_country, 'Kenya', 'f_country_costs_d_kenya.png', a)
cost_by_country(results_by_country, 'Pakistan', 'f_country_costs_e_pakistan.png', a)
cost_by_country(results_by_country, 'Albania', 'f_country_costs_f_albania.png', a)
cost_by_country(results_by_country, 'Peru', 'f_country_costs_g_peru.png', a)
cost_by_country(results_by_country, 'Mexico', 'f_country_costs_h_mexico.png', a)

