import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Generate sample data
np.random.seed(42)
data = {
    "amount": np.random.randint(10, 1000, 1000),
    "time": np.random.randint(0, 86400, 1000),
    "is_fraud": np.random.choice([0, 1], 1000, p=[0.95, 0.05])
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
