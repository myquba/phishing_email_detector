from flask import Flask, render_template, request
import joblib
import pandas as pd
import re
import enchant

# Create a Flask app instance
app = Flask(__name__)

# Load the trained model and TF-IDF vectorizer
model = joblib.load('model/random_forest_model.pkl')
vectorizer = joblib.load('model/tfidf_vectorizer.pkl')

# Process the user input and extract features
def process_input(email_text):
    # Extract features from the user input
    email_length = len(email_text)
    url_count = email_text.lower().count('http')
    email_count = email_text.count('@')
    
    # Keyword count
    keywords = ['urgent', 'account', 'password', 'verify', 'security', 'suspicious']
    keyword_count = sum(email_text.lower().count(keyword) for keyword in keywords)
    
    # Punctuation count
    punctuation_count = sum(email_text.count(punct) for punct in '.,;!?')
    
    # Misspelled words count
    d = enchant.Dict('en_US')
    misspelled_words_count = sum(1 for word in re.findall(r'\w+', email_text) if not d.check(word))
    
    # Subject length and subject keyword count
    subject_pattern = r'Subject: ([^\n]+)'
    match = re.search(subject_pattern, email_text)
    subject = match.group(1) if match else ''
    subject_length = len(subject)
    subject_keyword_count = sum(subject.lower().count(keyword) for keyword in keywords)
    
    # Transform the email text using the TF-IDF vectorizer
    tfidf_features = vectorizer.transform([email_text])
    
    # Convert the features to a DataFrame
    features_df = pd.DataFrame(tfidf_features.toarray())
    features_df['Email Length'] = email_length
    features_df['URL Count'] = url_count
    features_df['Email Count'] = email_count
    features_df['Keyword Count'] = keyword_count
    features_df['Punctuation Count'] = punctuation_count
    features_df['Misspelled Words Count'] = misspelled_words_count
    features_df['Subject Length'] = subject_length
    features_df['Subject Keyword Count'] = subject_keyword_count
    
    return features_df

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for the results page
@app.route('/results', methods=['POST'])
def results():
    if request.method == 'POST':
        # Get the user input
        email_text = request.form['email_text']

        # Explanation text
        if prediction_result == 'Phishing Email':
            explanation = ("This email has been classified as a phishing email. "
                           "Phishing emails are malicious messages that attempt to deceive recipients into disclosing sensitive information, "
                           "such as login credentials or financial information. These emails often contain suspicious links, attachments, "
                           "or requests for personal information. To protect yourself, do not click on any links or download any attachments "
                           "in this email, and avoid providing personal information in response to unsolicited requests.")
        else:
            explanation = ("This email has been classified as a safe email. However, it is always important to stay vigilant and "
                           "exercise caution when interacting with email messages. Avoid clicking on links or downloading attachments "
                           "from unknown senders, and be cautious of requests for personal information.")
        
        # Render the results template with the prediction result and explanation
        return render_template('results.html', prediction_result=prediction_result, explanation=explanation)

        # Process the user input and extract features
        features_df = process_input(email_text)
        
        # Make a prediction
        prediction = model.predict(features_df)
        prediction_result = 'Phishing Email' if prediction[0] == 'phishing' else 'Safe Email'
        
        # Render the results template with the prediction result
        return render_template('results.html', prediction_result=prediction_result)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
