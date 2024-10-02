from flask import Flask, request, jsonify ,render_template
import pandas as pd
import tensorflow as tf

app = Flask(__name__)

# Load the trained model
model = tf.keras.models.load_model('student_score_model.h5')
data_prd = pd.read_csv("students_encoded.csv")

# Replace 'means' and 'std_devs' with your actual values used during normalization
means = {
    'Hours_Studied': data_prd['Hours_Studied'].mean(),
    'Attendance': data_prd['Attendance'].mean(),
    'Parental_Involvement': data_prd['Parental_Involvement'].mean(),
    'Access_to_Resources': data_prd['Access_to_Resources'].mean(),
    'Previous_Scores': data_prd['Previous_Scores'].mean(),
    'Tutoring_Sessions': data_prd['Tutoring_Sessions'].mean()
}

std_devs = {
    'Hours_Studied': data_prd['Hours_Studied'].std(),
    'Attendance': data_prd['Attendance'].std(),
    'Parental_Involvement': data_prd['Parental_Involvement'].std(),
    'Access_to_Resources': data_prd['Access_to_Resources'].std(),
    'Previous_Scores': data_prd['Previous_Scores'].std(),
    'Tutoring_Sessions': data_prd['Tutoring_Sessions'].std()
}

def predict_exam_score(hours_studied, attendance, parental_involvement, access_to_resources,
                       previous_scores, tutoring_sessions):
    
    # Convert inputs to float
    hours_studied = float(hours_studied)
    attendance = float(attendance)
    parental_involvement = float(parental_involvement)
    access_to_resources = float(access_to_resources)
    previous_scores = float(previous_scores)
    tutoring_sessions = float(tutoring_sessions)
    
    # Create a DataFrame to hold the input features
    input_data = pd.DataFrame({
        'Hours_Studied': [hours_studied],
        'Attendance': [attendance],
        'Parental_Involvement': [parental_involvement],
        'Access_to_Resources': [access_to_resources],
        'Previous_Scores': [previous_scores],
        'Tutoring_Sessions': [tutoring_sessions],
    })
    
    # Normalize the data (assuming you used normalization during training)
    input_data_standardized = (input_data - pd.Series(means)) / pd.Series(std_devs)
    
    # Predict the exam score
    predicted_score = model.predict(input_data_standardized)
    return predicted_score.flatten()[0]

@app.route('/')
def home():
    # Render the HTML form when the root URL is accessed
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Extract the input data from the request
        hours_studied = data.get('Hours_Studied')
        attendance = data.get('Attendance')
        parental_involvement = data.get('Parental_Involvement')
        access_to_resources = data.get('Access_to_Resources')
        previous_scores = data.get('Previous_Scores')
        tutoring_sessions = data.get('Tutoring_Sessions')
        
        # Predict the score using the predict_exam_score function
        predicted_score = predict_exam_score(hours_studied, attendance, parental_involvement, access_to_resources,
                                            previous_scores, tutoring_sessions)
        
        # Convert the predicted score to a Python float to ensure it's JSON serializable
        predicted_score = float(predicted_score)

        if predicted_score > 100.00:
             predicted_score = 100.00

        predicted_score = round(predicted_score, 2)

        # Return the prediction as a JSON response
        return jsonify({'predicted_score': predicted_score})

    except Exception as e:
            print(f"Error occurred: {e}")
            return jsonify({'error': 'Something went wrong on the server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
