import sys
import os
import json
from datetime import datetime, timezone

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY") or os.getenv("MONGO_DB_URL")
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, Form, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.url_features import extract_url_features
from networksecurity.utils.ml_utils.explainability import explain_prediction


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca, serverSelectionTimeoutMS=2000)

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]
history_collection = database["URLScans"]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
def _risk_band(phishing_probability: float) -> str:
    if phishing_probability >= 0.75:
        return "high"
    if phishing_probability >= 0.4:
        return "medium"
    return "low"


def _save_scan(scan):
    try:
        history_collection.insert_one(scan.copy())
    except Exception:
        history_path = "prediction_output/scan_history.jsonl"
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        with open(history_path, "a") as history_file:
            history_file.write(json.dumps(scan) + "\n")


@app.post("/predict")
async def predict_route(
    request: Request,
    url: str = Form(default=""),
    file: UploadFile = File(default=None),
):
    try:
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        if url.strip():
            df = extract_url_features(url)
            prediction = int(network_model.predict(df)[0])
            if hasattr(final_model, "predict_proba"):
                probabilities = final_model.predict_proba(preprocesor.transform(df))[0]
                class_probabilities = dict(zip(final_model.classes_, probabilities))
                phishing_probability = float(class_probabilities.get(0, 1 - max(probabilities)))
            else:
                phishing_probability = 1.0 if prediction == 0 else 0.0
            scan = {
                "url": url.strip(),
                "prediction": "phishing" if prediction == 0 else "legitimate",
                "phishing_probability": round(phishing_probability, 4),
                "risk": _risk_band(phishing_probability),
                "explanation": explain_prediction(final_model, preprocesor, df),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            }
            _save_scan(scan)
            return templates.TemplateResponse(request=request, name="index.html", context={"result": scan})

        if file is None:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={"error": "Enter a URL or upload a feature CSV."},
            )
        df = pd.read_csv(file.file)
        y_pred = network_model.predict(df)
        df['predicted_column'] = y_pred
        df.to_csv('prediction_output/output.csv', index=False)
        table_html = df.to_html(classes='table table-striped', index=False)
        return templates.TemplateResponse(request=request, name="table.html", context={"table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)


@app.get("/explain")
async def explain_route(url: str):
    try:
        preprocessor = load_object("final_model/preprocessor.pkl")
        model = load_object("final_model/model.pkl")
        features = extract_url_features(url)
        explanation = explain_prediction(model, preprocessor, features)
        prediction = int(model.predict(preprocessor.transform(features))[0])
        return {
            "url": url,
            "prediction": "phishing" if prediction == 0 else "legitimate",
            "explanation": explanation,
        }
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.get("/history")
async def scan_history():
    try:
        return {"scans": list(history_collection.find({}, {"_id": 0}).sort("scanned_at", -1).limit(100))}
    except Exception:
        history_path = "prediction_output/scan_history.jsonl"
        if not os.path.exists(history_path):
            return {"scans": []}
        with open(history_path) as history_file:
            scans = [json.loads(line) for line in history_file if line.strip()]
        return {"scans": list(reversed(scans[-100:]))}


@app.get("/metrics")
async def model_metrics():
    metrics_path = "final_model/evaluation.json"
    if not os.path.exists(metrics_path):
        return {"message": "Train a model first."}
    with open(metrics_path) as metrics_file:
        return json.load(metrics_file)

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)
