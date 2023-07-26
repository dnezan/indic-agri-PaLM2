<br />
<div align="center">

  <h2 align="center">Indic Agro Advisory using PaLM API and BHASHINI</h2>

  <p align="center">
    Streamlit-powered decision support tool for Indian farmers in 14 different Indic languages, converting spoken word prompts to auditory information sourced from a large vector database.
  </p>
    <a href="https://github.com/dnezan/streamlit-hyperspectral-agri">
    <img src="./img/banner.png" alt="Logo">
</div>
</br>

*The project is still work in progress, see the [disclaimer below](#status).*

![screen](./img/screenshot.png)

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
    BHASHINI_api_key = **********
)
```

## Why not just use GPT 4?

Good question.

PaLM 2 is a powerful new language model that has the potential to compete with GPT-4 and help Google in the AI race.

PaLM 2 is a newer model than GPT-4, and it has been trained on a larger dataset of text and code. This means that PaLM 2 has the potential to be more powerful and versatile than GPT-4.
PaLM 2 is also open source, which means that it is available to anyone to use and improve. 

## Language Support

Let us examine the capabilities of our proposed pipeline using PaLM 2 + BHASHINI.

| Indic Language | GPT4 | PaLM 2  | PaLM 2 + BHASHINI |
|---|---|---|---|
| English | 🟢 | 🟢 | 🟢 |
| Bengali | 🟢 | 🟢 | 🟢 |
| Bodo |  |  | 🟢 |
| Assamese | 🟢 |  | 🟢 |
| Gujarati | 🟢 | 🟢 | 🟢 |
| Hindi | 🟢 |  | 🟢 |
| Kannada | 🟢 |  | 🟢 |
| Malayalam | 🟢 |  | 🟢 |
| Manipuri | 🟢 |  | 🟢 |
| Marathi | 🟢 | 🟢 | 🟢 |
| Oriya | 🟢 |  | 🟢 |
| Punjabi | 🟢 |  | 🟢 |
| Tamil | 🟢 | 🟢 | 🟢 |
| Telegu | 🟢 | 🟢 | 🟢 |
| Urdu | 🟢 |  | 🟢 |

We can also compare the performance of Whisper API vs BHASHINI API when it comes to Automatic Speech Recognition (speech to text) applications. BHASHINI supports 14 Indic languages while Whisper API only 5 - English, Hindi, Kannada, Marathi, Tamil, and Urdu.

This makes the BHASHINI-PaLM 2-BHASHINI pipeline a powerful open-source competitor when considering the closed source alternative using GPT and Whisper.
