import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle


# Generate a larger, more realistic dataset with clear fraud rules
np.random.seed(42)
num_samples = 5000
amounts = np.random.randint(10, 2000, num_samples)
# time in seconds since midnight (0-86399)
times = np.random.randint(0, 86400, num_samples)

# Define fraud: (high amount AND suspicious hour) OR very high amount
# Convert seconds to hours
hours = (times / 3600).astype(int) % 24
# Fraud if: (amount > 1200 AND hour between 22-4) OR (amount > 1800)
is_fraud = (((amounts > 1200) & ((hours >= 22) | (hours <= 4))) | (amounts > 1800)).astype(int)

data = {
    "amount": amounts,
    "time": times,
    "is_fraud": is_fraud
}
df = pd.DataFrame(data)

# Train model
X = df[["amount", "time"]]
y = df["is_fraud"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Save the model
with open("model_rndf.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully!")
