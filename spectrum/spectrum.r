#Spectrum costs
library(tidyverse)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, 'data_inputs', 'spectrum_costs.csv'))

coverage <- data[data$type == "coverage",]

coverage$group = factor(coverage$group, levels=c("High", "Median", "Low"))

coverage <- ggplot(coverage, aes(x=year, y=dollars.mhz.pop, colour=group))  +
  geom_point(size=2) +
  scale_x_continuous(breaks= c(2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017)) +
  theme(axis.text.x = element_text(angle = 30)) +
  guides(colour=guide_legend(title="Price\nGroup")) +
  labs(title = "Spectrum Prices (Coverage)", x='Year', y='$ / MHz / Per Capita (USD)',
       subtitle = "Bands comprise 700, 800, 850, 900 MHz and include annual fees",
       shape='Group')


#export to folder
path = file.path(folder, 'figures', 'coverage.tiff')
tiff(path, units="in", width=7, height=5, res=300)
print(coverage)
dev.off()

capacity <- data[data$type == "capacity",]

capacity$group = factor(capacity$group, levels=c("Extreme outlier", "Outlier","High", "Median", "Low"))

capacity <- ggplot(capacity, aes(x=year, y=dollars.mhz.pop, colour=group))  + 
  geom_point(size=2) +
  scale_x_continuous(breaks= c(2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017)) +
  theme(axis.text.x = element_text(angle = 30)) +
  guides(colour=guide_legend(title="Price\nGroup")) +
  labs(title = "Spectrum Prices (Capacity)", x='Year', y='$ / MHz / Per Capita (USD)',
       subtitle = "Bands comprise AWS, PCS, 1800, 2100, 2600 MHz and include annual fees",
       shape='Group')

#export to folder
path = file.path(folder, 'figures', 'capacity.tiff')
tiff(path, units="in", width=7, height=5, res=300)
print(capacity)
dev.off()