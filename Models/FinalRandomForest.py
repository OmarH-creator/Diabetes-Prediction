import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, KBinsDiscretizer
from sklearn.metrics import accuracy_score, f1_score, recall_score

# Load data
train = pd.read_csv('diabetes_train_smote_normalized.csv')
test = pd.read_csv('diabetes_test_normalized.csv')

# Encode target class
le_class = LabelEncoder()
train['class'] = le_class.fit_transform(train['class'])
test['class'] = le_class.transform(test['class'])

# Separate features and target
X_train = train.drop('class', axis=1)
y_train = train['class']

X_test = test.drop('class', axis=1)
y_test = test['class']

# Encode gender
le_gender = LabelEncoder()
X_train['gender'] = le_gender.fit_transform(X_train['gender'])
X_test['gender'] = le_gender.transform(X_test['gender'])

# Discretize numeric columns only
numeric_cols = X_train.columns.drop('gender')

discretizer = KBinsDiscretizer(
    n_bins=3,
    encode='ordinal',
    strategy='quantile'
)

X_train[numeric_cols] = discretizer.fit_transform(X_train[numeric_cols])
X_test[numeric_cols] = discretizer.transform(X_test[numeric_cols])

# Train Random Forest
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Metrics
accuracy = accuracy_score(y_test, predictions)
f1 = f1_score(y_test, predictions, average='weighted')
recall = recall_score(y_test, predictions, average='weighted')

print(f"Accuracy: {accuracy * 100:.2f}%")
print(f"F1 Score: {f1 * 100:.2f}%")
print(f"Recall:   {recall * 100:.2f}%")