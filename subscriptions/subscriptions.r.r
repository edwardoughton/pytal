#Spectrum costs
library(tidyverse)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, 'data_inputs', 'data_input.csv'))

panel <- ggplot(data, aes(x=year, y=penetration, colour=country, group=country)) + 
  geom_point() +   geom_line() +
  geom_vline(xintercept=2017, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2017, y = 13, label = "Historical", vjust=-1, angle = 90) +
  annotate("text", x = 2018.2, y = 13, label = "Forecast", vjust=-1, angle = 90) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "bottom") +
  labs(title = "Mobile Cellular Subscriptions", colour='Country',
       subtitle = "Historical: 2007-2017. Forecast: 2018-2030 ",
       x = NULL, y = "Cell Phone Penetration (Per 100 Inhabitants)") + 
  scale_x_continuous(expand = c(0, 0), limits = c(2005,2030), breaks = seq(2005,2030,1)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0,200)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=6)) 
 
path = file.path(folder, 'figures', 'panel.png')
ggsave(path, units="in", width=7, height=7)
print(panel)
dev.off()
