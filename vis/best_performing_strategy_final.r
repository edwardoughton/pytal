###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)
library(kableExtra)
library(magick)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

####################SUPPLY-DEMAND METRICS
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, '..', 'results', 'decile_mno_results_technology_options.csv'))

names(data)[names(data) == 'GID_0'] <- 'country'

#select desired columns
data <- select(data, country, scenario, strategy, confidence, decile, #population, area_km2, 
               population_km2, total_estimated_sites, existing_mno_sites,
               total_estimated_sites_km2, existing_mno_sites_km2,
               phone_density_on_network_km2, sp_density_on_network_km2,
               total_mno_revenue, total_mno_cost, cost_per_network_user, 
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
                 phone_density_on_network_km2, 
                 sp_density_on_network_km2)

demand <- gather(demand, metric, value, population_km2:sp_density_on_network_km2)

demand$metric = factor(demand$metric, 
                       levels=c("population_km2",
                                "phone_density_on_network_km2",
                                "sp_density_on_network_km2"),
                       labels=c("Population Density",
                                "Modeled Network Phone Density",
                                "Modeled Network Smartphone Density"))

demand_densities <- ggplot(demand, aes(x=decile, y=value, colour=metric, group=metric)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme( legend.position = "bottom", axis.text.x = element_text(angle = 45, hjust = 1)) + 
  labs(colour=NULL,
       title = "Demand-Side Density Metrics by Population Decile",
       # subtitle = "Population and user densities",
       x = "Population Decile", y = "Density (per km^2)") + 
  scale_x_continuous(expand = c(0, 0.5), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(~country, scales = "free", ncol=4) 

supply = data[(
  data$scenario == 'S1_25_10_2' &
    data$strategy == '4G_epc_fiber_baseline_baseline_baseline_baseline'
),]

supply <- select(supply, country, decile, total_estimated_sites_km2, existing_mno_sites_km2)

supply <- gather(supply, metric, value, total_estimated_sites_km2:existing_mno_sites_km2)

supply$metric = factor(supply$metric, 
                       levels=c("total_estimated_sites_km2",
                                "existing_mno_sites_km2"),
                       labels=c("Total Site Density",
                                "Modeled Network Site Density"))

supply_densities <- ggplot(supply, aes(x=decile, y=value, colour=metric, group=metric)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme( legend.position = "bottom", axis.text.x = element_text(angle = 45, hjust = 1)) + 
  labs(colour=NULL,
       title = "Supply-Side Density Metrics by Population Decile",
       x = "Population decile", y = "Density (per km^2)") + 
  scale_x_continuous(expand = c(0, 0.5), breaks = seq(0,100,20)) + 
  scale_y_continuous(expand = c(0, 0)) + #, limits = c(0,20)) +  
  theme(panel.spacing = unit(0.6, "lines")) + expand_limits(y=0) +
  guides(colour=guide_legend(ncol=3)) +
  facet_wrap(~country, scales = "free", ncol=4) 

demand_supply <- ggarrange(demand_densities, supply_densities, 
                           ncol = 1, nrow = 2, align = c("hv"))

#export to folder
path = file.path(folder, 'figures_tables', 'a_demand_supply_panel.png')
ggsave(path,  units="in", width=8, height=9, dpi=300)
print(demand_supply)
dev.off()

################################
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

srn <- data_bus_mod %>%
  filter(str_detect(strategy, "_srn_baseline_baseline_baseline")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
srn$strategy_summary = 'srn'

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
  filter(str_detect(strategy, "_srn_baseline_low_low")) %>% 
  group_by(GID_0, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
mixed$strategy_summary = 'mixed'

####################
#Aggregate results
results = rbind(baseline, passive, active, srn, 
                spectrum_low, spectrum_high,
                tax_low, tax_high, mixed)

results$tech = sapply(strsplit(results$strategy, "_"), "[", 1)
results$backhaul = sapply(strsplit(results$strategy, "_"), "[", 3)

rm(data_tech, data_bus_mod, data_policy, baseline, passive, active, srn, 
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
  mutate(srn = cell_spec(srn, "html", 
     color=ifelse(grepl("4G (W)", srn, fixed = T), "blue", "black"))) %>%
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

results = select(results, Country, Scenario, baseline, passive, active, srn, 
                 spectrum_low, spectrum_high, tax_low, tax_high, mixed)

names(results)[names(results)=="baseline"] <- "Baseline"
names(results)[names(results)=="passive"] <- "Passive"
names(results)[names(results)=="active"] <- "Active"
names(results)[names(results)=="srn"] <- "SRN"
names(results)[names(results)=="spectrum_low"] <- "Low P."
names(results)[names(results)=="spectrum_high"] <- "High P."
names(results)[names(results)=="tax_low"] <- "Low T."
names(results)[names(results)=="tax_high"] <- "High T."
names(results)[names(results)=="mixed"] <- "Lowest"

results = kable(results, "html", escape = F, 
  caption = "Least (Financial) Cost Technology for Universal Coverage") %>% 
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  add_header_above(
    c(" "= 3, 
      "Infrastructure Sharing" = 3, 
      "Spectrum Pricing" = 2, 
      "Taxation" = 2,
      "Hybrid" = 1)) 

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(results, file = 'b_best_performing_technology.png', zoom = 1.5)

#################
#Financial Cost = MNO cost + govt cost
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

results$private_cost = signif(results$private_cost/1e9, 2)
results$government_cost = signif(results$government_cost/1e9, 2)
results$societal_cost = signif(results$societal_cost/1e9, 2)

results$GID_0 = factor(results$GID_0,
                       levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
                       labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 'Pakistan', 'Albania', 'Peru', 'Mexico'))
results$strategy_summary = factor(results$strategy_summary,
                                  levels=c('baseline', 'passive', 'active', 'srn',
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

path = file.path(folder, 'vis_results', 'societal_costs.csv')
write.csv(results, path, row.names=FALSE)

#######################################
results_wide <- gather(results, Metric, value, societal_cost:government_cost)

results_wide = results_wide %>%
  pivot_wider(names_from = strategy_summary, values_from = value)

results_wide = select(results_wide, Country, Scenario, Strategy, Metric, Baseline)

results_wide = results_wide %>%
  pivot_wider(names_from = Country, values_from = Baseline)

results_wide = with(results_wide, results_wide[order(Scenario, Strategy, Metric),])

results_wide$Metric = factor(results_wide$Metric,
       levels=c('private_cost', 'government_cost', 'societal_cost'),
       labels=c('Private Cost ($Bn)', 'Government Cost ($Bn)','Financial Cost ($Bn)'))

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
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Infrastructure Sharing Strategy: Baseline.",
                      "Spectrum Pricing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 2 s.f."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table1, file='sup_baseline_tech_country_costs.png', zoom = 1.5)

######################################
path = file.path(folder, 'vis_results', 'sup_baseline_tech_country_costs.csv')
write.csv(results_wide, path, row.names=FALSE)

results_wide = results_wide[(results_wide$Metric == 'Financial Cost ($Bn)'),]

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
  kable(escape = F, 
  caption = 'Technology Results reported by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Infrastructure Sharing Strategy: Baseline.",
                      "Spectrum Pricing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 2 s.f."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table1, file='c_baseline_tech_country_costs.png', zoom = 1.5)

#######################################
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
                             labels=c('Private Cost ($Bn)', 'Government Cost ($Bn)','Financial Cost ($Bn)'))

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
  kable(escape = F, caption = 'Infrastructure Sharing Results by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Technology Strategy: 5G NSA with Wireless Backhaul.",
                      "Spectrum Pricing Strategy: Baseline.",
                      "Taxation Strategy: Baseline."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table2, file='sup_infra_sharing_country_costs.png', zoom = 1.5)

path = file.path(folder, 'vis_results', 'sup_infra_sharing_country_costs.csv')
write.csv(results_wide, path, row.names=FALSE)

#######################################
results_wide = results_wide[(results_wide$Metric == 'Financial Cost ($Bn)'),]

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
  kable(escape = F, caption = 'Infrastructure Sharing Results by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Technology Strategy: 5G NSA with Wireless Backhaul.",
                      "Spectrum Pricing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 2 s.f."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table2, file='d_infra_sharing_country_costs.png', zoom = 1.5)

###############################
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
                             labels=c('Private Cost ($Bn)', 'Government Cost ($Bn)','Financial Cost ($Bn)'))

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
  kable(escape = F, caption = 'Spectrum Pricing Results by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 3, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Technology Strategy: 5G NSA with Wireless Backhaul.",
                      "Infrastructure Sharing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 2 s.f."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table3, file='sup_spectrum_pricing_country_costs.png', zoom = 1.5)

path = file.path(folder, 'vis_results', 'sup_spectrum_pricing_country_costs.csv')
write.csv(results_wide, path, row.names=FALSE)

###############################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
results_S2 = read.csv(file.path(folder, 'spectrum_ratio.csv'))
results_S2$Scenario = NULL
specify_decimal <- function(x, k) trimws(format(round(x, k), nsmall=k))

results_S2$Pakistan = specify_decimal(results_S2$Pakistan, 1)
results_S2$Albania = specify_decimal(results_S2$Albania, 1)
results_S2$Peru = specify_decimal(results_S2$Peru, 1)
results_S2$Mexico = specify_decimal(results_S2$Mexico, 1)

results_S2$Pakistan = as.numeric(results_S2$Pakistan)
results_S2$Albania = as.numeric(results_S2$Albania)
results_S2$Peru = as.numeric(results_S2$Peru)
results_S2$Mexico = as.numeric(results_S2$Mexico)

table4 = results_S2 %>%
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
  kable(escape = F, caption = 'Spectrum Pricing Results by Country', digits=1) %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  row_spec(which(results_S2$Malawi >6), bold = T, color = "black", background = "lightgrey") %>%
  add_header_above(
    c(" "= 2, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Scenario: S2 (<200 Mbps).",
                      "Technology Strategy: 5G NSA with Wireless Backhaul.",
                      "Infrastructure Sharing Strategy: Baseline.",
                      "Taxation Strategy: Baseline."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table4, file='d_S2_spectrum_costs_ratio.png', zoom = 1.5)






###################NATIONAL COST PROFILE FOR BASELINE

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_technology_options.csv'))

data <- data[(data$strategy == "5G_nsa_microwave_baseline_baseline_baseline_baseline"),]
# data <- data[(data$scenario == "S2_200_50_5"),]
data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, scenario, strategy, country, total_ran:total_market_cost)

data = data %>%
  group_by(scenario, strategy, country) %>%
  mutate(
    perc_ran = total_ran / total_market_cost * 100,
    perc_backhaul = total_backhaul_fronthaul / total_market_cost * 100,
    perc_civils = total_civils / total_market_cost * 100,
    perc_core_network = total_core_network / total_market_cost * 100,
    perc_administration = total_administration / total_market_cost * 100,
    perc_spectrum_cost = total_spectrum_cost / total_market_cost * 100,
    perc_tax = total_tax / total_market_cost * 100,
    perc_profit_margin = total_profit_margin / total_market_cost * 100,
  ) %>%
  select(scenario, strategy, country, perc_ran, perc_backhaul, perc_civils, 
         perc_core_network, perc_administration, perc_spectrum_cost,
        perc_tax, perc_profit_margin)

data <- gather(data, metric, value, perc_ran:perc_profit_margin)#ran:profit_margin)#

data$metric = factor(data$metric, levels=c(
  'perc_profit_margin',
  'perc_tax',
  'perc_spectrum_cost',
  'perc_administration',
  'perc_core_network',
  'perc_civils',
  'perc_backhaul',
  'perc_ran'
),
labels=c(
  "Profit",
  "Tax",
  "Spectrum",
  "Administration",
  'Core',
  "Civils",
  "Backhaul",
  "RAN"
))

data$scenario = factor(data$scenario, levels=c("S1_25_10_2",
                                                     "S2_200_50_5",
                                                     "S3_400_100_10"),
                          labels=c("S1 (<25 Mbps)",
                                   "S2 (<200 Mbps)",
                                   "S3 (<400 Mbps)"))

data$country = factor(data$country, levels=c(
  'MEX','PER','ALB','PAK','KEN','SEN','UGA','MWI'
),
labels=c(
  'Mexico','Peru', 'Albania', 'Pakistan', 'Kenya', 'Senegal', 'Uganda','Malawi' 
))

table5 <- ggplot(data, aes(x=country, y=(value), group=metric, fill=metric)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  scale_fill_brewer(palette="Spectral", name = NULL, direction=1) +
  theme(legend.position = "bottom", axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Private Cost Composition for 5G NSA (W) by Country", colour=NULL,
       subtitle = "Baseline Infrastructure Sharing, Spectrum Pricing and Taxation",
       x = NULL, y = "Percentage of Total Private Cost (%)") +
  scale_y_continuous(expand = c(0, 0)) +  
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=8, reverse = TRUE)) +
  facet_wrap(~scenario, scales = "free", ncol=3)

path = file.path(folder, 'figures_tables', 'e_percentage_of_total_private_cost.png')
ggsave(path, units="in", width=7, height=4, dpi=300)
print(table5)
dev.off()

###################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'national_market_cost_results_all_options.csv'))

data <- data[(data$confidence == 50),]

names(data)[names(data) == 'GID_0'] <- 'country'

data <- select(data, scenario, strategy, country, societal_cost)

baseline <- data %>%
  filter(str_detect(strategy, "5G_nsa_microwave")) %>% 
  group_by(country, scenario) %>% 
  filter(str_detect(strategy, "baseline_baseline_baseline_baseline")) 
baseline$type = 'Baseline ($Bn)'

data <- data %>%
  filter(str_detect(strategy, "5G_nsa_microwave")) %>% 
  group_by(country, scenario) %>%
  filter(societal_cost == min(societal_cost)) 
data$type = 'Lowest ($Bn)'

all_data = rbind(data, baseline)

all_data$country = factor(all_data$country,
 levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
 labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 
          'Pakistan', 'Albania', 'Peru', 'Mexico'))

all_data$strategy = NULL

all_data = all_data[!duplicated(all_data[c('scenario', 'country', 'type')]),]

all_data$scenario = factor(all_data$scenario, levels=c("S1_25_10_2",
                                                       "S2_200_50_5",
                                                       "S3_400_100_10"),
                           labels=c("S1 (<25 Mbps)",
                                    "S2 (<200 Mbps)",
                                    "S3 (<400 Mbps)"))

all_data$societal_cost = round(all_data$societal_cost / 1e9, 1)

names(all_data)[names(all_data) == 'scenario'] <- 'Scenario'
names(all_data)[names(all_data) == 'type'] <- 'Strategy'

all_data <- spread(all_data, country, societal_cost)

table6 = all_data %>%
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
  kable(escape = F, caption = '(A) Financial Cost of Universal Access NPV 2020-2030 by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 2, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Technology Strategy: 5G NSA with Wireless Backhaul.",
                      "Infrastructure Sharing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 1 d.p."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table6, file='f_a_social_cost.png', zoom = 1.5)


###################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data_revenue <- read.csv(file.path(folder, '..', 'results', 'national_mno_results_all_options.csv'))
data_revenue <- data_revenue[(data_revenue$confidence == 50),]
data_revenue <- select(data_revenue, GID_0, scenario, strategy, total_mno_revenue)

data <- read.csv(file.path(folder, '..', 'results', 'decile_mno_cost_results_all_options.csv'))
data <- data[(data$confidence == 50),]
data <- data %>% filter(str_detect(strategy, "5G_nsa_microwave")) 

data <- select(data, GID_0, scenario, strategy, decile, total_mno_cost, required_state_subsidy)

data <- merge(data, data_revenue, by=c('GID_0', 'strategy', 'scenario'))

data <- data[order(data$GID_0, data$scenario, data$strategy, data$decile),]

#get baseline rows
baseline <- data %>% filter(str_detect(strategy, "baseline_baseline_baseline_baseline")) 

baseline <- baseline %>%
  group_by(GID_0, scenario) %>%
  mutate(
    total_mno_revenue = total_mno_revenue/1e9,
    cumulative_cost_bn = cumsum(round(total_mno_cost / 1e9, 3)),
    cumulative_subsidy_bn = cumsum(round(required_state_subsidy / 1e9, 2))
    )
baseline$type = 'Baseline (%)'

problems <- baseline %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_mno_revenue <= cumulative_cost_bn) %>%
  filter(decile == min(decile)) 

baseline <- baseline %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_mno_revenue >= cumulative_cost_bn)

#get baseline rows
lowest <- filter(data, !strategy %in% "5G_nsa_microwave_baseline_baseline_baseline_baseline") 

lowest <- lowest[order(lowest$GID_0, lowest$scenario, lowest$strategy, lowest$decile),]

lowest <- lowest %>%
  group_by(GID_0, strategy, scenario) %>%
  mutate(
    total_mno_revenue = total_mno_revenue/1e9,
    cumulative_cost_bn = cumsum(round(total_mno_cost / 1e9, 3)),
    cumulative_subsidy_bn = cumsum(round(required_state_subsidy / 1e9, 2))
    )
lowest$type = 'Lowest (%)'

lowest <- lowest %>%
  group_by(GID_0, strategy, scenario) %>%
  filter(total_mno_revenue >= cumulative_cost_bn)

all_data = rbind(lowest, baseline)

subsidy_all = all_data
subsidy_all = rbind(subsidy_all, problems)

all_data <- all_data %>%
  group_by(GID_0, scenario, type) %>%
  filter(decile == max(decile)) 

all_data = rbind(all_data, problems)

all_data$GID_0 = factor(all_data$GID_0,
                        levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
                        labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 
                                 'Pakistan', 'Albania', 'Peru', 'Mexico'))

all_data = select(all_data, scenario, GID_0, decile, type)

all_data = all_data[!duplicated(all_data[c('scenario', 'GID_0', 'type')]),]

all_data$scenario = factor(all_data$scenario, levels=c("S1_25_10_2",
                                                       "S2_200_50_5",
                                                       "S3_400_100_10"),
                           labels=c("S1 (<25 Mbps)",
                                    "S2 (<200 Mbps)",
                                    "S3 (<400 Mbps)"))

names(all_data)[names(all_data) == 'scenario'] <- 'Scenario'
names(all_data)[names(all_data) == 'type'] <- 'Strategy'

all_data <- spread(all_data, GID_0, decile)

all_data[is.na(all_data)] <- 0

cb_inverted <- function(x) {
  range <- max(abs(x))
  width <- round(abs(range / x * 5), 2)
  ifelse(
    x < 100,
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightpink; width: ',
      width, '%; margin-right: 50%; text-align: right; float: right; ">', x, '</span>'
    ),
    paste0(
      '<span style="display: inline-block; border-radius: 2px; ',
      'padding-right: 2px; background-color: lightgreen; width: ',
      width, '%; margin-left: 50%; text-align: left;">', x, '</span>'
    )

  )
}

table7 = all_data %>%
  mutate(
    Malawi = cb_inverted(Malawi),
    Uganda = cb_inverted(Uganda),
    Senegal = cb_inverted(Senegal),
    Kenya = cb_inverted(Kenya),
    Pakistan = cb_inverted(Pakistan),
    Albania = cb_inverted(Albania),
    Peru = cb_inverted(Peru),
    Mexico = cb_inverted(Mexico)
  ) %>%
  kable(escape = F, caption = '(B) Commercially Viable Population Coverage by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 2, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Technology Strategy: 5G NSA with Wireless Backhaul.",
                      "Infrastructure Sharing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 1 d.p."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table7, file='f_b_viable_coverage.png', zoom = 1.5)

#########################################
subsidy = ungroup(subsidy_all)

subsidy <- subsidy %>%
  group_by(GID_0, scenario, type) %>%
  filter(decile == max(decile)) 

subsidy = select(subsidy, scenario, strategy, GID_0, cumulative_subsidy_bn, type)

subsidy$strategy = NULL

subsidy = subsidy[!duplicated(subsidy[c('scenario', 'GID_0', 'type')]),]

subsidy$scenario = factor(subsidy$scenario, levels=c("S1_25_10_2",
                                                       "S2_200_50_5",
                                                       "S3_400_100_10"),
                           labels=c("S1 (<25 Mbps)",
                                    "S2 (<200 Mbps)",
                                    "S3 (<400 Mbps)"))

subsidy$GID_0 = factor(subsidy$GID_0,
                        levels=c('MWI', 'UGA', 'SEN', 'KEN', 'PAK', 'ALB', 'PER', 'MEX'),
                        labels=c('Malawi', 'Uganda', 'Senegal', 'Kenya', 
                                 'Pakistan', 'Albania', 'Peru', 'Mexico'))

names(subsidy)[names(subsidy) == 'scenario'] <- 'Scenario'
names(subsidy)[names(subsidy) == 'type'] <- 'Strategy'

subsidy$Strategy[subsidy$Strategy == 'Baseline (%)'] <- "Baseline ($Bn)"
subsidy$Strategy[subsidy$Strategy == 'Lowest (%)'] <- 'Lowest ($Bn)'

# subsidy$required_state_subsidy = round(subsidy$required_state_subsidy / 1e9, 3)

subsidy <- spread(subsidy, GID_0, cumulative_subsidy_bn)

table8 = subsidy %>%
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
  kable(escape = F, 
        caption = '(C) Government Subsidy to Reach Universal Access NPV 2020-2030 by Country') %>%
  kable_classic("striped", full_width = F, html_font = "Cambria") %>%
  row_spec(0, align = "c") %>%
  add_header_above(
    c(" "= 2, "C1" = 2, "C2" = 2, "C3" = 1, "C4" = 1, "C5" = 1, "C6" = 1)) %>%
  footnote(number = c("Technology Strategy: 5G NSA with Wireless Backhaul.",
                      "Infrastructure Sharing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 1 d.p."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table8, file='f_c_subsidy.png', zoom = 1.5)


















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

results$total_market_cost <- results$mean_cost_per_pop * results$population

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
  '4G_epc_microwave_srn_baseline_low_low',
  '4G_epc_fiber_srn_baseline_low_low',
  '5G_nsa_microwave_srn_baseline_low_low',
  '5G_sa_fiber_srn_baseline_low_low'
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
    `Baseline (US$Tn)` = signif(sum(Baseline)/1e12, 2),
    `Lowest (US$Tn)` = signif(sum(Lowest)/1e12, 2),
    `Baseline (GDP%)` = signif((sum(Baseline)/10) / sum(gdp) * 100, 2),
    `Lowest (GDP%)` = signif((sum(Lowest)/10)/ sum(gdp) * 100, 2)
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
      "10-Year GDP Share" = 2
    )) %>%
  footnote(number = c("Infrastructure Sharing Strategy: Baseline.",
                      "Spectrum Pricing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 2 s.f."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table4, file='g_costs_by_income_group.png', zoom = 1.5)

















path = file.path(folder, 'vis_results', 'headline_costs.csv')
write.csv(headline_costs, path, row.names=FALSE)

inc_group_costs = results[!(results$income_group == 'HIC'),]

inc_group_costs <- select(inc_group_costs, country, scenario, strategy, metric,
                          income_group, total_market_cost, gdp, population)

inc_group_costs = inc_group_costs %>%
  group_by(scenario, strategy, metric, income_group) %>%
  summarize(
    population = sum(population),
    total_market_cost = sum(total_market_cost),
    gdp = sum(gdp)
  )

inc_group_costs = inc_group_costs %>% 
                  gather(econ_metric, value, total_market_cost, gdp)

inc_group_costs$value_dc = round(inc_group_costs$value/1e9, 2)

inc_group_costs$combined <- paste(inc_group_costs$income_group, inc_group_costs$metric, sep="_")

inc_group_costs = ungroup(inc_group_costs)

inc_group_costs <- select(inc_group_costs, scenario, strategy, 
                          combined, econ_metric, value, population)

inc_group_costs =  inc_group_costs %>% spread(econ_metric, value)

# path = file.path(folder, 'vis_results', 'test.csv')
# write.csv(inc_group_costs, path, row.names=FALSE)

inc_group_costs <- inc_group_costs %>%
  group_by(scenario, strategy, combined) %>%
  summarize(
    `population` = sum(population),
    `total_cost $USDbn` = (sum(total_market_cost)/1e9),
    `(GDP$Bn)` = round(sum(gdp)/1e9),
    `(GDP%)` = signif((sum(total_market_cost)/10) / sum(gdp) * 100, 2),
  )

# path = file.path(folder, 'vis_results', 'test2.csv')
# write.csv(inc_group_costs, path, row.names=FALSE)

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

inc_group_costs <- select(inc_group_costs, scenario, strategy, combined, `(GDP%)`)

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

table5 = inc_group_costs %>%
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
      "Low\nIncome\n(10-Year GDP%)" = 2,
      "Lower\nMiddle Income\n(10-Year GDP%)" = 2,
      "Upper\nMiddle Income\n(10-Year GDP%)" = 2
      )) %>%
  footnote(number = c("Infrastructure Sharing Strategy: Baseline.",
                      "Spectrum Pricing Strategy: Baseline.",
                      "Taxation Strategy: Baseline.",
                      "Results rounded to 2 s.f."))

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures_tables')
setwd(path)
kableExtra::save_kable(table5, file='h_costs_by_income_group.png', zoom = 1.5)

path = file.path(folder, 'vis_results', 'costs_by_income_group.csv')
write.csv(inc_group_costs, path, row.names=FALSE)