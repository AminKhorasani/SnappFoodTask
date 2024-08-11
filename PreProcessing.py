import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt

dataset_path = 'Datasets/SnappFoodDataset.csv'
data = pd.read_csv(dataset_path)

# Function to convert Persian numbers to Latin numbers
def persian_to_latin(input_str):
    persian_nums = '۰۱۲۳۴۵۶۷۸۹'
    latin_nums = '0123456789'
    trans_table = str.maketrans(persian_nums, latin_nums)
    return input_str.translate(trans_table)


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
