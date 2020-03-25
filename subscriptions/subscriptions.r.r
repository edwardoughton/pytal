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

data$country = factor(data$country, levels=c("PAK",
                                             "MEX",
                                             "PER",
                                             "UGA",
                                             "DZA",
                                             "KEN",
                                             "SEN"),
                      labels=c("Pakistan\n(Cluster 1)",
                               "Mexico\n(Cluster 2)",
                               "Peru\n(Cluster 3)",
                               "Uganda\n(Cluster 4)",
                               "Algeria\n(Cluster 5)",
                               "Kenya\n(Cluster 6)",
                               'Senegal\n(Cluster 6)'))

subscriptions <- ggplot(data, aes(x=year, y=penetration, colour=country, group=country)) + 
  geom_point() +   geom_line() +
  geom_vline(xintercept=2017, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2017, y = 25, label = "Historical", vjust=-1, angle = 90) +
  annotate("text", x = 2018.2, y = 25, label = "Forecast", vjust=-1, angle = 90) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "bottom") +
  labs(title = "Mobile Cellular Subscriptions", colour=NULL,
       subtitle = "Historical: 2007-2017. Forecast: 2018-2030 ",
       x = NULL, y = "Cell Subscriptions (Per 100 Inhabitants)") + 
  scale_x_continuous(expand = c(0, 0), limits = c(2005,2030), breaks = seq(2005,2030,1)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0,175)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=7)) 
 

# path = file.path(folder, 'figures', 'cell_subscriptions.png')
# ggsave(path, units="in", width=7, height=7, dpi=300)
# print(subscriptions)
# dev.off()

subscribers <- ggplot(data, aes(x=year, y=unique_users, colour=country, group=country)) + 
  geom_point() +   geom_line() +
  geom_vline(xintercept=2017, linetype="dashed", color = "grey", size=.5) +
  annotate("text", x = 2017, y = 13, label = "Historical", vjust=-1, angle = 90) +
  annotate("text", x = 2018.2, y = 13, label = "Forecast", vjust=-1, angle = 90) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "bottom") +
  labs(title = "Unique Mobile Users", colour=NULL,
       subtitle = "Historical: 2007-2017. Forecast: 2018-2030 ",
       x = NULL, y = "Unique Cell Users (Percent of Population)") + 
  scale_x_continuous(expand = c(0, 0), limits = c(2005,2030), breaks = seq(2005,2030,1)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0,100)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(colour=guide_legend(ncol=7)) 

# 
# path = file.path(folder, 'figures', 'unique_subscribers.png')
# ggsave(path, units="in", width=7, height=7, dpi=300)
# print(subscribers)
# dev.off()

subscriber_panel <- ggarrange(
  subscriptions, subscribers, 
  ncol = 1, nrow = 2, align = c("hv"), 
  common.legend = TRUE, legend='bottom')

#export to folder
path = file.path(folder, 'figures', 'subscriber_panel.png')
ggsave(path, units="in", width=7.5, height=9, dpi=300)
print(subscriber_panel)
dev.off()
