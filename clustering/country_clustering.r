###country clustering script
# install.packages("tidyverse")
library(tidyverse)
# library(ggplot2)
# library(dplyr)

#set directory for input data 
data_input <- "C:\\Users\\edwar\\Dropbox\\Academic Projects\\WB 5G assessment\\countries for clustering.csv"
# data_input <- "/home/edward/Dropbox/Academic Projects/WB 5G assessment/countries for clustering.csv"

#set directory for export 
data_input_directory <- "C:\\Users\\edwar\\Dropbox\\Academic Projects\\WB 5G assessment"
# data_input_directory <- "/home/edward/Dropbox/Academic Projects/WB 5G assessment"

#read in data
mydata <- read.csv(data_input)

#subset - remove high income
# mydata <- mydata[which(mydata$income != 'High income'), ]

#get statistical summary
summary(mydata)

#remove missing data
mydata <- na.omit(mydata) # listwise deletion of missing

#allocate country name as row name 
rownames(mydata) <- mydata$country

##############################################
### subset 7 variables and run with 7 clusters
subset <- select(mydata, coverage_4g, pop_density, urban_pop, total_pop, gdp_per_cap, rural_pop, area)

#scale data
subset <- scale(subset) # standardize variables

#determine number of clusters
wss <- ''
for (i in 1:20) wss[i] <- sum(kmeans(subset, centers=i)$withinss)

#set export directory and export wgsss
tiff("wgsss_7-variables.tiff")
plot(1:20, wss, type="b", xlab="Number of Clusters", ylab="Within groups sum of squares")
dev.off()

# K-Means Cluster Analysis
fit <- kmeans(subset, 12) 
# aggregate(subset,by=list(fit$cluster),FUN=mean)
subset <- data.frame(subset, fit$cluster)

#set directory and export
write.csv(subset, 'results_12-clusters_7-variables.csv')

# K-Means Cluster Analysis
fit <- kmeans(subset, 16) 
# aggregate(subset,by=list(fit$cluster),FUN=mean)
subset$fit.cluster <- NULL
subset <- data.frame(subset, fit$cluster)

#export
write.csv(subset, 'results_16-clusters_7-variables.csv')

# K-Means Cluster Analysis
fit <- kmeans(subset, 18) 
# aggregate(subset,by=list(fit$cluster),FUN=mean)
subset$fit.cluster <- NULL
subset <- data.frame(subset, fit$cluster)

#set directory and export
write.csv(subset, 'results_18-clusters_7-variables.csv')