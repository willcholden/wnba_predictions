# WNBA Score Predictor
### By William C Holden

## Introduction

The objective of this project was to create a fully automated system that could provide real-time, accurate predictions about the outcomes of WNBA games. This system comprises five separate steps: Web scraping to get WNBA stats, training machine learning models using the stats, making predictions on upcoming games, sending these predictions to my phone for convenience, and automating steps 1-4. Each of the five steps will be explained below. 

As an avid WNBA fan, this project was a blast to complete despite its many challenges. I enjoyed taking the data science techniques I gathered in academic and professional settings and applying them to one of my personal interests. Watching the games has an added layer of tension/excitement when I'm hoping my predictions come true. I hope others can look at this repository and be inspired to find the data science project hidden in their passions. 

## Step 1: Web Scraping

I used the `requests` package[^1] in python to extract data from the internet, seen in the script `get_stats.py`. First, the script will get the team stats (field goal attempts, rebounds, steals, etc) for every WNBA team from 2018 to present day, and store them in the dataframe "teams". All of this information is conveniently available at https://www.basketball-reference.com/. Next, the script will get the final scores from every game played since 2018, and store them in a dataframe called "matchups". Then, the script will join the "teams" dataframe with the "matchups" dataframe by taking the *difference* between two teams' stats for each matchup. For instance, the first row of the joined dataframe, "df", shows the difference in stats between the 2018 Dallas Wings and the 2018 Phoenix Mercury, as well as the point difference in their matchup played on May 18th, 2018. The stats will be used as the features/predictors and the point differences will be used as the targets. Now that all of this data has been collected and saved to a CSV, `matchup_stats.csv`, we can use it to train machine learning models.

## Step 2: Creating ML Models. 

I decided not to create classification predictors that would simply output 1's or 0's for a team winning. Instead, I created some regression models that would estimate the final score difference between two teams given their stats. The way I figure, if the predicted score difference is large (> 10 points), the model must be confident that one team will dominate the other. These models are created in the script `create_model.py`.

I decided to create three separate models, namely linear regression, ridge regression, and lasso regression[^2]. This is because I don't want to make any assumptions about colinearity and independence among features. For ridge and lasso, I performed a grid search for optimal values of alpha using some recommended values I found online. For each of the three models I used R2 as an accuracy metric on test data to make sure the models were generalizeable. 

## Step 3: Making Predictions

Once all three models are trained and scored, they can be used to predict the scores for upcoming games. The matchup_stats dataframe contains a column "date" which can be used to find out when the next games will take place. Using the datetime package[^3] in python, I can search the dataframe for games taking place the day of and the day after execution of the program. 

If the search shows that there are any games being played soon, the stats from the opposing teams are extracted, subtracted from one another, and scaled so they can be input to the predictors. The predictions made by the linear, ridge, and lasso models are stored in a text file, `message_body.txt`. 

## Step 4: Sending Messages

For convenience, I wanted the predictions for each upcoming match to be sent directly from my machine to my cellphone. This can be accomplished using the SMTP protocol client[^4] as seen in my script `send_message.py`. This library allows a user to send mail to any machine connected to the internet. In the case of this project, I sent messages through an email gateway connected to my phone so that I could get text updates. Reading the text file `message_body.txt`, the message sending program will send one text per game which includes the date of the game, the two competing teams, and the predicted score from all three regression models, as well as each model's R2 score. A screenshot from my text bot can be seen below: 

![text example](https://github.com/willcholden/wnba_predictions/blob/main/text_example.PNG)

## Step 5: Automation

![raspberry pi](https://github.com/willcholden/wnba_predictions/blob/main/raspberry_pi.HEIC)

It would be a hassle to boot up my computer each morning and run all these scripts one by one. To avoid this, I figured out a way to automate the process using a Raspberry Pi 4[^5]. The Raspberry Pi is a simple computer that draws very little power- the average power consumption while idle is 4W. For comparison, the average low-power LED light bulb draws 10W of power. Once I cloned all of my python scripts to the Pi, I created a cron[^6] job to schedule the scripts to run each morning. Finally, I wrote a shell script to ensure that the Pi is connected to the internet, `check_wifi.sh`, or else the system would fail to scrape the web and send messages via SMTP. 

![cron job](https://github.com/willcholden/wnba_predictions/blob/main/cron_job.png)





[^1]: https://pypi.org/project/requests/
[^2]: https://scikit-learn.org/stable/modules/linear_model.html
[^3]: https://docs.python.org/3/library/datetime.html
[^4]: https://docs.python.org/3/library/smtplib.html
[^5]: https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
[^6]: https://www.redhat.com/sysadmin/linux-cron-command
