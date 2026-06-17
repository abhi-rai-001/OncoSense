# Project Analysis: Cancer Drug Prediction System

## 1. Project Overview
This project is a full-stack bio-informatics application. It leverages **CaDRReS (Cancer Drug Response prediction using a Recommender System)**, an advanced Machine Learning framework, to predict how specific cancer cell lines respond to various pharmaceutical drugs.

### How It Works:
1. **The Machine Learning Core (CaDRReS):**
   - The original framework is written in Python 2.7 (and Python 3 compatible in many cases). It uses **Matrix Factorization**—a technique commonly used in recommender systems (like Netflix recommending movies)—to match 'cell lines' (patients/tumors) with 'drugs'. 
   - It computes a predicted "IC50" value (Half-maximal inhibitory concentration) which represents how much of a drug is needed to inhibit biological processes by 50%.
2. **The Web Application (FlaskApp):**
   - A modern Python 3.11 web app built with **Flask**. 
   - It operates on the pre-computed predictions outputted by the CaDRReS model (`ccle_all_pred_end.csv`). 
   - Users interact with a web interface where they can select a **Cell Line** and a **Drug**, and provide a custom **sensitivity threshold**.
   - The app dynamically determines whether the cell line is **Sensitive** or **Resistant** to the chosen drug and visualizes statistics. Users can also download reports (CSVs) of sensitive/resistant cell lines.

---

## 2. Detailed Technical Analysis
- **Architecture:** The system follows a decoupled architecture. The heavy lifting (ML training and predicting) is performed offline by CaDRReS, generating static CSVs. This allows the Flask app to remain lightweight and highly responsive.
- **Frontend/Backend:** The Flask backend (`app.py`) parses `pandas` DataFrames, and utilizes basic Jinja2 templating (`index.html`, `result.html`) with basic interactivity to render data and visual counts.
- **Performance:** Since the Flask application uses primarily exact lookups via pandas `df.loc[cell_line, drug]`, response times are virtually instantaneous for the end user.
- **Deployment:** The project includes a `Dockerfile` that packages the Flask application on a lightweight `python:3.11-slim` environment, making the project portable across different OS architectures.

---

## 3. How to Run It

### Method 1: Using Docker (Recommended for simplicity)
You can run the web application easily without modifying your local system using the provided Docker environment.
```bash
# Build the Docker Image from the 'Final Year Project' directory
docker build -t cadrres-flask-app .

# Run the Docker Image
docker run -p 5000:5000 cadrres-flask-app
```
Access the application by going to `http://localhost:5000/` in your web browser.

### Method 2: Running via Python Locally (For developers)
Make sure you have Python 3 installed.
```bash
# 1. Navigate to the project directory
cd "Final Year Project"

# 2. Create and activate a Virtual Environment (Optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# 3. Install the backend dependencies
cd flaskApp
pip install -r requirements.txt

# 4. Start the Flask application
python3 app.py
```
Open your browser and navigate to `http://localhost:5000/`.

*(Note: To train the CaDRReS model itself from scratch, you must navigate to the `CaDRReS-master/scripts` directory and use Python 2.7 as the original model dictates, or upgrade it to Python 3).*

---

## 4. What More Can Be Added (Future Enhancements)

1. **Dynamic Real-Time Predictions:** 
   Currently, the application reads a static, pre-computed `.csv`. You could integrate a Python 3 compatible inference script of the CaDRReS model natively in the Flask app. This would allow users to upload new patient cell-line CSV data dynamically, and the app would generate rapid predictions on the fly.
2. **Interactive Visualizations (Dashboards):**
   Integrate libraries like **Plotly.js** or **D3.js** to show dose-response curves, clustering graphs of drugs, and scatterplots correlating drug sensitivity.
3. **Upgrade Core Algorithm (Single-Cell Data):**
   Implement the newer **CaDRReS-SC** variant. This takes Single-Cell RNA Sequencing (scRNA-seq) data, making your platform cutting-edge and more clinically viable for heterogeneous tumors.
4. **Interactive Feature Engineering UI:**
   Let users modify the genetic features of the chosen cell line via interactive sliders to simulate what happens if a gene is mathematically suppressed or over-expressed.
5. **Report Generation (PDFs):**
   Add functionality via `ReportLab` or `WeasyPrint` to generate clinical-style PDF reports containing drug combinations, resistance risk, and graphical plots.
6. **Robust Database Migration:**
   Move away from static CSVs to a lightweight relational database like **SQLite** or **PostgreSQL** coupled with SQLAlchemy.

---

## 5. Finding More Datasets

The current ecosystem likely relies on **CCLE**. To expand the model, you need large-scale Pharmacogenomics datasets:
- **DepMap (Dependency Map Portal):** Highly reliable datasets from the Broad Institute. It includes updated CCLE data, CRISPR knockout screens, and drug sensitivity data. (https://depmap.org/portal/download/)
- **GDSC (Genomics of Drug Sensitivity in Cancer):** Contains data on thousands of cell lines and hundreds of anti-cancer drugs. Excellent for training cross-platform robustness. (https://www.cancerrxgene.org/)
- **CTRP (Cancer Therapeutics Response Portal):** Provides small-molecule mechanism-of-action data. (https://portals.broadinstitute.org/ctrp/)
- **TCGA (The Cancer Genome Atlas):** Available via the GDC Data Portal. Contains multi-omics primary patient data rather than just in-vitro cell line data. 

---

## 6. Related Topics in Brief

### Artificial Intelligence & Machine Learning (AI / ML)
- **Machine Learning in Biology:** ML focuses on developing algorithms that allow computers to learn patterns from historical data (like gene expressions) without explicit programming. Since biological data is extremely vast (the human genome is millions of variables), ML is essential to filter out the noise and find connections between specific biomarkers and diseases.
- **Recommender Systems (Matrix Factorization):** Originally designed for e-commerce. You have a matrix of generic sizes; Rows are Users (Cell Lines) and Columns are Items (Drugs). A matrix factorization model breaks this large matrix into two smaller, latent-feature sets (one abstractly representing the characteristics of the cell-line, and another the characteristics of the drug). The dot product of these predicts the missing cells (the unknown IC50 drug response).

### Bioinformatics & Pharmacogenomics
- **Pharmacogenomics:** The study of how genes affect a person's response to drugs. This project is a pure pharmacogenomics application because it tries to match the genetic makeup (cell line features) to an individualized, optimized drug therapy.
- **IC50 Calculation:** Stands for half-maximal inhibitory concentration. In simple terms: how much drug do you need to dump onto a cancer cell line to kill 50% of the cells, or inhibit their growth by 50%? A *lower IC50* means the drug is *more potent* (Sensitive). A *higher IC50* means it requires massive amounts of drug to work, rendering it practically useless (Resistant).
- **Overfitting & Generalization in ML:** A massive hurdle in AI bio-medicine. Because there are 20,000+ genes but maybe only 1,000 cell lines, models often try to memorize the exact dataset (overfitting) instead of learning underlying rules. Caching variables into smaller, dense features (like using 10 dimensions in CaDRReS) prevents overfitting.

---

## 7. Key Medical & Technical Vocabulary
To effectively present and explain this project, familiarize yourself with these essential terms:

### Medical & Biological Terms
- **Cell Line:** A population of human/cancer cells extracted from a patient and grown continuously in a laboratory setting. They act as "stand-ins" or "avatars" for real tumors during testing.
- **In vitro vs. In vivo:** *In vitro* means testing done outside a living organism (like in a test tube or using our cell lines). *In vivo* means testing done inside a living organism (like clinical trials in humans). This project focuses on *In vitro* predictions.
- **Biomarker:** A biological molecule found in blood, other body fluids, or tissues that is a sign of a normal or abnormal process, or of a condition or disease (e.g., a specific genetic mutation that makes a tumor vulnerable to a drug).
- **Gene Expression (Transcriptomics / RNA-seq):** A measurement of how "active" specific genes are in a cell. This is the primary feature data the ML model looks at to understand the nature of the cancer.
- **Cytotoxicity / Cellular Toxicity:** The degree to which a substance (the drug) can damage or kill cells (the cancer). 

### Machine Learning & Technical Terms
- **Latent Features / Latent Space:** "Latent" means hidden. Matrix Factorization discovers "hidden" mathematical features that govern how drugs and cells interact, even if we don't know the biological name for that feature.
- **Model Training / Inference:** *Training* is the phase where the CaDRReS algorithm learns from the existing GDSC/CCLE datasets. *Inference* (or testing/prediction) is what the Flask app does: using the learned rules to make a guess about a new, unseen cell line.
- **Features (in ML):** The input variables. In this project, the features are the genetic profiles (mutations, expressions) of the cell lines.
- **Collaborative Filtering:** The broader scientific name for the recommendation technique used here. If Cell Line A is similar to Cell Line B, and Drug X works on Cell Line A, the system "collaboratively" assumes Drug X might work on Cell Line B.

---
*Generated by Antigravity Assistant.*
