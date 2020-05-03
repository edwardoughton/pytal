#Spectrum costs
library(tidyverse)
library(ggpubr)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_inputs = file.path(folder, "data_inputs")

files = list.files(path=folder_inputs, pattern="*.csv")

data <- 
  do.call("rbind", 
          lapply(files, 
                 function(x) 
                   read.csv(file.path(folder_inputs, x), 
                            stringsAsFactors = FALSE)))

data$country = factor(data$country, levels=c("UGA",
                                             "MWI",
                                             "KEN",
                                             "SEN",
                                             "PAK",
                                             "ALB",
                                             "PER",
                                             "MEX"),
                                    labels=c("Uganda\n(Cluster 1)",
                                             "Malawi\n(Cluster 1)",
                                             "Kenya\n(Cluster 2)",
                                             "Senegal\n(Cluster 2)",
                                             "Pakistan\n(Cluster 3)",
                                             "Albania\n(Cluster 4)",
                                             "Peru\n(Cluster 5)",
                                             "Mexico\n(Cluster 6)"))

subscriptions <- ggplot(data, aes(x=year, y=penetration, colour=country, group=country)) + 
  scale_colour_manual(values = c("#F0E442", "#F0E442","#E69F00", "#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73")) + 
  geom_point() +   geom_line() +
  geom_vline(xintercept=2020, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2020, y = 25, label = "Historical", vjust=-1, angle = 90) +
  annotate("text", x = 2021, y = 25, label = "Forecast", vjust=-1, angle = 90) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "bottom") +
  labs(title = "Mobile Market Penetration", colour=NULL,
       subtitle = "Historical: 2010-2020. Forecast: 2020-2030 ",
       x = NULL, y = "Unique Mobile Subscribers (%)") + 
  scale_x_continuous(expand = c(0, 0), limits = c(2010,2030), breaks = seq(2010,2030,1)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0,95)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=4)) 
 
path = file.path(folder, 'figures', 'cell_subscriptions.png')
ggsave(path, units="in", width=7, height=7, dpi=300)
print(subscriptions)
dev.off()

