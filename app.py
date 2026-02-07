from flask import Flask, request, jsonify
import joblib
import pandas as pd
# -------------------------------
# Create Flask App
# -------------------------------
app = Flask(__name__)
# -------------------------------
# Load Saved Model + Preprocessor
# -------------------------------

with open('model.pkl','rb') as f:
    model = joblib.load(f)
with open('preprocessor.pkl','rb') as f:
    preprocessor = joblib.load(f)

# -------------------------------
# Feature Engineering Function
# -------------------------------
def transform_input(data):

    # Convert JSON → DataFrame
    df = pd.DataFrame([data])

    # -------- Remove unwanted columns ----------
    df['diff_new_old_org']=df['newbalanceOrig']-df['oldbalanceOrg']
    df['diff_new_old_Dest']=df['newbalanceDest']-df['oldbalanceDest']
    df.drop(['newbalanceOrig','newbalanceDest'],axis=1,inplace=True)

    if 'isFlaggedFraud'in df.columns:
         df.drop(['isFlaggedFraud'],axis=1,inplace=True)   
    if 'nameOrig'in df.columns:
         df.drop(['nameOrig'],axis=1,inplace=True)   
    if 'nameDest'in df.columns:
         df.drop(['nameDest'],axis=1,inplace=True)   
    return df
# -------------------------------
# Home Route
# -------------------------------
@app.route("/")
def home():
    return "Flask Model API Running"


# -------------------------------
# Prediction Route
# -------------------------------
@app.route("/predict", methods=["POST"])
def predict():

    try:
        # Step 1 → Get JSON input
        data = request.get_json()

        # Step 2 → Feature Engineering
        df = transform_input(data)

        # Step 3 → Apply Preprocessing
        processed = preprocessor.transform(df)

        # Step 4 → Model Prediction
        prediction = model.predict(processed)[0]
        
        result = 'Yes' if int(prediction) == 1 else 'No'

        return jsonify({"prediction": result})

    except Exception as e:
        return jsonify({"error": str(e)})