from flask import Flask, render_template, request, url_for, flash, redirect 
import joblib
import re
from nltk.corpus import stopwords
import nltk

# Download stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

app = Flask(__name__)

# Load models and vectorizer
nb_model = joblib.load('models/naive_bayes_model.pkl')
lr_model = joblib.load('models/logistic_regression_model.pkl')
rf_model = joblib.load('models/random_forest_model.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')

# Function to clean text
def clean_text(text):
    text = re.sub(r'\W', ' ', text)
    text = text.lower()
    text = text.split()
    text = [word for word in text if word not in stop_words]
    return ' '.join(text)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@app.route('/about')
def about():
    return render_template('about.html')

app.secret_key = 'supersecretkey'  # ✅ REQUIRED for flash messages

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Example message handling (you can replace this with your logic)
        if not name or not email or not message:
            flash('Please fill out all fields. ⚠️', 'error')
        else:
            flash('Your message has been sent successfully! ', 'success')

        return redirect(url_for('contact'))

    return render_template('contact.html')



@app.route('/predict', methods=['POST'])
def predict():
    message = request.form['message']
    cleaned_message = clean_text(message)
    data = vectorizer.transform([cleaned_message])
    
    # Predict using all models
    prediction_nb = nb_model.predict(data)[0]
    prediction_lr = lr_model.predict(data)[0]
    prediction_rf = rf_model.predict(data)[0]

    result_nb = 'Spam' if prediction_nb == 1 else 'Not Spam'
    result_lr = 'Spam' if prediction_lr == 1 else 'Not Spam'
    result_rf = 'Spam' if prediction_rf == 1 else 'Not Spam'

    results = {
        'Naive Bayes': result_nb,
        'Logistic Regression': result_lr,
        'Random Forest': result_rf
    }

    # 🧠 Majority Voting
    spam_count = [result_nb, result_lr, result_rf].count('Spam')
    final_verdict = 'Spam' if spam_count >= 2 else 'Not Spam'

    return render_template(
        'result.html',
        result=results,
        final_verdict=final_verdict,
        message=message
    )


if __name__ == '__main__':
    app.run(debug=True)