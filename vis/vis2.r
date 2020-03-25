###plot pysim5g lookup tables
# install.packages("tidyverse")
library(tidyverse)
library(plyr)
library(ggpubr)
#####################

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#get path to full tables via the data folder
full_tables <- file.path(folder, '..', 'data', 'raw', 'pysim5g', 'full_tables')

#get a list of all files in the folder ending in .csv
myfiles = list.files(path=full_tables, pattern="*.csv", full.names=TRUE)

#import data for all files in file list
data = ldply(myfiles, read_csv)

#select the ISD of 10000m to plot
data = data[data$inter_site_distance_m == 10000,]

data = data[data$frequency_GHz != 1.8 & data$frequency_GHz != 3.7 ,]

#drop results over 5km distance
data = data[data$r_distance <= 5000,]

#turn env into factor and relabel
data$environment = factor(data$environment, levels=c("urban",
                                                     "suburban",
                                                     "rural"),
                                            labels=c("Urban",
                                                     "Suburban",
                                                     "Rural"))

#subset the data for plotting
data = select(data, environment, frequency_GHz, ant_type, r_distance, spectral_efficiency_bps_hz, capacity_mbps, capacity_mbps_km2)

#plot data
#locally estimated scatterplot smoothing
#https://ggplot2.tidyverse.org/reference/geom_smooth.html
pysim5g_plot_se = ggplot(data, aes(x=r_distance/1000, y=spectral_efficiency_bps_hz, colour=factor(frequency_GHz))) + 
  geom_point() + 
  geom_smooth() +
  scale_x_continuous(expand = c(0, 0)) + scale_y_continuous(expand = c(0, 0)) +
  theme(legend.position="bottom") + guides(colour=guide_legend(ncol=7)) +
  labs(title = 'Spectral Efficiency vs User Distance', x = NULL, y='Spectral Efficiency (Bps/Hz)', colour='Frequency (GHz)\n(10MHz BW)') +
  facet_wrap(~environment)

#plot data
#locally estimated scatterplot smoothing
#https://ggplot2.tidyverse.org/reference/geom_smooth.html
pysim5g_plot_capacity = ggplot(data, aes(x=r_distance/1000, y=capacity_mbps, colour=factor(frequency_GHz))) + 
  geom_point() + 
  geom_smooth() +
  scale_x_continuous(expand = c(0, 0)) + scale_y_continuous(expand = c(0, 0)) +
  theme(legend.position="bottom") + guides(colour=guide_legend(ncol=7)) +
  labs(title = 'Channel Capacity vs User Distance', x = NULL, y='Capacity (Mbps)', colour='Frequency (GHz)\n(10MHz BW)') +
  facet_wrap(~environment)

#plot data
#locally estimated scatterplot smoothing
#https://ggplot2.tidyverse.org/reference/geom_smooth.html
pysim5g_plot_capacity_km2 = ggplot(data, aes(x=r_distance/1000, y=capacity_mbps_km2, colour=factor(frequency_GHz))) + 
  geom_point() + 
  geom_smooth() +
  scale_x_continuous(expand = c(0, 0)) + scale_y_continuous(expand = c(0, 0)) +
  theme(legend.position="bottom") + guides(colour=guide_legend(ncol=7)) +
  labs(title = 'Area Capacity vs User Distance', x = "Distance (km)", y='Capacity (Mbps/km^2)', colour='Frequency (GHz)\n(10MHz BW)') +
  facet_wrap(~environment)

panel = ggarrange(pysim5g_plot_se, pysim5g_plot_capacity, pysim5g_plot_capacity_km2,  
                  common.legend = TRUE, legend = 'bottom', ncol = 1, nrow = 3)

path = file.path(folder, 'figures', 'pysim5g_panel.png', dpi=300)
ggsave(path, units="in", width=8, height=10)
print(panel)
dev.off()
