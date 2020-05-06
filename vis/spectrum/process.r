library(tidyverse)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, 'data_inputs', 'whole_database_raw.csv'))

names(data)[names(data) == 'Country'] <- 'country'

data <- data[(data$year > 2005),]

data <- select(data, year, country, Price.Paid..USDm., Term..Years., Band.Paired, Band.Unpaired, Block.Paired, Block.Unpaired)
data <- select(data, year, country, Price.Paid..USDm., Term..Years., Band.Paired, Block.Paired)

iso3 <- read.csv(file.path(folder, 'data_inputs', 'global_information.csv'))

iso3 <- select(iso3, country, ISO_3digit)

data$country <- as.character(data$country)
data$country[data$country == 'Niger'] <- 'Niger (the)'
data$country[data$country == 'Moldova'] <- 'Moldova (the Republic of)'
data$country[data$country == 'United States'] <- 'United States of America (the)'
data$country[data$country == 'Philippines'] <- 'Philippines (the)'
data$country[data$country == 'Taiwan'] <- 'Taiwan (Province of China)'
data$country[data$country == 'South Korea'] <- 'Korea (the Republic of)'
data$country[data$country == 'Czech Republic'] <- 'Czechia'
data$country[data$country == 'Congo, Rep.'] <- 'Congo (the)'
data$country[data$country == 'Congo, Dem. Rep.'] <- 'Congo (the Democratic Republic of the)'
data$country[data$country == 'Russia'] <- 'Russian Federation (the)'

# non_matching <- anti_join(data, iso3, x.by='country', y.by='country')
# non_matching <- non_matching[complete.cases(non_matching), ]

data <- merge(data, iso3, x.by='country', y.by='country', all=FALSE)

data <- data[(data$Block.Paired == '2x5' |
                data$Block.Paired == '2x10'|
                data$Block.Paired == '2x15'|
                data$Block.Paired == '2x20'|
                data$Block.Paired == '2x25'|
                data$Block.Paired == '2x30'|
                data$Block.Paired == '1x100'|
                data$Block.Paired == '1x50'|
                data$Block.Paired == '1x60'|
                data$Block.Paired == '1x90'|
                data$Block.Paired == '2x0.6'|
                data$Block.Paired == '2x0.8'|               
                data$Block.Paired == '2x1'|            
                data$Block.Paired == '2x1.2'|              
                data$Block.Paired == '2x1.8'|  
                data$Block.Paired == '2x12.5'|  
                data$Block.Paired == '2x14'|  
                data$Block.Paired == '2x15'|  
                
                data$Block.Paired == '10'  |
                data$Block.Paired == '20'  |
                data$Block.Paired == '30'
),]

names(data)[names(data) == 'Block.Paired'] <- 'bandwidth'

data$bandwidth <- as.character(data$bandwidth)
data$bandwidth[data$bandwidth == '10'] <- 10
data$bandwidth[data$bandwidth == '20'] <- 20
data$bandwidth[data$bandwidth == '30'] <- 30
data$bandwidth[data$bandwidth == '1x100'] <- 100
data$bandwidth[data$bandwidth == '1x60'] <- 60
data$bandwidth[data$bandwidth == '1x90'] <- 90
data$bandwidth[data$bandwidth == '2x5'] <- 10
data$bandwidth[data$bandwidth == '2x10'] <- 20
data$bandwidth[data$bandwidth == '2x15'] <- 30
data$bandwidth[data$bandwidth == '2x20'] <- 40
data$bandwidth[data$bandwidth == '2x25'] <- 50
data$bandwidth[data$bandwidth == '2x30'] <- 60

data$bandwidth[data$bandwidth == '2x0.6'] <- 0.6
data$bandwidth[data$bandwidth == '2x0.8'] <- 0.8
data$bandwidth[data$bandwidth == '2x1'] <- 2
data$bandwidth[data$bandwidth == '2x1.2'] <- 2.4
data$bandwidth[data$bandwidth == '2x1.2'] <- 3.6
data$bandwidth[data$bandwidth == '2x12.5'] <- 25
data$bandwidth[data$bandwidth == '2x14'] <- 28
data$bandwidth[data$bandwidth == '2x15'] <- 30

data$bandwidth[data$bandwidth == '2x30'] <- 60
data$bandwidth[data$bandwidth == '2x30'] <- 60
data$bandwidth[data$bandwidth == '2x30'] <- 60
data$bandwidth[data$bandwidth == '2x30'] <- 60

data$bandwidth <- as.numeric(data$bandwidth)

data$price <- as.numeric(as.character(data$Price.Paid..USDm.))
data$price <- data$price * 1e6

data$dollar_per_mhz <- data$price / data$bandwidth

names(data)[names(data) == 'Term..Years.'] <- 'length'
data$length <- as.numeric(as.character(data$length))
data$dollar_per_mhz_per_single_year <- data$dollar_per_mhz / data$length 

data <- data[complete.cases(data),]

clusters <- read.csv(file.path(folder, 'data_inputs', 'data_clustering_results.csv'))
clusters <- select(clusters, ISO_3digit, cluster)
data <- merge(data, clusters, x.by='country', y.by='ISO_3digit', all=FALSE)

pop <- read.csv(file.path(folder, 'data_inputs', 'population_2018.csv'))
pop <- select(pop, iso3, population)
pop$iso3 <- as.character(pop$iso3)

data$ISO_3digit <- as.character(data$ISO_3digit)
names(data)[names(data) == 'ISO_3digit'] <- 'iso3'
data <- merge(data, pop, x.by='iso3', y.by='iso3', all=FALSE)

data$dollar_per_mhz_per_pop_per_single_year <- data$dollar_per_mhz_per_single_year / data$population
data$Band.Paired <- as.numeric(as.character(data$Band.Paired))
data$metric[data$Band.Paired <= 1000]  <- 'Coverage Spectrum'
data$metric[data$Band.Paired > 1000]  <- 'Capacity Spectrum'
data <- data[complete.cases(data),]
data$metric = factor(data$metric, levels=c("Coverage Spectrum", "Capacity Spectrum"))

data <- data[!(data$cluster == 'High Income'),]

names(data)[names(data) == 'cluster'] <- 'Cluster'

spectrum_prices <- ggplot(data, aes(Cluster, dollar_per_mhz_per_pop_per_single_year, colour=Cluster)) + 
  geom_boxplot(aes(group=factor(Cluster))) +
  geom_jitter(size=1.7) + 
  theme(legend.position = "bottom") +
  #green, light_blue, organge, yellow, dark blue, dark organge
  # scale_colour_manual(values = c("#009E73", "#56B4E9", "#E69F00", "#F0E442", "#0072B2", "#D55E00")) + 
  scale_colour_manual(values = c("#F0E442","#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73")) + 
  expand_limits(x = 0, y = 0) + 
  guides(colour=guide_legend(ncol=7)) +
  scale_y_continuous(limits=c(0, 0.12)) +
  labs(title = "Spectrum Prices by Cluster", x='Cluster Number', y='$USD/MHz/Population',
       subtitle = "Coverage Spectrum <= 1 GHz, Capacity Spectrum > 1GHz") +
  facet_wrap(~metric)


path = file.path(folder, 'figures', 'spectrum_prices_by_cluster.png')
ggsave(path, units="in", width=6, height=5, dpi=300)
print(spectrum_prices)
dev.off()

write.csv(data, file.path(folder, 'results', 'spectrum_costs.csv'))

prices <- data %>%
  group_by(Cluster, metric) %>%
  summarise(round(median(dollar_per_mhz_per_pop_per_single_year), 4))
