import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from nltk.corpus import stopwords
import nltk
import string
from nltk.stem.porter import PorterStemmer
import pickle

# Load the data
df = pd.read_csv("categoryData.csv")

# Preprocess text
ps = PorterStemmer()
def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    y = [i for i in text if i.isalnum()]
    text = [i for i in y if i not in stopwords.words('english') and i not in string.punctuation]
    y = [ps.stem(i) for i in text]
    return " ".join(y)

df['transformed_text'] = df['text'].apply(transform_text)

# TF-IDF Vectorization
tfidf = TfidfVectorizer()
X = tfidf.fit_transform(df['transformed_text']).toarray()
y = df['Pattern Category'].values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# SVC model with 'ovr' decision_function_shape for multiclass
svc = SVC(kernel='sigmoid', decision_function_shape='ovr')
svc.fit(X_train, y_train)

# Predictions
y_pred = svc.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Precision Score:", precision_score(y_test, y_pred, average='weighted'))

# Save the model and label_encoder for later use
pickle.dump(svc, open("category_model.pkl", "wb"))
pickle.dump(tfidf, open("category_vectoriser.pkl", "wb"))