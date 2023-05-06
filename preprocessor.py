import re
import pandas as pd
import nltk
nltk.downloader.download('vader_lexicon')
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

def preprocess(data):
    pattern = r"\d{2}/\d{2}/\d{2}, \d{2}:\d{2}\u202f[ap]m -"
    dates = re.findall(pattern, data)
    messages = re.split(pattern, data)[1:]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # separate users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    pattern = r'^(\d{2}/\d{2}/\d{2}),\s(\d{2}:\d{2})\s(am|pm)\s-$'

    # Define a function to clean the date strings using regex
    def clean_date(date_string):
        # Use regex to extract the relevant parts of the date string
        match = re.search(pattern, date_string)
        if match:
            # Extract the date, time, and am/pm components from the match object
            date = match.group(1)
            time = match.group(2)
            am_pm = match.group(3)
            # Convert the 12-hour time format to 24-hour format
            if am_pm == 'pm':
                hour = int(time.split(':')[0]) + 12
                time = str(hour) + time[2:]
            # Combine the cleaned date and time components into a single string
            cleaned_date = date + ' ' + time
            return cleaned_date
        else:
            # If the regex pattern doesn't match, return NaN
            return pd.NaT

    # Clean the dates in the 'date' column using the clean_date() function
    cleaned_dates = df['date'].apply(clean_date)

    df[['FDate', 'FTime']] = cleaned_dates.str.split(' ', n=1, expand=True)

    time = df['FDate']

    # use regular expressions to split the date into year, month, and day columns
    df[['day', 'month', 'year']] = df['FDate'].str.extract(r'^(\d{2})/(\d{2})/(\d{2})$')

    # convert the month from a number to a name
    month_dict = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                  '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    df['month'] = df['month'].map(month_dict)

    df[['hour', 'minute']] = df['FTime'].str.extract(r'^(\d{2}):(\d{2})$')



    return df
