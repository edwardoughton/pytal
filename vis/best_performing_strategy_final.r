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
data_tech <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))
data_tech <- select(data_tech, GID_0, scenario, strategy, confidence, societal_cost)
data_tech$societal_cost = round(data_tech$societal_cost/1e9,2)
data_tech <- data_tech[(data_tech$confidence == 50),]

baseline <- data_tech %>%
  filter(str_detect(strategy, "_baseline_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
baseline$strategy_summary = 'baseline'

#business model
data_bus_mod <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_business_model_options.csv'))
data_bus_mod <- select(data_bus_mod, GID_0, scenario, strategy, confidence, societal_cost)
data_bus_mod <- data_bus_mod[(data_bus_mod$confidence == 50),]

passive <- data_bus_mod %>%
  filter(str_detect(strategy, "_passive_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
passive$strategy_summary = 'passive'

active <- data_bus_mod %>%
  filter(str_detect(strategy, "_active_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
active$strategy_summary = 'active'

shared <- data_bus_mod %>%
  filter(str_detect(strategy, "_shared_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
shared$strategy_summary = 'shared'

#policy options
data_policy <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_policy_options.csv'))
data_policy <- select(data_policy, GID_0, scenario, strategy, confidence, societal_cost)
data_policy <- data_policy[(data_policy$confidence == 50),]

spectrum_low <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_low_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
spectrum_low$strategy_summary = 'spectrum_low'

spectrum_high <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_high_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
spectrum_high$strategy_summary = 'spectrum_high'

tax_low <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_low")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
tax_low$strategy_summary = 'tax_low'

tax_high <- data_policy %>%
  filter(str_detect(strategy, "baseline_baseline_baseline_high")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
tax_high$strategy_summary = 'tax_high'

#Mixed options
data_mixed <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_mixed_options.csv'))
data_mixed <- data_mixed[(data_mixed$confidence == 50),]
data_mixed <- select(data_mixed, GID_0, scenario, strategy, confidence, societal_cost)

mixed <- data_mixed %>%
  filter(str_detect(strategy, "_shared_baseline_low_low")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
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
results$scenario = factor(results$scenario, levels=c("S1_25_10_2",
                                                     "S2_200_50_5",
                                                     "S3_400_100_10"),
                          labels=c("S1 (<25 Mbps)",
                                   "S2 (<200 Mbps)",
                                   "S3 (<400 Mbps)"))

results = with(results, results[order(GID_0, scenario, strategy_summary),])

results$tech_strategy = with(results, paste0(tech, '_', backhaul))
results$tech_strategy[results$tech_strategy == '4G_microwave'] <- '4G (W)'
results$tech_strategy[results$tech_strategy == '5G_microwave'] <- '5G NSA (W)'

results = select(results, GID_0, scenario, strategy_summary, tech_strategy)

results$strategy_summary = as.factor(results$strategy_summary)
results$tech_strategy = as.factor(results$tech_strategy)

path = file.path(folder, 'vis_results', 'a_cheapest_strategies.csv')
write.csv(results, path, row.names=FALSE)

names(results)[names(results)=="GID_0"] <- "Country"
names(results)[names(results)=="scenario"] <- "Scenario"

results = results %>%
  pivot_wider(names_from = strategy_summary, values_from = tech_strategy)

results = results %>%
  mutate(baseline = cell_spec(baseline, "html", 
    color=ifelse(grepl("4G (W)", baseline, fixed = T), "blue", "black"))) %>%
  mutate(passive = cell_spec(passive, "html", 
    color=ifelse(grepl("4G (W)", passive, fixed = T), "blue", "black"))) %>%
  mutate(active = cell_spec(active, "html", 
     color=ifelse(grepl("4G (W)", active, fixed = T), "blue", "black"))) %>%
  mutate(shared = cell_spec(shared, "html", 
     color=ifelse(grepl("4G (W)", shared, fixed = T), "blue", "black"))) %>%
  mutate(spectrum_low = cell_spec(spectrum_low, "html", 
     color=ifelse(grepl("4G (W)", spectrum_low, fixed = T), "blue", "black"))) %>%
  mutate(spectrum_high = cell_spec(spectrum_high, "html", 
     color=ifelse(grepl("4G (W)", spectrum_high, fixed = T), "blue", "black"))) %>%
  mutate(tax_low = cell_spec(tax_low, "html", 
     color=ifelse(grepl("4G (W)", tax_low, fixed = T), "blue", "black"))) %>%
  mutate(tax_high = cell_spec(tax_high, "html", 
     color=ifelse(grepl("4G (W)", tax_high, fixed = T), "blue", "black"))) %>%
  mutate(mixed = cell_spec(mixed, "html", 
     color=ifelse(grepl("4G (W)", mixed, fixed = T), "blue", "black")))

results = select(results, Country, Scenario, baseline, passive, active, shared, 
                 spectrum_low, spectrum_high, tax_low, tax_high, mixed)

names(results)[names(results)=="baseline"] <- "Baseline"
names(results)[names(results)=="passive"] <- "Passive"
names(results)[names(results)=="active"] <- "Active"
names(results)[names(results)=="shared"] <- "SRN"
names(results)[names(results)=="spectrum_low"] <- "Low P."
names(results)[names(results)=="spectrum_high"] <- "High P."
names(results)[names(results)=="tax_low"] <- "Low T."
names(results)[names(results)=="tax_high"] <- "High T."
names(results)[names(results)=="mixed"] <- "Lowest"

results = kable(results, "html", escape = F, 
  caption = "Least (Social) Cost Technology for Universal Coverage") %>% 
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  add_header_above(
    c(" "= 3, 
      "Infrastructure Sharing" = 3, 
      "Spectrum Pricing" = 2, 
      "Taxation" = 2,
      "Hybrid" = 1)) 

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(results, file = 'a_best_performing_technology.png', zoom = 1.5)

#################
#Social Cost = MNO cost + govt cost
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#technology
data_tech <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))
data_tech <- data_tech[(data_tech$confidence == 50),]

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

data_bus_mod$strategy <- as.character(data_bus_mod$strategy)

data_bus_mod$strategy_summary = sapply(strsplit(data_bus_mod$strategy, "_"), "[", 4)

data_bus_mod = data_bus_mod[!(data_bus_mod$strategy_summary == 'baseline'), ]

#policy
data_policy <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_policy_options.csv'))
data_policy <- data_policy[(data_policy$confidence == 50),]

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

results$private_cost = round(results$private_cost/1e9, 2)
results$government_cost = round(results$government_cost/1e9, 2)
results$societal_cost = round(results$societal_cost/1e9, 2)

results$GID_0 = factor(results$GID_0,
                       levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
                       labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 'Pakistan', 'Albania', 'Peru', 'Mexico'))
results$strategy_summary = factor(results$strategy_summary,
                                  levels=c('baseline', 'passive', 'active', 'shared',
                                           'spectrum_low', 'spectrum_high', 'tax_low', 'tax_high', 'mixed'),
                                  labels = c('Baseline', 'Passive', 'Active', 'SRN',
                                             'Low P.', 'High P.', 'Low T.', 'High T.', 'Mixed'))
results$scenario = factor(results$scenario, levels=c("S1_25_10_2",
                                                     "S2_200_50_5",
                                                     "S3_400_100_10"),
                          labels=c("S1 (<25 Mbps)",
                                   "S2 (<200 Mbps)",
                                   "S3 (<400 Mbps)"))
results$tech_strategy = factor(results$tech_strategy,
                               levels=c('4G_epc_microwave', '4G_epc_fiber',
                                        '5G_nsa_microwave', '5G_sa_fiber'),
                               labels=c('4G (W)', '4G (F)', '5G NSA (W)', '5G SA (F)'))

names(results)[names(results)=="GID_0"] <- "Country"
names(results)[names(results)=="scenario"] <- "Scenario"
names(results)[names(results)=="tech_strategy"] <- "Strategy"

path = file.path(folder, 'vis_results', 'c_societal_costs.csv')
write.csv(results, path, row.names=FALSE)

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
                             labels=c('Private Cost ($Bn)', 'Government Cost ($Bn)','Social Cost ($Bn)'))

results_wide = select(results_wide, Scenario, Strategy, Metric,
              Malawi, Uganda, Senegal, Kenya, Pakistan, Albania, Peru, Mexico)

cb <- function(x) {
  range <- max(abs(x))
  width <- round(abs(x / range * 50), 2)
  ifelse(
    x > 0,
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightpink; width: ',
      width, '%; margin-left: 50%; text-align: left;">', x, '</span>'
    ),
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightgreen; width: ',
      width, '%; margin-right: 50%; text-align: right; float: right; ">', x, '</span>'
    )
  )
}

table1 = results_wide %>%
  mutate(
    Malawi = cb(Malawi),
    Uganda = cb(Uganda),
    Senegal = cb(Senegal),
    Kenya = cb(Kenya),
    Pakistan = cb(Pakistan),
    Albania = cb(Albania),
    Peru = cb(Peru),
    Mexico = cb(Mexico)
  ) %>%
  kable(escape = F, caption = 'Full Technology Results by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table1, file='sup_baseline_tech_country_costs.png', zoom = 1.5)

results_wide = results_wide[(results_wide$Metric == 'Social Cost ($Bn)'),]

table1 = results_wide %>%
  mutate(
    Malawi = cb(Malawi),
    Uganda = cb(Uganda),
    Senegal = cb(Senegal),
    Kenya = cb(Kenya),
    Pakistan = cb(Pakistan),
    Albania = cb(Albania),
    Peru = cb(Peru),
    Mexico = cb(Mexico)
  ) %>%
  kable(escape = F, caption = 'Technology Results by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table1, file='b_baseline_tech_country_costs.png', zoom = 1.5)

#TABLE2
results_wide <- gather(results, Metric, value, societal_cost:government_cost)

results_wide = results_wide[(results_wide$Strategy == '5G NSA (W)'),]

results_wide = results_wide[
  (results_wide$strategy_summary == "Baseline" |
     results_wide$strategy_summary == "Passive" |
     results_wide$strategy_summary == "Active" |
     results_wide$strategy_summary == "SRN" ), ]

results_wide = results_wide %>%
  pivot_wider(names_from = Country, values_from = value)

results_wide$Strategy = NULL

names(results_wide)[names(results_wide)=="strategy_summary"] <- "Strategy"

results_wide$Metric = factor(results_wide$Metric,
                             levels=c('private_cost', 'government_cost', 'societal_cost'),
                             labels=c('Private Cost ($Bn)', 'Government Cost ($Bn)','Social Cost ($Bn)'))

results_wide = with(results_wide, results_wide[order(Scenario, Strategy),])

results_wide = select(results_wide, Scenario, Strategy, Metric,
                      Malawi, Uganda, Senegal, Kenya, Pakistan, Albania, Peru, Mexico)

table2 = results_wide %>%
  mutate(
    Malawi = cb(Malawi),
    Uganda = cb(Uganda),
    Senegal = cb(Senegal),
    Kenya = cb(Kenya),
    Pakistan = cb(Pakistan),
    Albania = cb(Albania),
    Peru = cb(Peru),
    Mexico = cb(Mexico)
  ) %>%
  kable(escape = F, caption = 'Infrastructure Sharing Results for 5G NSA (W) by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1))


folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table2, file='sup_infra_sharing_country_costs.png', zoom = 1.5)

results_wide = results_wide[(results_wide$Metric == 'Social Cost ($Bn)'),]

table2 = results_wide %>%
  mutate(
    Malawi = cb(Malawi),
    Uganda = cb(Uganda),
    Senegal = cb(Senegal),
    Kenya = cb(Kenya),
    Pakistan = cb(Pakistan),
    Albania = cb(Albania),
    Peru = cb(Peru),
    Mexico = cb(Mexico)
  ) %>%
  kable(escape = F, caption = 'Infrastructure Sharing Results for 5G NSA (W) by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table2, file='c_infra_sharing_country_costs.png', zoom = 1.5)

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
                             labels=c('Private Cost ($Bn)', 'Government Cost ($Bn)','Social Cost ($Bn)'))

results_wide$Strategy = factor(results_wide$Strategy,
                               levels=c('Low P.', 'Baseline', 'High P.'),
                               labels=c('Low Prices (-75%)', 'Baseline','High Prices (+100%)'))

results_wide = with(results_wide, results_wide[order(Scenario, Strategy),])

results_wide = select(results_wide, Scenario, Strategy, Metric,
                      Malawi, Uganda, Senegal, Kenya, Pakistan, Albania, Peru, Mexico)

table3 = results_wide %>%
  mutate(
    Malawi = cb(Malawi),
    Uganda = cb(Uganda),
    Senegal = cb(Senegal),
    Kenya = cb(Kenya),
    Pakistan = cb(Pakistan),
    Albania = cb(Albania),
    Peru = cb(Peru),
    Mexico = cb(Mexico)
  ) %>%
  kable(escape = F, caption = 'Spectrum Pricing Results for 5G NSA (W) by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table3, file='sup_spectrum_pricing_country_costs.png', zoom = 1.5)

results_S2 = results_wide[(results_wide$Scenario == 'S2 (<200 Mbps)'),]

table3 = results_S2 %>%
  mutate(
    Malawi = cb(Malawi),
    Uganda = cb(Uganda),
    Senegal = cb(Senegal),
    Kenya = cb(Kenya),
    Pakistan = cb(Pakistan),
    Albania = cb(Albania),
    Peru = cb(Peru),
    Mexico = cb(Mexico)
  ) %>%
  kable(escape = F, caption = 'Spectrum Pricing Results for 5G NSA (W) by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table3, file='d_S2_spectrum_pricing_country_costs.png', zoom = 1.5)

##################CLUSTER COSTS
#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

results <- read.csv(file.path(folder, '..', 'results', 'national_market_results_technology_options.csv'))
names(results)[names(results) == 'GID_0'] <- 'iso3'
results$metric = 'Baseline'

#mixed
mixed <- read.csv(file.path(folder, '..', 'results', 'national_market_results_mixed_options.csv'))
names(mixed)[names(mixed) == 'GID_0'] <- 'iso3'
mixed$metric = 'Lowest'

results = rbind(results, mixed)

clusters <- read.csv(file.path(folder, 'clustering', 'results', 'data_clustering_results.csv'))
names(clusters)[names(clusters) == 'ISO_3digit'] <- 'iso3'
clusters <- select(clusters, iso3, cluster, country)

results <- merge(results, clusters, x.by='iso3', y.by='iso3', all=FALSE)

results$cost_per_pop = results$total_market_cost / results$population

mean_pop_cost_by_cluster <- select(results, scenario, strategy, confidence, metric,
                                   cost_per_pop, cluster)

mean_pop_cost_by_cluster <- mean_pop_cost_by_cluster %>%
  group_by(scenario, strategy, confidence, metric, cluster) %>%
  summarise(mean_cost_per_pop = round(mean(cost_per_pop)))

results <- merge(clusters, mean_pop_cost_by_cluster, x.by='cluster', y.by='cluster', all=TRUE)

gdp <- read.csv(file.path(folder, 'gdp.csv'))
names(gdp)[names(gdp) == 'iso3'] <- 'iso3'
gdp <- select(gdp, iso3, gdp, income_group)

results <- merge(results, gdp, by='iso3', all=FALSE)

pop <- read.csv(file.path(folder, 'population_2018.csv'))
pop <- select(pop, iso3, population)
pop$iso3 <- as.character(pop$iso3)

results <- merge(results, pop, by='iso3', all=FALSE)

#Not sure if this is right
#Current costs are for a user on a network with 25% market share
#We then multiply the user cost across the whole population?
#check and revise this
results$total_market_cost <- results$mean_cost_per_pop * results$population

# results$gdp_percentage <- (results$total_market_cost / 5) / results$gdp * 100

# results$confidence = factor(results$confidence, levels=c('5','50', '95'),
#                             labels=c("lower", 'mean', "upper"))

results <- results[(results$confidence == 50),]

results$scenario = factor(results$scenario, levels=c("S1_25_10_2",
                                                     "S2_200_50_5",
                                                     "S3_400_100_10"),
                          labels=c("S1 (<25 Mbps)",
                                   "S2 (<200 Mbps)",
                                   "S3 (<400 Mbps)"))

results$strategy = factor(results$strategy, levels=c(
  "4G_epc_microwave_baseline_baseline_baseline_baseline",
  "4G_epc_fiber_baseline_baseline_baseline_baseline",
  "5G_nsa_microwave_baseline_baseline_baseline_baseline",
  "5G_sa_fiber_baseline_baseline_baseline_baseline",
  '4G_epc_microwave_shared_baseline_low_low',
  '4G_epc_fiber_shared_baseline_low_low',
  '5G_nsa_microwave_shared_baseline_low_low',
  '5G_sa_fiber_shared_baseline_low_low'
  ),
  labels=c(
    "4G (W)",
    "4G (FB)",
    "5G NSA (W)",
    "5G SA (FB)",
    "4G (W)",
    "4G (FB)",
    "5G NSA (W)",
    "5G SA (FB)"))

results <- results[complete.cases(results),]

# results <- results[(results$confidence == 'mean'),]
results$total_market_cost_dc <- round(results$total_market_cost/1e9, 2)

headline_costs <- select(results, country, scenario, strategy,
                  total_market_cost, gdp, metric)
headline_costs <- spread(headline_costs, metric, total_market_cost)

headline_costs <- headline_costs %>%
  group_by(scenario, strategy) %>%
  summarize(
    `Baseline (US$Tn)` = round(sum(Baseline)/1e12, 2),
    `Lowest (US$Tn)` = round(sum(Lowest)/1e12, 2),
    `Baseline (GDP%)` = round((sum(Baseline)/5) / sum(gdp) * 100, 2),
    `Lowest (GDP%)` = round((sum(Lowest)/5)/ sum(gdp) * 100, 2)
    )

names(headline_costs)[names(headline_costs)=="strategy"] <- "Strategy"
names(headline_costs)[names(headline_costs)=="scenario"] <- "Scenario"

cb <- function(x) {
  range <- max(abs(x))
  width <- round(abs(x / range * 20), 4)
  ifelse(
    x > 0,
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightpink; width: ',
      width, '%; margin-left: 50%; text-align: left;">', x, '</span>'
    ),
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightgreen; width: ',
      width, '%; margin-right: 50%; text-align: right; float: right; ">', x, '</span>'
    )
  )
}
headline_costs = ungroup(headline_costs)

table4 = headline_costs %>%
  mutate(
    `Baseline (US$Tn)` = cb(`Baseline (US$Tn)`),
    `Lowest (US$Tn)` = cb(`Lowest (US$Tn)`),
    `Baseline (GDP%)` = cb(`Baseline (GDP%)`),
    `Lowest (GDP%)` = cb(`Lowest (GDP%)`),
  ) %>%
  kable(escape = F, caption = 'Technology Cost Results for the Developing World') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" " = 2,
      "Total Cost" = 2,
      "5-Year GDP Share" = 2
    ))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(table4, file='e_costs_by_income_group.png', zoom = 1.5)

inc_group_costs = results[!(results$income_group == 'HIC'),]

inc_group_costs <- select(inc_group_costs, country, scenario, strategy, metric,
                          income_group, total_market_cost, gdp)

inc_group_costs = inc_group_costs %>%
  group_by(scenario, strategy, metric, income_group) %>%
  summarize(
    total_market_cost = sum(total_market_cost),
    gdp = sum(gdp)
  )

inc_group_costs = inc_group_costs %>% gather(econ_metric, value, total_market_cost, gdp)

inc_group_costs$value_dc = round(inc_group_costs$value/1e9, 2)

inc_group_costs$combined <- paste(inc_group_costs$income_group, inc_group_costs$metric, sep="_")

inc_group_costs = ungroup(inc_group_costs)

inc_group_costs <- select(inc_group_costs, scenario, strategy, combined, econ_metric, value)

inc_group_costs =  inc_group_costs %>% spread(econ_metric, value)

inc_group_costs <- inc_group_costs %>%
  group_by(scenario, strategy, combined) %>%
  summarize(
    # `(US$Bn)` = round(sum(total_market_cost)/1e9),
    `(GDP%)` = round((sum(total_market_cost)/5) / sum(gdp) * 100, 2),
  )

inc_group_costs$combined = factor(inc_group_costs$combined,
                levels=c(
                  'LIC_Baseline',
                  'LIC_Lowest',
                  'LMC_Baseline',
                  'LMC_Lowest',
                  'UMC_Baseline',
                  'UMC_Lowest'
                     ),
                labels=c(
                  'Baseline\nLIC',
                  'Lowest\nLIC',
                  'Baseline\nLMIC',
                  'Lowest\nLMIC',
                  'Baseline\nUMIC',
                  'Lowest\nUMIC'
                ))

inc_group_costs <- spread(inc_group_costs, combined, `(GDP%)`)

names(inc_group_costs)[names(inc_group_costs)=="strategy"] <- "Strategy"
names(inc_group_costs)[names(inc_group_costs)=="scenario"] <- "Scenario"
inc_group_costs = ungroup(inc_group_costs)

cb <- function(x) {
  range <- max(abs(x))
  width <- round(abs(x / range * 20), 4)
  ifelse(
    x > 0,
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightpink; width: ',
      width, '%; margin-left: 50%; text-align: left;">', x, '</span>'
    ),
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightgreen; width: ',
      width, '%; margin-right: 50%; text-align: right; float: right; ">', x, '</span>'
    )
  )
}

inc_group_costs = inc_group_costs %>%
  mutate(
    `Baseline\nLIC` = cb(`Baseline\nLIC`),
    `Lowest\nLIC` = cb(`Lowest\nLIC`),
    `Baseline\nLMIC` = cb(`Baseline\nLMIC`),
    `Lowest\nLMIC` = cb(`Lowest\nLMIC`),
    `Baseline\nUMIC` = cb(`Baseline\nUMIC`),
    `Lowest\nUMIC` = cb(`Lowest\nUMIC`)
  ) %>%
  kable(escape = F, caption = 'Technology Cost Results for the Developing World') %>%
  kable_classic("striped", html_font = "Cambria", full_width = FALSE) %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 2,
      "Low\nIncome\n(5-Year GDP%)" = 2,
      "Lower\nMiddle Income\n(5-Year GDP%)" = 2,
      "Upper\nMiddle Income\n(5-Year GDP%)" = 2
      ))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'tables')
setwd(path)
kableExtra::save_kable(inc_group_costs, file='f_costs_by_income_group.png', zoom = 1.5)
