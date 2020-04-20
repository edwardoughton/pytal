#Spectrum costs
library(tidyverse)
require("ggrepel")
library(ggpubr)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, 'data_inputs', 'spectrum_costs.csv'))

data$income = factor(data$income, levels=c("High", "Upper Middle", "Lower Middle", "Unknown"))

coverage <- data[data$type == "coverage",]

coverage$group = factor(coverage$group, levels=c("High", "Median", "Low"))

coverage <- ggplot(coverage, aes(x=year, y=dollars.mhz.pop, colour=income, shape=group))  +
  geom_point(size=3) +
  geom_label_repel(aes(label = iso3), size = 3) +
  scale_x_continuous(expand = c(0, 0.1), limits = c(2008,2017),
                     breaks= c(2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017)) +
  scale_y_continuous(expand = c(0, 0.1)) +
  annotate("text", x = 2009.2, y = 2.86, label = "Extreme", vjust=-1) +
  geom_hline(yintercept=2.86, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2009.2, y = 1.88, label = "Outliers", vjust=-1) +
  geom_hline(yintercept=1.88, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2009.2, y = 0.91, label = "High", vjust=-1) +
  geom_hline(yintercept=0.91, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2009.2, y = 0.58, label = "Median", vjust=-1) +
  geom_hline(yintercept=0.58, linetype="dashed", color = "grey", size=.5) +
  theme(axis.text.x = element_text(angle = 30)) +
  guides(colour=guide_legend(title="Income"), shape=guide_legend(title="Price")) +
  labs(title = "Coverage spectrum prices comprising 700 MHz, 800 MHz, 850 MHz and 900 MHz", 
       x=NULL, 
       y='$ / MHz / Per Capita (USD)',
       subtitle = "Prices adjusted for PPP exchange rates, inflation and license duration, and include annual fees."
       )

capacity <- data[data$type == "capacity",]

capacity$group = factor(capacity$group, levels=c("Extreme outlier", "Outlier", "High", "Median", "Low"))

capacity <- ggplot(capacity, aes(x=year, y=dollars.mhz.pop, colour=income, shape=group))  +
  geom_point(size=3) +
  geom_label_repel(aes(label = iso3), size = 3) +
  scale_x_continuous(expand = c(0, 0.1),  limits = c(2008,2017),
                     breaks= c(2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017)) +
  scale_y_continuous(expand = c(0, 0.035)) +
  annotate("text", x = 2009.2, y = 1.26, size=3.5,label = "Extreme", vjust=-1) +
  geom_hline(yintercept=1.26, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2009.2, y = 0.80, size=3.5,label = "Outliers", vjust=-1) +
  geom_hline(yintercept=0.80, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2009.2, y = 0.35, size=3.5,label = "High", vjust=-1) +
  geom_hline(yintercept=0.35, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2009.2, y = 0.13, size=3.5,label = "Median", vjust=-1) +
  geom_hline(yintercept=0.13, linetype="dashed", color = "grey", size=.5) +
  theme(axis.text.x = element_text(angle = 30)) +
  guides(colour=guide_legend(title="Income"), shape=guide_legend(title="Price")) +
  labs(title = "Capacity spectrum prices comprising AWS, PCS, 1800 MHz, 2100 MHz and 2600 MHz", 
       x=NULL, 
       y='$ / MHz / Per Capita (USD)',
       subtitle = "Prices adjusted for PPP exchange rates, inflation and license duration, and include annual fees."
      )


panel <- ggarrange(coverage, capacity, ncol = 1, nrow = 2, align = c("hv"), common.legend = TRUE, legend="bottom")

path = file.path(folder, 'figures', 'panel.png')
ggsave(path, units="in", width=8, height=12)
print(panel)
dev.off()

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

data <- read.csv(file.path(folder, 'data_inputs', 'spectrum_by_cluster_country.csv'))

data$income[data$Country == 'Uganda'] <- 'Lower'
data$income[data$Country == 'Kenya'] <- 'Lower Middle'
data$income[data$Country == 'Senegal'] <- 'Lower Middle'
data$income[data$Country == 'Pakistan'] <- 'Lower Middle'
data$income[data$Country == 'Albania'] <- 'Upper Middle'
data$income[data$Country == 'Peru'] <- 'Upper Middle'
data$income[data$Country == 'Mexico'] <- 'Upper Middle'

data$income = factor(data$income, levels=c("Upper Middle", "Lower Middle", "Lower"))

cluster_prices <- ggplot(data, aes(x=Year, y=usd_per_mhz_per_pop, colour=income))  + 
  geom_point(size=3) +
  geom_label_repel(aes(label = Country), size = 3) +
  scale_x_continuous(limits = c(2010,2018),
                     breaks= c(2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018)) +
  scale_y_continuous(limits=c(0, 0.2)) +
  theme(axis.text.x = element_text(angle = 30)) +
  guides(colour=guide_legend(title="Income")) +
  labs(title = "Spectrum Prices", x=NULL, y='$ / MHz / Per Capita (USD)')

#export to folder
path = file.path(folder, 'figures', 'cluster_prices.png')
ggsave(path, units="in", width=8, height=8)
print(cluster_prices)
dev.off()

subset <- select(data, Country, usd_per_mhz_per_pop)

mean_spectrum_prices <- aggregate(x = subset$usd_per_mhz_per_pop,                
                                  by = list(subset$Country),              
                                  FUN = mean) 
               