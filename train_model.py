import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# Load your data (ensure you have this file)
data = pd.read_csv('hotel_prices.csv')  # Adjust path to your dataset

# Prepare features and target
X = data[['original_price']]  # Features
y = data['offer_price']  # Target

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'price_prediction_model.pkl')
