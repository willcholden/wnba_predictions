# %%
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge, LinearRegression, Lasso
from sklearn.preprocessing import StandardScaler 
from datetime import datetime, timedelta
from sklearn.model_selection import GridSearchCV
import sklearn.metrics
import warnings

warnings.filterwarnings('ignore')

# %%
df = pd.read_csv('/home/pi/wnba_predictions/matchup_stats.csv')
prev_matchups = df[df['pts_d'] != 0]

column_names = df.columns.values[2:24]

y = prev_matchups['pts_d'].to_numpy()
X = prev_matchups.to_numpy()[:,2:24]

# X_sq = np.square(np.abs(X)) * np.sign(X)
# X_rt = np.sqrt(np.abs(X).astype(float)) * np.sign(X)


# X_tot = np.hstack((X, X_sq, X_rt))


# %%
scaler = StandardScaler() 
scaled_X = scaler.fit_transform(X) 
  
X_train, X_test, y_train, y_test = train_test_split(scaled_X, 
                                                    y, 
                                                    test_size = 0.2) 


# %%
RidgeRegression = Ridge()
hyperParameters = {'alpha':[1e-15,1e-10,1e-8,1e-3,1e-2,1,5,10,20,30,35,40,45,50,55,100]}
ridgeRegressor = GridSearchCV(RidgeRegression, hyperParameters, scoring='r2', cv=5)
ridgeRegressor.fit(X_train,y_train)

# print("Best value for lambda : ",ridgeRegressor.best_params_)
# print("Best score for cost function: ", ridgeRegressor.best_score_)

rdg=ridgeRegressor.best_estimator_
rdg_score=rdg.score(X_test, y_test)
# print("Model score: ", rdg_score, "\n")

# for i in range(0, 22):
#     print(column_names[i], ": ", rdg.coef_[i])

# %%


# %%
LassoRegression = Lasso(tol=1e-2, max_iter=10000)
hyperParameters = {'alpha':[1e-15,1e-10,1e-8,1e-3,1e-2,1,5,10,20,30,35,40,45,50,55,100]
                   }
LassoRegressor = GridSearchCV(LassoRegression, hyperParameters, scoring='r2', cv=5)
LassoRegressor.fit(X_train, y_train)

# print("Best value for lambda : ",LassoRegressor.best_params_)
# print("Best score for cost function: ", LassoRegressor.best_score_)

lso=LassoRegressor.best_estimator_
lso_score=lso.score(X_test, y_test)
# print("Model score: ", lso_score, "\n")

# for i in range(0, 22):
#     print(column_names[i], ": ", lso.coef_[i])

# %%
lin = LinearRegression() 
lin.fit(X_train, y_train) 
y_pred = lin.predict(X_test)
lin_score = lin.score(X_test, y_test) 
# print("Model score : ", lin_score, "\n")

# for i in range(0, 22):
#     print(column_names[i], ": ", lin.coef_[i])

# %%
def isWin(team_a, team_b, pts_d):
    if pts_d > 0:
        outp = team_a + ">" + team_b + " | " + str(round(pts_d, 1))
    else:
        outp = team_b + ">" + team_a + " | " + str(round(abs(pts_d), 1))
    return(outp)

# %%
models = [lin, rdg, lso]
s = '-'*50

today_dt=datetime.today() - timedelta(days=1)
today = today_dt.strftime("%a, %b %d, %Y")

with open('/home/pi/wnba_predictions/message_body.txt', 'w') as the_file:
    for _ in range(0, 2):
        today_dt += timedelta(days=1)
        today = today_dt.strftime("%a, %b %d, %Y")
        today_header = today + "\n"
        home_teams=df[df['date']==today]['team_a'].to_list()
        visitor_teams=df[df['date']==today]['team_b'].to_list()
        

        

        try:
            X_today=df[df['date']==today].drop(['pts_d', 'mp_per_g', 'date', 'team_a', 'team_b'], axis=1).to_numpy()[:,1:]
            X_today_scaled = scaler.transform(X_today)

            for j in range(0, len(home_teams)):
                print(today_header)
                the_file.write(today_header)
                

                for model in models:
                    prediction_text = isWin(home_teams[j], visitor_teams[j], model.predict(X_today_scaled)[j])
                    print(prediction_text)
                    the_file.write(prediction_text)

                    model_header = " (" + str(model)[:3] + ", r2=" + str(round(model.score(X_test, y_test), 3)) + ")\n"
                    print(model_header)
                    the_file.write(model_header)
                
                the_file.write("***\n")
                
        except:
            print("No games on ", today)

