import sys
import os
import time
import json
import joblib
from datetime import datetime, timezone
import pandas as pd

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.responses import Response

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.url_features import extract_url_features
from networksecurity.utils.ml_utils.pure_url_features import extract_pure_static_features, extract_pure_static_dataframe
from networksecurity.utils.ml_utils.explainability import explain_prediction
from networksecurity.utils.ml_utils.secure_llm_reasoning import SecureLLMReasoningPipeline

try:
    import certifi
    ca = certifi.where()
except Exception:
    ca = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

mongo_db_url = os.getenv("MONGODB_URL_KEY") or os.getenv("MONGO_DB_URL")
client = None
database = None
collection = None
history_collection = None

try:
    import pymongo
    if mongo_db_url:
        if ca:
            client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca, serverSelectionTimeoutMS=2000)
        else:
            client = pymongo.MongoClient(mongo_db_url, serverSelectionTimeoutMS=2000)
        from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
        from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME
        database = client[DATA_INGESTION_DATABASE_NAME]
        collection = database[DATA_INGESTION_COLLECTION_NAME]
        history_collection = database["URLScans"]
except Exception as mongo_err:
    client = None
    history_collection = None

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
        from networksecurity.pipeline.training_pipeline import TrainingPipeline
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
    if history_collection is not None:
        try:
            history_collection.insert_one(scan.copy())
            return
        except Exception:
            pass
    history_path = "prediction_output/scan_history.jsonl"
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(history_path, "a") as history_file:
        history_file.write(json.dumps(scan) + "\n")


@app.post("/predict")
async def predict_route(
    request: Request,
    url: str = Form(default=""),
    api_key: str = Form(default=""),
    llm_provider: str = Form(default="auto"),
    file: UploadFile = File(default=None),
):
    try:
        preprocesor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)

        if url.strip():
            target_url = str(url).strip()
            key_str = str(api_key).strip() if isinstance(api_key, str) else ""
            prov_str = str(llm_provider).strip() if isinstance(llm_provider, str) else "auto"

            t0 = time.time()
            pure50 = extract_pure_static_features(target_url)
            latency_ms = (time.time() - t0) * 1000

            df30 = extract_url_features(target_url)
            base_pred = int(network_model.predict(df30)[0])
            if hasattr(final_model, "predict_proba"):
                base_probs = final_model.predict_proba(preprocesor.transform(df30))[0]
                base_class_map = dict(zip(final_model.classes_, base_probs))
                base_phish_prob = float(base_class_map.get(0, 1.0 - max(base_probs)))
            else:
                base_phish_prob = 1.0 if base_pred == 0 else 0.0

            # SOTA Stacking Prediction
            if os.path.exists("final_model/sota_stacking_model.pkl") and os.path.exists("final_model/sota_feature_selector.pkl"):
                sota_clf = joblib.load("final_model/sota_stacking_model.pkl")
                sota_sel = joblib.load("final_model/sota_feature_selector.pkl")
                X_sel = sota_sel.transform(df30)
                sota_pred_raw = int(sota_clf.predict(X_sel)[0])
                sota_probs = sota_clf.predict_proba(X_sel)[0]
                sota_class_map = dict(zip(sota_clf.classes_, sota_probs))
                sota_phish_prob = float(sota_class_map.get(0, 1.0 - max(sota_probs)))
                sota_pred = "phishing" if (sota_pred_raw == 0 or sota_phish_prob >= 0.5) else "legitimate"
            else:
                sota_pred = "phishing" if base_pred == 0 else "legitimate"
                sota_phish_prob = base_phish_prob

            explanation = explain_prediction(final_model, preprocesor, df30)
            top_shap_features = [f["feature"] for f in explanation.get("features", [])]

            # LLM Forensics with Live Provider / Fallback
            llm_pipeline = SecureLLMReasoningPipeline()
            sanitization = llm_pipeline.sanitize_input(target_url)
            evidence_packet = llm_pipeline.assemble_evidence_packet(
                url=target_url,
                prediction_label=sota_pred,
                confidence=sota_phish_prob if sota_pred == "phishing" else (1.0 - sota_phish_prob),
                top_shap_features=top_shap_features,
                top_lime_features=explanation.get("features", [])
            )
            system_prompt, user_prompt = llm_pipeline.format_llm_prompts(evidence_packet)
            llm_res = llm_pipeline.call_live_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                api_key=key_str if key_str else None,
                provider=prov_str
            )

            if llm_res.get("live_call") and llm_res.get("raw_output"):
                parsed = llm_pipeline.validate_and_parse_response(llm_res["raw_output"])
                report_dict = parsed.get("report") or parsed.get("fallback_report")
                report_dict["provider"] = llm_res["provider"]
            else:
                narrative = (
                    f"Automated SOC Triage: Target '{target_url}' classified as {sota_pred.upper()} "
                    f"with {sota_phish_prob*100:.1f}% threat confidence by Optuna Stacking Ensemble. "
                    f"Dominant risk indicators: {', '.join(top_shap_features[:3])}."
                )
                if sanitization["injection_flagged"]:
                    narrative += " [WARNING: Adversarial prompt injection syntax was quarantined]."
                report_dict = {
                    "analyst_explanation": narrative,
                    "risk_level": evidence_packet["risk_level"],
                    "recommended_action": "Block URL at perimeter gateway and isolate destination endpoint." if sota_pred == "phishing" else "Allow access and log for monitoring.",
                    "uncertainty_flag": evidence_packet["uncertainty_flag"],
                    "provider": llm_res["provider"]
                }

            scan = {
                "url": target_url,
                "prediction": sota_pred,
                "phishing_probability": round(sota_phish_prob, 4),
                "sota_prediction": sota_pred,
                "sota_probability": round(sota_phish_prob, 4),
                "baseline_prediction": "phishing" if base_pred == 0 else "legitimate",
                "baseline_probability": round(base_phish_prob, 4),
                "risk": _risk_band(sota_phish_prob),
                "telemetry": {
                    "domain_entropy": round(float(pure50.get("domain_entropy", 0.0)), 3),
                    "complexity_score": round(float(pure50.get("url_complexity_score", 0.0)), 2),
                    "homoglyph_flag": bool(pure50.get("is_punycode", 0) or pure50.get("char_diversity", 1.0) < 0.25),
                    "latency_ms": round(latency_ms, 2),
                    "injection_flagged": sanitization["injection_flagged"]
                },
                "pure_50_features": {k: round(v, 4) if isinstance(v, float) else v for k, v in pure50.items()},
                "llm_report": report_dict,
                "explanation": explanation,
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            }
            _save_scan(scan)
            return templates.TemplateResponse(request=request, name="index.html", context={"result": scan, "request_url": target_url, "api_key": api_key})

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
        raise NetworkSecurityException(e, sys)


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


@app.get("/pure-features")
async def pure_features_route(url: str):
    """Extract 50 pure static, zero-network features without dummy zeros."""
    try:
        features = extract_pure_static_features(url)
        return {
            "url": url,
            "feature_count": len(features),
            "features": features
        }
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.get("/incident-report")
async def incident_report_route(url: str, api_key: str = "", provider: str = "auto"):
    """
    Generate an evidence-grounded incident report.
    Integrates model prediction, SHAP feature attributions, and prompt-injection defense.
    Supports real LLM call (Groq, Gemini, OpenAI, Ollama) if api_key is provided or set in env.
    """
    try:
        pipeline = SecureLLMReasoningPipeline()
        sanitization = pipeline.sanitize_input(url)

        preprocessor = load_object("final_model/preprocessor.pkl")
        model = load_object("final_model/model.pkl")
        features = extract_url_features(url)
        explanation = explain_prediction(model, preprocessor, features)
        prediction = int(model.predict(preprocessor.transform(features))[0])

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(preprocessor.transform(features))[0]
            confidence = float(max(probs))
        else:
            confidence = 0.95

        pred_label = "phishing" if prediction == 0 else "legitimate"
        top_shap_features = [f["feature"] for f in explanation.get("features", [])]

        evidence_packet = pipeline.assemble_evidence_packet(
            url=url,
            prediction_label=pred_label,
            confidence=confidence,
            top_shap_features=top_shap_features,
            top_lime_features=explanation.get("features", [])
        )

        system_prompt, user_prompt = pipeline.format_llm_prompts(evidence_packet)

        # Call real live LLM or fallback
        llm_res = pipeline.call_live_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key.strip() if api_key.strip() else None,
            provider=provider
        )

        if llm_res.get("live_call") and llm_res.get("raw_output"):
            parsed = pipeline.validate_and_parse_response(llm_res["raw_output"])
            report_dict = parsed.get("report") or parsed.get("fallback_report")
            report_dict["provider"] = llm_res["provider"]
        else:
            analyst_narrative = (
                f"Automated Triage: URL '{url}' flagged as {pred_label.upper()} with {confidence*100:.1f}% confidence. "
                f"Key risk drivers include: {', '.join(top_shap_features[:3])}."
            )
            if sanitization["injection_flagged"]:
                analyst_narrative += " WARNING: Input exhibits adversarial prompt injection syntax."

            report_dict = {
                "analyst_explanation": analyst_narrative,
                "risk_level": evidence_packet["risk_level"],
                "recommended_action": "Block URL at perimeter and revoke associated active tokens." if pred_label == "phishing" else "Permit access and monitor.",
                "uncertainty_flag": evidence_packet["uncertainty_flag"],
                "provider": llm_res["provider"]
            }

        return {
            "evidence_packet": evidence_packet,
            "validated_incident_report": report_dict,
            "llm_provider": llm_res["provider"],
            "live_call": llm_res.get("live_call", False),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
    except Exception as e:
        raise NetworkSecurityException(e, sys)


    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)
