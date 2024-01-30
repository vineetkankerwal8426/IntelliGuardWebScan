import pandas as pd
from sklearn.svm import SVC
from collections import Counter
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
import pickle
import nltk
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,precision_score
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
import string
from nltk.stem.porter import PorterStemmer
df = pd.read_csv("dataset.csv")
df['label'].value_counts()

nltk.download('punkt')
nltk.download('stopwords')
ps = PorterStemmer()
def transform_text(text):
  text = text.lower()
  text = nltk.word_tokenize(text)
  y = []
  for i in text:
    if i.isalnum():
      y.append(i)

  text = y[:]
  y.clear()
  for i in text:
    if i not in stopwords.words('english') and i not in string.punctuation:
      y.append(i)

  text = y[:]
  y.clear()
  for i in text:
    y.append(ps.stem(i))

  return " ".join(y)

df['transformed_text'] = df['text'].apply(transform_text)
dark_corpus=[]
for i in df[df['label']==1]['transformed_text'].tolist():
  for j in i.split():
    dark_corpus.append(j)
Counter(dark_corpus).most_common(30)

cv = CountVectorizer()
tfidf = TfidfVectorizer()#max_features=1000)
X = tfidf.fit_transform(df['transformed_text']).toarray()
y = df['label'].values

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = 0.2)

svc = SVC(kernel='rbf')
# svc=RandomForestClassifier(n_estimators = 50)
svc.fit(X_train,y_train)
y_pred = svc.predict(X_test)
print(accuracy_score(y_test,y_pred))
print(confusion_matrix(y_test,y_pred))
print(precision_score(y_test,y_pred))

pickle.dump(tfidf,open('vectoriser.pkl','wb'))
pickle.dump(svc,open('model.pkl','wb'))