###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)
library(ggrepel)

#get folder directory
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

#set cluster number
cluster_num <- 6

#read in data
mydata <- read.csv(file.path(folder, 'data_inputs', 'country_data.csv'))

#split high income countries
high_income <- mydata[which(mydata$income == 'High income'),]

#drop high income countries
mydata <- mydata[which(mydata$income != 'High income'), ]

#get statistical summary
summary(mydata)

#remove missing data
mydata <- na.omit(mydata) 

#allocate country name as row name 
rownames(mydata) <- mydata$country

#subset country info df
country_info = select(mydata, income, region)

### subset 3 main variables
subset <- select(mydata, coverage_4g, pop_density, gdp_per_cap)

#scale data to be mean centralized 
subset <- scale(subset) 

#determine number of clusters
wss <- ''
for (i in 1:20) wss[i] <- sum(kmeans(subset, centers=i)$withinss)

#set export directory and export wgsss
tiff(file.path(folder, 'figures', "wgsss_variables.tiff"))
plot(1:20, wss, type="b", xlab="Number of Clusters", ylab="Within groups sum of squares")
dev.off()

# K-Means Cluster Analysis
fit <- kmeans(subset, cluster_num) 
data <- data.frame(subset, fit$cluster)

#turn row names into country column
country_info$country <- rownames(country_info)

#turn row names into country column
data$country <- rownames(data)

#merge cluster results with additional country info
data <- merge(data, country_info, by='country')

#omit missing data rows
data <- na.omit(data) # listwise deletion of missing

#country characters to lower format for merging 
data$country <- tolower(data$country)

#remove whitespace for merging
data$country <- gsub(" ", "", data$country)

#read file containing ISO3 country codes
iso3 <- read.csv(file.path(folder, 'data_inputs', 'global_information.csv'))

#lower characters and remove whitespace for merging
iso3$country <- tolower(iso3$country)
iso3$country <- gsub(" ", "", iso3$country)

#merge data
data <- merge(data, iso3, by='country', all=TRUE)

#omit missing rows
data <- na.omit(data) 

#rename variable to cluster
names(data)[names(data) == 'fit.cluster'] <- 'cluster'

#select desired columns
long <- select(data, country, coverage_4g, pop_density, gdp_per_cap, cluster, income, region, ISO_3digit)

#transform from wide to long
long <- gather(long, 'coverage_4g', 'pop_density', 'gdp_per_cap', key='metric', value='value')

#create factor levels/labels
long$metric = factor(long$metric, levels=c("gdp_per_cap", "pop_density", "coverage_4g"),
                                  labels=c("GDP per capita", "Population Density", "4G Coverage"))

#create factor levels/labels
long$income = factor(long$income, levels=c("Low income", "Lower middle income", "Upper middle income"))

#rename columns
names(long)[names(long) == 'region'] <- 'Region'
names(long)[names(long) == 'income'] <- 'Income'

#specify boxplot
boxplot <- ggplot(long, aes(factor(cluster), value, colour=Region, shape=Income)) + 
  geom_boxplot(aes(group=factor(cluster))) +
  geom_jitter(width = 0.4, height=0.5, size=1.5) + theme(legend.position = "bottom") +  
  expand_limits(x = 0, y = 0) + 
  guides(colour=guide_legend(ncol=2), shape=guide_legend(ncol=1, reverse=T)) + 
  scale_y_continuous(breaks = seq(-2, 8, by = 1)) +
  labs(title = "Summary Statistics by Cluster", x='Cluster Number', y='Mean Centred Values',
       subtitle = "Based on GDP Per Capita, Population Density and 4G Coverage (Mean Centered)") +
  facet_wrap(~metric)

#export to folder
path = file.path(folder, 'figures', 'clustering_boxplot.tiff')
tiff(path, units="in", width=8, height=6, res=300)
print(boxplot)
dev.off()

#specify boxplot
boxplot_labelled <- ggplot(long, aes(factor(cluster), value, colour=Region, shape=Income)) + 
  geom_boxplot(aes(group=factor(cluster))) +
  geom_jitter(width = 0.4, height=0.5, size=1.5) + theme(legend.position = "bottom") +  
  expand_limits(x = 0, y = 0) + 
  guides(colour=guide_legend(ncol=2), shape=guide_legend(ncol=1, reverse=T)) + 
  scale_y_continuous(breaks = seq(-2, 8, by = 1)) +
  labs(title = "Summary Statistics by Cluster", x='Cluster Number', y='Mean Centred Values',
       subtitle = "Based on GDP Per Capita, Population Density and 4G Coverage (Mean Centered)") +
  facet_wrap(~metric, nrow=1, ncol=3) +
  geom_label_repel(aes(label = ISO_3digit), box.padding = 0.3, point.padding = 0.3, 
       segment.color = 'grey50') 

#export to folder
path = file.path(folder, 'figures', 'boxplot_labelled.tiff')
tiff(path, units="in", width=12, height=12, res=300)
print(boxplot_labelled)
dev.off()

#subset data for exporting
data <- select(data, ISO_3digit, country, cluster)

#allocate high income group to df
high_income$cluster <- 'High Income'

#remove whitespace and lower for merging
high_income$country <- gsub(" ", "", high_income$country)
high_income$country <- tolower(high_income$country)

#merge on country column
high_income <- merge(high_income, iso3, by='country')

#subset data
high_income <- select(high_income, ISO_3digit, country, cluster)

#concatenate dfs vertically via row bind
data = rbind(data, high_income)

#export data
write.csv(data, file.path(folder, 'results', 'data_clustering_results.csv'))


