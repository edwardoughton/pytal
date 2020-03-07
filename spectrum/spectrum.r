#Spectrum costs
library(tidyverse)
require("ggrepel")

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

library(ggpubr)

panel <- ggarrange(coverage, capacity, ncol = 1, nrow = 2, align = c("hv"), common.legend = TRUE, legend="bottom")

# #export to folder
# path = file.path(folder, 'figures', 'panel.tiff')
# tiff(path, units="in", width=10, height=10, res=300)
# print(panel)
# dev.off()

path = file.path(folder, 'figures', 'panel.png')
ggsave(path, units="in", width=8, height=12)
print(panel)
dev.off()
