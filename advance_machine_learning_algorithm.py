# -*- coding: utf-8 -*-
"""Advance Machine Learning Algorithm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rQ0jEdlj5Cu5Gs4wG534Q7tZtco-dK-6
"""

from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import statsmodels.api as sm

bank_df = pd.read_csv('bank.csv')
bank_df.head(5)

bank_df.info()

bank_df.subscribed.value_counts()

from sklearn.utils import resample
bank_subscribed_no = bank_df[bank_df.subscribed == 'no']
bank_subscribed_yes = bank_df[bank_df.subscribed == 'yes']
df_minority_unsampled = resample(bank_subscribed_yes,
                                 replace=True,
                                 n_samples=2000)

new_bank_df = pd.concat([bank_subscribed_no, df_minority_unsampled])

from sklearn.utils import shuffle
new_bank_df = shuffle(new_bank_df)

X_features = list( new_bank_df.columns )
X_features.remove('subscribed')
X_features

encoded_bank_df = pd.get_dummies(new_bank_df[X_features],
                                 drop_first = True )

X = encoded_bank_df

Y = new_bank_df.subscribed.map(lambda x: int( x == 'yes'))

from sklearn.model_selection import train_test_split
train_X, test_X, train_y, test_y = train_test_split(X,
                                                    Y,
                                                    test_size=0.3,
                                                    random_state=42)

from sklearn.linear_model import LogisticRegression
logit = LogisticRegression()
logit.fit(train_X, train_y)

pred_y = logit.predict(test_X)

"""**Confusion Matrix**"""

from sklearn import metrics
def draw_cm(actual, predicted ):
  cm = metrics.confusion_matrix(actual, predicted, [1,0])
  sn.heatmap(cm, annot=True,  fmt ='.2f',
    xticklabels = ["Subscribed", "Not Subscribed"],
    yticklabels = ["Subscribed", "Not Subscribed"])
  plt.ylabel('True label')
  plt.xlabel('predicted label')
  plt.show()

cm = draw_cm(test_y, pred_y)

"""**Classification Report**"""

print(metrics.classification_report(test_y, pred_y))

"""**Reciever Operaing Characteristics Curve(ROC) and Area Under ROC (AUC)  Score**"""

predict_proba_df = pd.DataFrame(logit.predict_proba (test_X)  )
predict_proba_df.head()

test_results_df = pd.DataFrame({ 'actual': test_y })
test_results_df = test_results_df.reset_index()
test_results_df['chd_1'] = predict_proba_df.iloc[:,1:2]

test_results_df.head(5)

#passing actual class labels and predicted probability values to compute ROC AUC score

auc_score =  metrics.roc_auc_score(test_results_df.actual,
                                   test_results_df.chd_1)
round( float( auc_score ), 2)

"""**Plotting ROC Curve**"""

def draw_roc_curve( model, test_X, test_y ):
  test_results_df = pd.DataFrame( { 'actual': test_y })
  test_results_df = test_results_df.reset_index()
  predict_proba_df = pd.DataFrame(model.predict_proba(test_X))
  test_results_df['chd_1'] = predict_proba_df.iloc[:,1:2]

fpr,tpr, thresholds = metrics.roc_curve(test_results_df.actual,
                                        test_results_df.chd_1,
                                        drop_intermediate = False  )
auc_score = metrics.roc_auc_score(test_results_df.actual,
                                  test_results_df.chd_1)

plt.figure(figsize=(8,6))
  plt.plot(fpr, tpr, label= 'ROC curve (area  =  %.2f)'  %auc_score)
  plt.plot([0, 1], [0,1], 'k--')
  plt.xlim([0.0, 1.0])
  plt.ylim([0.0, 1.05])

  ## Setting labels and titles
  plt.xlabel('False Positive Rate or [1 - True Negative Rate]')
  plt.ylabel('True Positive Rate')
  plt.title('Receiver operating characteristic example')
  plt.legend(loc="lower right")
  plt.show()

"""# **K- Nearest Neighbours (KNN) Algorithms**"""

from sklearn.neighbors import KNeighborsClassifier
knn_clf = KNeighborsClassifier()
knn_clf.fit(train_X, train_y)

pred_y = knn_clf.predict(test_X)
draw_cm(test_y, pred_y)

print( metrics.classification_report(test_y, pred_y) )

"""**Grid Search for Optimal Paramters**"""

from sklearn.model_selection import GridSearchCV
## Creating a dictionary with hyperparameters and possible values for searching
tuned_parameters = [{'n_neighbors': range(5,10),
'metric': ['canberra', 'euclidean', 'minkowski']}]
## Configuring grid search
clf = GridSearchCV(KNeighborsClassifier(),
tuned_parameters,
cv=10,
scoring='roc_auc')
clf.fit(train_X, train_y )

clf.best_score_

clf.best_params_

"""# **Random Forest**"""

from sklearn.ensemble import RandomForestClassifier
radm_clf = RandomForestClassifier(max_depth=10, n_estimators=10)
radm_clf.fit(train_X, train_y)

"""**Grid Search for Optimal Parameters**"""

radm_clf = RandomForestClassifier(max_depth=15,
n_estimators=20,
max_features = 'auto')
radm_clf.fit(train_X, train_y)

"""**Drawing the Confusion Matrix**"""

pred_y = radm_clf.predict(test_X)
draw_cm(test_y, pred_y)

print(metrics.classification_report(test_y, pred_y))

"""**Finding Important Features**"""

# Create a dataframe to store the featues and their corresponding importances
feature_rank = pd.DataFrame( { 'feature': train_X.columns,
'importance': radm_clf.feature_importances_ } )

feature_rank = feature_rank.sort_values('importance', ascending = False)
plt.figure(figsize=(8, 6))
# plot the values
sn.barplot( y = 'feature', x = 'importance', data = feature_rank );

feature_rank['cumsum'] = feature_rank.importance.cumsum() * 100
feature_rank.head(10)

"""# **Boosting**

**1) AdaBoost**
"""

from sklearn.ensemble import AdaBoostClassifier
logreg_clf = LogisticRegression()
ada_clf = AdaBoostClassifier(logreg_clf, n_estimators=50)
ada_clf.fit(train_X, train_y)

"""**2) Gradient Boosting**"""

from sklearn.ensemble import GradientBoostingClassifier
gboost_clf = GradientBoostingClassifier(n_estimators=500,
max_depth = 10)
gboost_clf.fit(train_X, train_y)

from sklearn.model_selection import cross_val_score
gboost_clf = GradientBoostingClassifier( n_estimators=500,
max_depth=10)
cv_scores = cross_val_score( gboost_clf, train_X, train_y,
cv = 10, scoring = 'roc_auc' )

print( cv_scores )
print( "Mean Accuracy: ", np.mean(cv_scores), " with standard deviation of: ",
np.std(cv_scores))

gboost_clf.fit(train_X, train_y )
pred_y = gboost_clf.predict( test_X )
draw_cm( test_y, pred_y )

print( metrics.classification_report( test_y, pred_y ) )