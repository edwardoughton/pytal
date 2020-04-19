#Spectrum costs
library(tidyverse)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, 'data_inputs', 'data_input.csv'))

data$Technology = factor(data$Technology, levels=c("Satellite",  "Microwave",  "Copper", "Fiber")) 

plot <- ggplot(data=data, aes(x=Region, y=Value, fill=Technology)) +
  geom_bar(stat="identity") + facet_grid(rows = vars(Year)) +
  theme(legend.position="bottom", axis.text.x = element_text(angle = 45, hjust = 1)) + 
  labs(x=NULL, y=c('Percentage Composition (%)'), 
       title='Composition of Macro Cell Backhaul Technology',
       subtitle='Industry reported statistics broken down by region and year') +
  guides(fill = guide_legend(reverse=T)) + 
  scale_y_continuous(expand = c(0, 1.5), limits = c(0,100))

path = file.path(folder, 'figures', 'panel.png')
ggsave(path, units="in", width=5, height=5)
print(plot)
dev.off()
