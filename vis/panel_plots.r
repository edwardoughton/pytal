###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#load data
data <- read.csv(file.path(folder, 'example_data.csv'))

#select desired columns
data <- select(data, country, scenario, strategy, geotype, cost)

#assuming the data is at the subregional level, aggregate by scenario, strategy etc..
#cumulative_cost_data <- aggregate( . ~ Strategy + Scenario + geotype, FUN=sum, data=cumulative_cost_data)   

#set factors 
data$geotype = factor(data$geotype, levels=c("Urban",
                                             "Suburban 1",
                                             "Suburban 2",
                                             "Rural 1",
                                             "Rural 2",
                                             "Rural 3",
                                             "Rural 4"
                                             ))
data$strategy = factor(data$strategy, levels=c("Spectrum Integration",
                                                "Small Cells",
                                                "Hybrid"))

data <- data %>%
  group_by(country, scenario, strategy) %>%
  mutate(cost_cum = cumsum(cost))


panel <- ggplot(data, aes(x=geotype, y=cost_cum, colour=country, group=country)) + 
  geom_line() +
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  labs(title = "Cumulative Cost Per Country By Geotype",
  subtitle = "Results reported by scenario, strategy and cost type for users within each geotype",
  x = NULL, y = "Per User Cost (Euros)") +
  facet_grid(scenario~strategy) + scale_y_continuous(expand = c(0, 0),limits = c(0, 1700)) 

path = file.path(folder, 'figures', 'panel.png')
ggsave(path, units="in", width=10, height=10)
print(panel)
dev.off()
