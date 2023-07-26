<br />
<div align="center">

  <h2 align="center">Indic Agro Advisory using PaLM API and Bhashini</h2>

  <p align="center">
    Streamlit-powered decision support tool for Indian farmers in 14 different Indic languages.
  </p>
    <a href="https://github.com/dnezan/streamlit-hyperspectral-agri">
    <img src="./img/banner.png" alt="Logo">
</div>
</br>

*The project is still work in progress, see the [disclaimer below](#status).*

## Installation

Pip install all the package including in *requirements.txt* in a Python>=3.8 environment.
```sh
git clone https://github.com/dnezan/indic-agro-advisory
pip install requirements.txt
```
Make sure to add your **PaLM API** key as well as your **BHASHINI MeitY API** key as Streamlit Secrets if you are deploying on Streamlit Community Cloud. You can also use Azure Key Vault if you are deploying on Azure.

_config.py_
```python
secret = dict(
    palm_api_key = **********,
    bhashini_api_key = **********
)
```

Replace your credentials as a **Secret** in TOML format.
```toml
json_data = { 
    "type": "service_account",
    "project_id": "****",
    "private_key_id": "****",
    "private_key": "****",
    "client_email": "****.iam.gserviceaccount.com",
    "client_id": "****",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "****",
    "universe_domain": "googleapis.com"
     }

service_account = '****.iam.gserviceaccount.com'
```

## Why?

Good question.

![screen](./img/screenshot.png)
