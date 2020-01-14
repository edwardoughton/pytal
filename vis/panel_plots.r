###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, '..', 'results', 'results_with_density.csv'))
# data <- read.csv(file.path(folder, 'example_data.csv'))

#select desired columns
data <- select(data, country, scenario, strategy, geotype, total_cost)

data$total_cost <- round(data$total_cost / 1e6)

data <- data[!(data$total_cost == "NA"),]
       
#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
data <- aggregate( . ~ country + strategy + scenario + geotype, FUN=sum, data=data)


#set factors 
data$geotype = factor(data$geotype, levels=c("urban",
                                             "suburban 1",
                                             "suburban 2",
                                             "rural 1",
                                             "rural 2",
                                             "rural 3",
                                             "rural 4",
                                             "rural 5"
                                             ),
                                    labels=c("Urban",
                                             "Suburban 1",
                                             "Suburban 2",
                                             "Rural 1",
                                             "Rural 2",
                                             "Rural 3",
                                             "Rural 4",
                                             "Rural 5"))


data$strategy = factor(data$strategy, levels=c("scorched earth 1",
                                               "scorched earth 2",
                                               "scorched earth 3"),
                                      labels=c("Scorched earth 1",
                                               "Scorched earth 2",
                                               "Scorched earth 3"))

data <- data[order(data$country, data$scenario, data$strategy, data$geotype),]

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_sum = cumsum(total_cost))

panel <- ggplot(data, aes(x=geotype, y=cost_sum, colour=country, group=country)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Cost Per Country By Geotype",
  subtitle = "Results reported by scenario, strategy and cost type for users within each geotype",
  x = NULL, y = "Per User Cost (Euros)") +
  facet_grid(scenario~strategy) #+ scale_y_continuous(expand = c(0, 0),limits = c(0, 1700)) 

path = file.path(folder, 'figures', 'panel.png')
ggsave(path, units="in", width=10, height=10)
print(panel)
dev.off()
