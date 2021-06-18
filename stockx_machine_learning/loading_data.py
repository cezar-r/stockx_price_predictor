import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import scipy.stats as stats

df = pd.read_csv('data/jordan_1_data.txt')

X_with_sizes = df.drop(['shoe_name', 'release_date', 'avg_price_sm_a', 'total_volume_sm_a'], axis=1)
X_with_sizes = X_with_sizes[X_with_sizes['size'] != "None"]
X_no_sizes = df.drop(['shoe_name', 'release_date', 'size', 'avg_price_sm_a'], axis=1)

y_no_sizes = df.loc[:, 'avg_price_sm_a']
y_with_sizes = df[df['size'] != "None"]
y_with_sizes = y_with_sizes.loc[:, 'avg_price_sm_a']

X_train, X_test, y_train, y_test = train_test_split(X_with_sizes, y_with_sizes, test_size = .1)
model = linear_model.LinearRegression()

model.fit(X_train, y_train)

sample = np.array(['9', 670, 5, 530, 12, 460, 20, 425, 36, 400, 28, 354, 32, 350, 47])

y_pred = model.predict(sample.reshape(1, -1))
print(y_pred)

print(model.coef_)
# print(np.sqrt(mean_squared_error(y_test, y_pred)))
# print(r2_score(y_test, y_pred))

plt.style.use("dark_background")
fig, ax = plt.subplots()
plt.scatter(y_test, y_test - y_pred, alpha = .5)
plt.show()