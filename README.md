### Network Security Projects For Phising Data

Setup github secrets:
AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_REGION = us-east-1

AWS_ECR_LOGIN_URI = 788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity
ECR_REPOSITORY_NAME = networkssecurity

Docker Setup In EC2 commands to be Executed
#optinal

sudo apt-get update -y

sudo apt-get upgrade

#required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker

## URL scanning workflow

This project trains a phishing URL classifier and serves it with FastAPI. After dependencies are installed, run:

```bash
uvicorn app:app --reload
```

Open `http://localhost:8000/` to paste a raw URL. The service derives the 30 features used by the training dataset, predicts phishing or legitimate, assigns a low/medium/high risk band, and shows the most influential model features. Scans are stored in MongoDB when available and fall back to `prediction_output/scan_history.jsonl`.

The API also provides:

- `POST /predict`: raw URL form submission, or the existing feature CSV upload.
- `GET /history`: the latest saved scans.
- `GET /metrics`: model comparison, cross-validation, test metrics, and confusion matrix from the latest training run.
- `GET /train`: runs ingestion, validation, transformation, tuning, and model training.

The trainer compares Logistic Regression, Decision Tree, Random Forest, AdaBoost, and Gradient Boosting with hyperparameter search and stratified cross-validation. Metrics are saved to `final_model/evaluation.json`. Set `MLFLOW_TRACKING_URI` and related credentials through environment variables to enable MLflow tracking; credentials should not be committed to source code.
