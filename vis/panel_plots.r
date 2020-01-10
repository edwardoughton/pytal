###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)

#set directory for export 
data_input_directory <- "C:\\Users\\edwar\\Dropbox\\Academic Projects\\WB 5G assessment"

setwd(data_input_directory)
data <- read.csv("dutch_per_user_cost_results.csv")

data <- select(data, scenario, strategy, geotype, metric, per_user_cost)

data$geotype = factor(data$geotype, levels=c("Urban",
                                             "Suburban 1",
                                             "Suburban 2",
                                             "Rural 1",
                                             "Rural 2",
                                             "Rural 3",
                                             "Rural 4"))

data$strategy = factor(data$strategy, levels=c("Spectrum Integration",
                                                "Small Cells",
                                                "Hybrid"))

data$metric = factor(data$metric, levels=c('Macro RAN',
                                          'Macro Civil Works',
                                          'Macro Backhaul',
                                          'Small Cell RAN',
                                          'Small Cell Civil Works'),
                                 labels=c('Macro RAN',
                                          'Macro Civil Works',
                                          'Macro Backhaul',
                                          'Small Cell RAN',
                                          'Small Cell Civil Works'))

totals <- data %>%
  group_by(scenario, strategy, geotype) %>%
  summarise(total_per_user_cost = (sum(round(per_user_cost, digits=0), na.rm=TRUE))) 

cost_per_user <- ggplot(data, aes(x = geotype, y = (per_user_cost), 
  fill=metric, label=per_user_cost)) + 
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "bottom") +
  geom_bar(stat="identity") +  labs(title = "Cost Per User By Geotype",
  subtitle = "Results reported by scenario, strategy and cost type for users within each geotype",
  x = NULL, y = "Per User Cost (Euros)") +
  facet_grid(scenario~strategy) + scale_y_continuous(expand = c(0, 0),limits = c(0, 1700)) +
  geom_text(aes(geotype, total_per_user_cost + 60, label = total_per_user_cost,fill = NULL), data = totals,size=2)

### EXPORT TO FOLDER
setwd(data_input_directory)
tiff('cost_per_user.tiff', units="in", width=8, height=8, res=500)
print(cost_per_user)
dev.off()
