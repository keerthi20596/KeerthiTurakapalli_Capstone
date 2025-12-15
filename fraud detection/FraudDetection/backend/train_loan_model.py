import os
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import MinMaxScaler

BASE_DIR = os.path.dirname(__file__)

def find_dataset():
    # Look for dataset in repo backend, workspace root, and Downloads
    candidates = [
        os.path.join(BASE_DIR, 'loan_approval_dataset.csv'),
        os.path.join(BASE_DIR, 'loan_approval_encoded.csv'),
        os.path.expanduser('~/Downloads/loan_approval_dataset.csv'),
        os.path.expanduser('~/Downloads/loan_approval_encoded.csv'),
        # Also check common alternative Downloads path (attachment source)
        r'C:\Users\kanch\Downloads\loan_approval_dataset.csv',
        r'C:\Users\kanch\Downloads\loan_approval_encoded.csv',
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    raise FileNotFoundError('Could not find loan_approval_dataset.csv or loan_approval_encoded.csv in expected locations')


def load_and_preprocess(path):
    df = pd.read_csv(path)
    # If target already encoded as 0/1 keep, else map
    df.columns = df.columns.str.strip()
    if 'loan_status' not in df.columns:
        raise ValueError('Dataset must contain loan_status column')

    # If loan_status are strings like 'Approved'/'Rejected' map them
    if df['loan_status'].dtype == object:
        df['loan_status'] = df['loan_status'].str.strip().map({'Approved':1, 'Rejected':0})

    # Map education/self_employed if present
    if 'education' in df.columns and df['education'].dtype == object:
        df['education'] = df['education'].str.strip().map({'Graduate':1, 'Not Graduate':0})
    if 'self_employed' in df.columns and df['self_employed'].dtype == object:
        df['self_employed'] = df['self_employed'].str.strip().map({'Yes':1, 'No':0})

    # Drop rows with missing target
    df = df.dropna(subset=['loan_status'])

    # Select numeric features automatically (exclude target and id)
    X = df.select_dtypes(include=[np.number]).drop(columns=['loan_status', 'loan_id'], errors='ignore')
    y = df['loan_status'].astype(int)

    # Fill NA with 0 for numeric
    X = X.fillna(0)
    return X, y


def train_and_save():
    path = find_dataset()
    print('Using dataset:', path)
    X, y = load_and_preprocess(path)

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    # Use fewer estimators for faster training, optimize with n_jobs
    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1, max_depth=15)
    print('Training model... this may take a minute...')
    model.fit(X_train, y_train)
    print('Training complete!')

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    model_path = os.path.join(BASE_DIR, 'loan_model.pkl')
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)

    print('Model saved to', model_path)
    print('Scaler saved to', scaler_path)
    print('Accuracy:', acc)
    print(report)


if __name__ == '__main__':
    train_and_save()
