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

data$settlement_type = factor(data$settlement_type, 
                              levels=c("urban",
                              "rural"),
                      labels=c("Urban",
                               "Rural"
                               ))

subscriptions <- ggplot(data, aes(x=year, y=penetration, group=country)) +
  geom_point(aes(shape=country, color=country), size=2.5) +
  geom_line(aes(color=country)) +
  scale_shape_manual(values=c(0, 1, 2, 3, 4, 5, 6, 7, 8)) +
  scale_color_manual(values=c("#F0E442", "#F0E442","#E69F00", "#E69F00","#D55E00", "#0072B2", "#56B4E9","#009E73"))+
  geom_vline(xintercept=2020, linetype="dashed", color = "grey", size=.5) +
  scale_x_continuous(expand = c(0, 0), limits = c(2020,2030), breaks = seq(2020,2030,1)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0,95)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), 
        legend.position = "bottom", legend.title=element_blank()) +
  labs(title = "Smartphone Penetration", 
       subtitle = "Forecast: 2020-2030 ",
       x = NULL, y = "Smartphone Adoption (%)") +
  guides(colour=guide_legend(ncol=4)) +
  facet_wrap(~settlement_type, ncol=1)

path = file.path(folder, 'figures', 'smartphones.png')
ggsave(path, units="in", width=7, height=7, dpi=300)
print(subscriptions)
dev.off()
