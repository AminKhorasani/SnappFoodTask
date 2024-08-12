import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import scipy.stats as stats


# Function to convert Persian numbers to Latin numbers
def persian_to_latin(input_str):
    persian_nums = '۰۱۲۳۴۵۶۷۸۹'
    latin_nums = '0123456789'
    trans_table = str.maketrans(persian_nums, latin_nums)
    return input_str.translate(trans_table)


# Function to classify based on bounds
def classify(score, bounds):
    if bounds[0] <= score <= bounds[1]:
        return 'E'
    elif bounds[1] <= score <= bounds[2]:
        return 'D'
    elif bounds[2] <= score <= bounds[3]:
        return 'C'
    elif bounds[3] <= score <= bounds[4]:
        return 'B'
    elif bounds[4] <= score <= bounds[5]:
        return 'A'
    else:
        return 'Unknown'  # For any score that doesn't fit the expected range


def process_data(path):
    data = pd.read_csv(path)

    min_max_scaler = MinMaxScaler()

    # Handling missing values
    data['Review'] = data['Review'].fillna('0')
    data['Category'] = data['Category'].fillna('Unknown')
    data = data.dropna(subset=['Rate'])

    # Handling data type
    data['Minimum Purchase'] = data['Minimum Purchase'].apply(lambda x: int(re.sub(r'\D', '', x)))
    data['Discount'] = data['Discount'].apply(lambda x: 1 if x != 'No Discount' else 0)
    data['Rate'] = data['Rate'].apply(persian_to_latin).replace('جدید', None)
    data['Review'] = data['Review'].apply(persian_to_latin).astype(int)
    data['Rate'] = pd.to_numeric(data['Rate'])

    # Handling duplicates
    data.drop_duplicates(inplace=True)

    # Draw a Correlation matrix for more insight on features
    corr_data = data[['Discount', 'Rate', 'Review', 'Minimum Purchase']]
    correlation_matrix = corr_data.corr()

    plt.figure(figsize=(10, 8))

    # Draw the heatmap
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', square=True, linewidths=.5)
    plt.title('Correlation Matrix of Features')
    plt.savefig('Figures/CorrelationMatrix.jpg', format='jpg', dpi=300)
    plt.show()

    # Remove additional features
    data = data[['Name', 'Location', 'Rate', 'Review']]

    # Save data to csv
    data.to_csv('Datasets/CleandSnappFoodDataset.csv', index=False)

    # Performing data analysis
    data = data.dropna(subset=['Rate'])
    data['Review_normalized'] = min_max_scaler.fit_transform(data[['Review']])
    data['Rate_normalized'] = min_max_scaler.fit_transform(data[['Rate']])

    print(data.shape)
    # q-q plot
    rate_standardized = (data['Rate_normalized'] - data['Rate_normalized'].mean()) / data['Rate_normalized'].std()
    plt.figure(figsize=(6,6))
    stats.probplot(rate_standardized, dist="norm", plot=plt)
    plt.title('Q-Q Plot for Standardized Rate')
    plt.savefig('Figures/Q-Q Plot for normalized rate.jpg', format='jpg', dpi=300)
    plt.show()

    rate_standardized = (data['Review_normalized'] - data['Review_normalized'].mean()) / data['Review_normalized'].std()
    plt.figure(figsize=(6,6))
    stats.probplot(rate_standardized, dist="norm", plot=plt)
    plt.title('Q-Q Plot for Standardized Review')
    plt.savefig('Figures/Q-Q Plot for normalized review.jpg', format='jpg', dpi=300)
    plt.show()

    # Box plot
    data_long = pd.melt(data, id_vars=['Name'], value_vars=['Rate_normalized', 'Review_normalized'], var_name='Metric', value_name='Value')

    sns.boxplot(x='Metric', y='Value', data=data_long, width=0.1)
    plt.title('Comparison of Rate and Review Distributions')
    plt.xlabel('Metric')
    plt.ylabel('Values')
    plt.savefig('Figures/Box plot for normalized rate and review.jpg', format='jpg', dpi=300)
    plt.show()

    # KPI
    review_weight = 0.7
    review_count_weight = 0.3
    data['CSAT'] = ((data['Rate'] * review_weight) + (data['Review'] * review_count_weight))
    # Normalization
    data['Normalized_CSAT'] = min_max_scaler.fit_transform(data[['CSAT']])

    # Plots for normalized KPI
    # Histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(data['Normalized_CSAT'], kde=True)
    plt.title('Distribution of Normalized Customer Satisfaction Scores')
    plt.xlabel('Normalized Customer Satisfaction Score')
    plt.ylabel('Frequency')
    plt.savefig('Figures/Histogram_normalizedCSAT.jpg', format='jpg', dpi=300)
    plt.show()

    # Box plot
    sns.boxplot(y=data['Normalized_CSAT'], width=0.1)  # Adjust width and color for clarity
    plt.title('Distribution of Normalized Customer Satisfaction Scores')
    plt.xlabel('Normalized Satisfaction Score')
    plt.savefig('Figures/BoxPlot_normalizedCSAT.jpg', format='jpg', dpi=300)
    plt.show()

    # Classification from A to E
    # Clustering
    kmeans = KMeans(n_clusters=5, random_state=42)
    data['Cluster'] = kmeans.fit_predict(data[['Normalized_CSAT']])
    cluster_min_max = data.groupby('Cluster')['Normalized_CSAT'].agg(['min', 'max'])
    cluster_min_max = cluster_min_max.sort_values(by=['min'])

    bounds = [0]
    for i in range(4):
        bound = (cluster_min_max['min'].iloc[i + 1] + cluster_min_max['max'].iloc[i])/2
        bounds.append(bound)
    bounds.append(1)

    # Apply the classification function
    data['Class'] = data['Normalized_CSAT'].apply(lambda x: classify(x, bounds))

    # Create a scatter plot
    plt.figure(figsize=(10, 6))
    scatter_plot = sns.scatterplot(x='Rate_normalized', y='Review_normalized', hue='Class', data=data, palette='viridis', s=100)

    # Enhancing the plot
    plt.title('Scatter Plot of Normalized Rate vs. Review by Class')
    plt.xlabel('Normalized Rate')
    plt.ylabel('Normalized Review')
    plt.legend(title='Class', bbox_to_anchor=(1.05, 1), loc='upper left')  # Place legend outside the plot
    plt.grid(True)
    plt.savefig('Figures/Classified_restaurants.jpg', format='jpg', dpi=300)
    plt.show()

    # Save data to csv
    data.to_csv('Datasets/FinalSnappFoodDataset.csv', index=False)

    return data

