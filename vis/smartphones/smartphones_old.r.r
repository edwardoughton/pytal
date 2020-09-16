#Spectrum costs
library(tidyverse)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, 'data_inputs', 'data_input.csv'))

data$Settlement = factor(data$Settlement, levels=c("Urban",  "Rural")) 

data$Type = factor(data$Type, levels=c("Smartphone", "Feature", "Basic")) 

plot <- ggplot(data=data, aes(x=Country, y=Value, fill=Type)) +
  geom_bar(stat="identity") + facet_grid(rows = vars(Settlement)) +
  theme(legend.position="bottom", axis.text.x = element_text(angle = 45, hjust = 1)) + 
  labs(x=NULL, y=c('Percentage Composition (%)'), 
       title='Cell Phone Types by Urban-Rural',
       subtitle='Source: World Bank reported survey statistics') +
  guides(fill = guide_legend(reverse=T)) + 
  scale_y_continuous(expand = c(0, 0.5), limits = c(0,101))

path = file.path(folder, 'figures', 'panel.png')
ggsave(path, units="in", width=5, height=5)
print(plot)
dev.off()
