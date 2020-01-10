###VISUALISE MODEL OUTPUTS###
# install.packages("tidyverse")
library(tidyverse)
library(ggrepel)

#set directory for export 
data_input_directory <- "C:\\Users\\edwar\\Dropbox\\Academic Projects\\WB 5G assessment"
data_input <- "C:\\Users\\edwar\\Dropbox\\Academic Projects\\WB 5G assessment\\countries for clustering.csv"

data <- read.csv('results_16-clusters_7-variables.csv')

data <- select(data, X, fit.cluster)

#read in data
mydata <- read.csv(data_input)

#remove missing data
mydata <- na.omit(mydata) # listwise deletion of missing

#merge both dfs
data <- merge(mydata, data, by.x='country', by.y='X')
data$country <- tolower(data$country)
data$country <- gsub(" ", "", data$country)

iso3 <- read.csv('global_information.csv')
iso3$country <- tolower(iso3$country)
iso3$country <- gsub(" ", "", iso3$country)

data <- merge(data, iso3, by='country', all=TRUE)

#remove unwanted
remove(mydata)

# data <- data[!(data$income == "High income"),]
data <- na.omit(data) 

data$coverage_4g <- (data$coverage_4g * 100)

data$pop_density <- (data$pop_density)
data$total_pop <- (data$total_pop)
data$area <- (data$area)

# data$urban_pop <- (data$urban_pop * 100)
data$rural_pop <- (data$rural_pop * 100)

data$gdp_per_cap <- (data$gdp_per_cap)

ggplot(data, aes(x=log(pop_density), y=coverage_4g, color=factor(fit.cluster), shape=factor(income))) + geom_point() 

ggplot(data, aes(x=log(pop_density), y=gdp_per_cap, color=factor(fit.cluster), shape=factor(income))) + geom_point() 

fig1 <- ggplot(data, aes(x=log(pop_density), y=log(gdp_per_cap), shape=factor(income), colour=region)) + geom_point() +
  geom_label_repel(aes(label = ISO_3digit),
                   box.padding   = 0.35, 
                   point.padding = 0.5,
                   segment.color = 'grey50') +   theme_classic() + facet_wrap(~fit.cluster)


### EXPORT TO FOLDER
setwd(data_input_directory)
tiff('fig1.tiff', units="in", width=12, height=12, res=300)
print(fig1)
dev.off()














data$area <- NULL

long = data %>% gather("coverage_4g", "pop_density",  "gdp_per_cap",  key = metric_1, value = value_1)

long = long %>% gather("urban_pop", "total_pop","rural_pop", key = metric_2, value = value_2)

# long$metric_2 <- long$metric
# long$metric_2 <- paste(long$metric_2, "2", sep="_")
# long$value_2 <- long$value

ggplot(long, aes(x=value_1, y=value_2)) +
  geom_point(aes(color=income)) + 
  facet_grid(long$metric_1~long$metric_2)





ggplot(data=data, aes(x=value, )) + geom_histogram(position="identity") + facet_grid(long$metric~long$metric)






long = data %>% gather("coverage_4g", "pop_density", "urban_pop", "total_pop", 
                       "gdp_per_cap", "rural_pop", "area", key = metric, value = value)

ggplot(data=long, aes(x=value)) + geom_histogram(position="identity") + facet_wrap(~long$metric)
