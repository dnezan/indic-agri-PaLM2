import google.generativeai as palm
from streamlit_extras.add_vertical_space import add_vertical_space
import textwrap
import numpy as np
import pandas as pd
import streamlit as st
import os
import time
import math
import geopandas as gpd
import streamlit as st
import geemap.colormaps as cm
import geemap.foliumap as geemap
import os
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import json
from annotated_text import annotated_text
import base64
from streamlit_modal import Modal
import os
import numpy as np
import streamlit as st
from io import BytesIO
import streamlit.components.v1 as components
from os.path import exists
from audiorecorder import audiorecorder
from streamlit_card import card
from annotated_text import annotated_text

from st_custom_components import st_audiorec
import wave

import wave
import pydub

import streamlit.components.v1 as components
import config

import requests
import json
import base64
import streamlit as st

# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

if "load_example" not in st.session_state:
    st.session_state.load_example = 0

if "in_lang" not in st.session_state:
    st.session_state.in_lang = "en"

if "in_lang_sid" not in st.session_state:
    st.session_state.in_lang_sid = ""

if "orig_query" not in st.session_state:
    st.session_state.orig_query = "none"

if "llm_history" not in st.session_state:
    st.session_state.llm_history = " "

def hide_examples():
    st.session_state.load_example += 1

palm_api_key = "AIzaSyA-63D6SrEGAUVKH3b6lDEogLTjs1ddXNE"
bhashini_api_key = 'Mt5dh5Qjr_TtwqpK5uNHGgApAngZjJGDM97-PGlbokBx_-BboOvMckDDOdKD9-VD'

palm.configure(api_key=palm_api_key)


models = [m for m in palm.list_models() if "embedText" in m.supported_generation_methods]

model = models[0]

def mp3_to_wav(mp3_file, wav_file):
  mp3 = pydub.AudioSegment.from_file(mp3_file)
  mp3.export(wav_file, format="wav")

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

#st.set_page_config(layout="wide")
st.set_page_config(layout="wide", initial_sidebar_state=st.session_state.sidebar_state)

st.markdown(
    """
<style>
    header {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-right: 5rem;
        padding-left: 5rem;
    }

    section[data-testid="stSidebar"] {
            width: 500px !important; # Set the width to your desired value
    }
           
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 500px;
        max-width: 500px;
    }

    .css-1iyw2u1 {
        display: none;
        
    }
</style>
""",
    unsafe_allow_html=True,
)



def mp3_to_base64(mp3_file):
  with wave.open(mp3_file, "rb") as mp3:
    mp3_data = mp3.readframes(mp3.getnframes())

  base64_data = base64.b64encode(mp3_data)
  return base64_data.decode("utf-8")

def save_string_to_txt(string, filename):
    with open(filename, "w") as f:
        f.write(string)

def write_dictionary_to_txt(dictionary, filename):
    with open(filename, "w") as f:
        for key, value in dictionary.items():
            f.write(f"{key}: {value}\n")

def find_best_passage(query, dataframe):
    query_embedding = palm.generate_embeddings(
        model=model, text=query
    )
    dot_products = np.dot(
        np.stack(dataframe["Embeddings"]),
        query_embedding["embedding"],
    )
    idx = np.argmax(dot_products)
    return dataframe.iloc[idx][
        "Text"
    ]

def make_prompt(query, relevant_passage):
    escaped = (
        relevant_passage.replace("'", "")
        .replace('"', "")
        .replace("\n", " ")
    )

    engineered_prompt_text = f"""You are a helpful and informative data scientist named AgriTech bot that answers questions using text from the reference passage included below. \
        Be sure to respond in a complete sentence, being comprehensive, including all relevant background information such as citing your source, and answer as elaborately as possible. \
        However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
        strike a friendly and converstional tone while rephrasing your answer so that it is easy to understand.\
        If the passage is irrelevant to the answer, you may ignore it and request that a question related to agriculture is asked.\
        The plot of land of the user is located in India, so answer their questions keeping that in mind.\
        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'
        ANSWER:
        """
# add agricultural scientist

    prompt = textwrap.dedent(engineered_prompt_text).format(
        query=query, relevant_passage=escaped
    )
    return prompt

def embed_fn(text):
    return palm.generate_embeddings(model=model, text=text)["embedding"]

import requests
import json

def bhashini_translate(my_input, input_language, output_language, nmt_serviceid_val):
    url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    payload = json.dumps({
      "pipelineTasks": [
        {
          "taskType": "translation",
          "config": {
            "language": {
              "sourceLanguage": input_language,
              "targetLanguage": output_language
            },
            "serviceId": nmt_serviceid_val
          }
        }
      ],
      "inputData": {
        "input": [
          {
            "source": my_input
          }
        ]
      }
    })
    headers = {
      'Accept': '*/*',
      'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
      'Authorization': bhashini_api_key,
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    output = json_data["pipelineResponse"][0]["output"][0]["target"]
    return output

def bhashini_tts(my_input, input_language, tts_serviceid_val):
    url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    payload = json.dumps({
    "pipelineTasks": [
        {
        "taskType": "tts",
        "config": {
            "language": {
            "sourceLanguage": input_language
            },
            "serviceId": tts_serviceid_val,
            "gender": "female",
            "samplingRate": 8000
        }
        }
    ],
    "inputData": {
        "input": [
        {
            "source": my_input
        }
        ]
    }
    })
    headers = {
    'Accept': '*/*',
    'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
    'Authorization': bhashini_api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    output = json_data["pipelineResponse"][0]["audio"][0]["audioContent"]
    return output

def bhashini_asr(base64_input, input_language, asr_serviceid_val):

    url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    payload = json.dumps({
    "pipelineTasks": [
        {
        "taskType": "asr",
        "config": {
            "language": {
            "sourceLanguage": input_language
            },
            "serviceId": asr_serviceid_val,
            "audioFormat": "wav",
            "samplingRate": 16000
        }
        }
    ],
    "inputData": {
        "audio": [
        {
            "audioContent": base64_input
        }
        ]
    }
    })
    headers = {
    'Accept': '*/*',
    'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
    'Authorization': bhashini_api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    output = json_data["pipelineResponse"][0]["output"][0]["source"]
    return(output)

def draw_examples():
    st.markdown(f"**<font size = 5>Try out these examples!**</font>", unsafe_allow_html=True)
    st.write("How do I protect my millets against pests?")
    st.write("திண்டுக்கல் வானிலை முன்னறிவிப்பு என்ன?")
    st.write("వరి నాట్లు వేయడానికి ఉత్తమ సమయం ఏది?")
    st.write("തിരുവനന്തപുരത്ത് എവിടെ നിന്ന് വളം വാങ്ങാമെന്ന് പറയൂ.")






tagline = "FOR FARMERS IN INDIA"


if st.session_state.in_lang!="en":
    tagline = bhashini_translate(tagline, "en", st.session_state.in_lang, st.session_state.in_lang_sid)

st.markdown(f"<font size=8 color=#4285f4>P</font><font size=8 color=#ea4335>a</font><font size=8 color=#fbbc05>L</font><font size=8 color=#34a853>M</font><font size=6 color=white> + </font> **<font size=8 color=#5473c2>BHASHINI</font> {tagline}**", unsafe_allow_html=True)


col1, col2 = st.columns(2, gap="large")
with col1:
    with st.form("my_form"):
        supported_languages_out_dict = {
                                        "English": "en",
                                        "Assamese": "as",
                                        "Bengali": "bn",
                                        "Bodo": "brx",
                                        "Gujarati": "gu",
                                        "Hindi": "hi",
                                        "Kannada": "kn",
                                        "Malayalam": "ml",
                                        "Manipuri": "mni",
                                        "Marathi": "mr",
                                        "Odia": "or",
                                        "Punjabi": "pa",
                                        "Tamil": "ta",
                                        "Telugu": "te",
                                        "Urdu": "ur"
                                        }
        
        options_list = list(supported_languages_out_dict.keys())

        
        col1_row1, col1_row2 = st.columns(2)
        with col1_row1:
            input_language_option = st.selectbox("Select input language", options_list, key=890)
            input_language = supported_languages_out_dict.get(input_language_option)
            st.session_state.in_lang = input_language
        with col1_row2:
            output_language_option = st.selectbox("Select output language", options_list, key=29, disabled=True)
            output_language = supported_languages_out_dict.get(output_language_option)

        asr_serviceid_dict = {'bn': 'ai4bharat/conformer-multilingual-indo_aryan-gpu--t4', 'en': 'ai4bharat/whisper-medium-en--gpu--t4', 'gu': 'ai4bharat/conformer-multilingual-indo_aryan-gpu--t4', 'hi': 'ai4bharat/conformer-hi-gpu--t4', 'kn': 'ai4bharat/conformer-multilingual-dravidian-gpu--t4', 'ml': 'ai4bharat/conformer-multilingual-dravidian-gpu--t4', 'mr': 'ai4bharat/conformer-multilingual-indo_aryan-gpu--t4', 'or': 'ai4bharat/conformer-multilingual-indo_aryan-gpu--t4', 'pa': 'ai4bharat/conformer-multilingual-indo_aryan-gpu--t4', 'sa': 'ai4bharat/conformer-multilingual-indo_aryan-gpu--t4', 'ta': 'ai4bharat/conformer-multilingual-dravidian-gpu--t4', 'te': 'ai4bharat/conformer-multilingual-dravidian-gpu--t4', 'ur': 'ai4bharat/conformer-multilingual-indo_aryan-gpu--t4'}
        with st.expander("See BHASHINI models", expanded=True):
            try:
                asr_serviceid_val = asr_serviceid_dict.get(input_language)
                if asr_serviceid_val is not None:
                    st.caption(f"**ASR Model:** :green[{asr_serviceid_val}]")
                else:
                    st.caption(f"**ASR Model:** :red[Unsupported]")
            except: st.caption(f":red[Error fetching data from API]")
            
            ###
            
            nmt_serviceid_dict = {'bn,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'bn,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'en,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'gu,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'hi,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'kn,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ml,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'mr,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'or,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'pa,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'sa,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ta,te': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'te,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,en': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,as': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,bn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,brx': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,gu': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,hi': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,kn': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,ml': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,mni': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,mr': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,or': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,pa': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,ta': 'ai4bharat/indictrans-v2-all-gpu--t4', 'ur,te': 'ai4bharat/indictrans-v2-all-gpu--t4'}
            try:
                query = str(input_language) + "," + str(output_language)
                nmt_serviceid_val = nmt_serviceid_dict.get(query)

                varx = "en," + str(input_language)
                st.session_state.in_lang_sid = nmt_serviceid_dict.get(varx)

                if nmt_serviceid_val is not None:
                    st.caption(f"**NMT Model:** :green[{nmt_serviceid_val}]")
                else:
                    st.caption(f"**NMT Model:** :red[Unsupported]")
            except: st.caption(f":red[Error fetching data from API]")

            ###

            tts_serviceid_dict = {'en': 'ai4bharat/indic-tts-coqui-misc-gpu--t4', 'as': 'ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4', 'brx': 'ai4bharat/indic-tts-coqui-misc-gpu--t4', 'gu': 'ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4', 'hi': 'ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4', 'kn': 'ai4bharat/indic-tts-coqui-dravidian-gpu--t4', 'ml': 'ai4bharat/indic-tts-coqui-dravidian-gpu--t4', 'mni': 'ai4bharat/indic-tts-coqui-misc-gpu--t4', 'mr': 'ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4', 'or': 'ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4', 'pa': 'ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4', 'ta': 'ai4bharat/indic-tts-coqui-dravidian-gpu--t4', 'te': 'ai4bharat/indic-tts-coqui-dravidian-gpu--t4', 'bn': 'ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4'}
            try:
                query = input_language
                tts_serviceid_val = tts_serviceid_dict.get(query)
                if tts_serviceid_val is not None:
                    st.caption(f"**TTS Model:** :green[{tts_serviceid_val}]")
                else:
                    st.caption(f"**TTS Model:** :red[Unsupported]")
            except: st.caption(f":red[Error fetching data from API]")


        col1_row5, col1_row6 = st.columns([6,1])
        with col1_row5:
            add_vertical_space(1)
            prompt_from_user = st.text_input(":mag: Enter your question", label_visibility='collapsed', placeholder="Enter your question")
            original_prompt_from_user = prompt_from_user
            st.session_state.orig_query = prompt_from_user
        with col1_row6:
            add_vertical_space(1)
            audio = None
            audio = audiorecorder("🎙️", "🔴")

        if len(audio) > 0:
            try:
                st.success("Recorded audio")
                wav_file = open("./audio/audio.mp3", "wb")
                wav_file.write(audio.tobytes())
                mp3_to_wav("./audio/audio.mp3", "./audio/audio_wav.wav")
                enc = base64.b64encode(open("./audio/audio_wav.wav", "rb").read())
                enc = enc.decode("utf-8")
                #st.write(enc)
                recorded_audio = bhashini_asr(enc, input_language, asr_serviceid_val)
                st.write(recorded_audio)
                st.session_state.orig_query = recorded_audio

            except:
                st.error("An error occured while recording your voice, please try again.")
        

        submitted = st.form_submit_button("Submit", on_click=hide_examples)
        

       
        with col2:
            placeholder = st.container()
            if st.session_state.load_example == 0:
                with placeholder:
                    draw_examples()

        if submitted:

            with placeholder:
                placeholder.empty()
                lottie_progress = load_lottiefile("./json/loading.json")
                with st_lottie_spinner(lottie_progress, loop=True, key="progress", height=180):
                    try: 
                        if not prompt_from_user:
                            prompt_from_user = recorded_audio
                            st.session_state.orig_query = prompt_from_user
                        if input_language != "en":
                            prompt_from_user = bhashini_translate(st.session_state.orig_query, input_language, output_language, nmt_serviceid_val)
                        DOCUMENT1 = "Rice cultivation is well-suited to countries and regions with low labor costs and high rainfall, as it is labor-intensive to cultivate and requires ample water. The traditional method for cultivating rice is flooding the fields while, or after, setting the young seedlings. This simple method requires sound planning and servicing of the water damming and channeling, but reduces the growth of less robust weed and pest plants that have no submerged growth state. While flooding is not mandatory for the cultivation of rice, all other methods of irrigation require higher effort in weed and pest control during growth periods and a different approach for fertilizing the soil.  Nutrient ManagementImportance of NutrientsNutritional DisordersManuring Fertilizer Requirement INM Nutrient ManagementImportance of NutrientsPaddy requires the following essential nutrients for its normal development:CarbonNitrogenCalciumHydrogenPhosphorusMagnesiumOxygenPotassiumSulphurIronZincChlorineManganeseBoronCopperMolybdenumNitrogen, phosphorus and potassium are known as primary plant nutrients; calcium, magnesium and sulphur, as secondary nutrients; iron manganese, copper, zinc, boron, molybdenum and chlorine as trace elements or micro-nutrients. The primary and secondary nutrient elements are known as major elements. This classification is based on their relative abundance, and not on their relative importance. The micronutrients are required in small quantities, but they are important as the major elements in plant nutrition.Nitrogen Nitrogen, the most important nutrient for rice, is universally limiting the rice productivity.Nitrogen encourages the vegetative development of plants by imparting a healthy green color to the leaves.It seems that majority of Indica varieties are adapted to relatively low levels of nitrogen in the region of 25 kg N/ha.Rice plant depends mainly for its nitrogen upon the decomposition of organic matter under anaerobic conditions and in the early stages of growth takes up nitrogen in the form of ammonia which is the stable form of nitrogen in submerged soils.There are two stages in the growth of rice crop when nitrogen is most needed; early vegetative and panicle initiation stages.Fertilizing the crop during early vegetative growth promotes tillering leading to higher yield. Application at panicle initiation or early booting stage will help the plant produce more and heavier grains per panicle.PhosphorusPhosphorus is particularly important in early growth stages.It is mobile within the plant and promotes root development (Particularly the development of fibrous roots),tillering and early flowering.Addition of mineral P fertilizer is required when the rice plants root system is not yet fully developed and the native soil P supply is inadequate.Phosphorus is remobilized within the plant during later growth stages if sufficient P has been absorbed during early growth.It also increases resistance to disease and strengthens the stems of cereal plants, thus reducing their tendency to lodge. It offsets the harmful effects of excess nitrogen in the plant.PotassiumPotassium enhances the ability of the plants to resist diseases, insect attacks, cold and other adverse conditions.It plays an essential part in the formation of starch and in the production and translocation of sugars, and is thus of special value to carbohydrate-rich crops.Involves in working of enzymes.Helps in production and movement of photosynthates to sink.Helps in proper uptake of other nutrients.Influences tillering or branching of plant and size and weight of grain.Over 80 per cent of the absorbed potassium by the plant is found in straw.Need for potassium is most likely to occur on sandy soils.CalciumCalcium combines with pectin in the plant to form calcium pectate, which is an essential constituent of the cell-wall.It also promotes the activity of soil bacteria concerned with the fixation of free nitrogen or the formation of nitrates from organic forms of nitrogen.Furthermore, it is necessary for the development of a good root system. MagnesiumMagnesium is an essential constituent of chlorophyll.It is usually needed by plant in relatively small quantities.Hence its deficiency in the soil is experienced later than that of potassium.SulphurIt involve in chlorophyll production, protein synthesis and plant function and structure. Sulphur forms an important constituent of straw and plant stalks.IronIron is necessary for the synthesis of chlorophyll. Mainly a problem in upland soils. ZincEssential for the transformation of carbohydrates. Regulates consumption of sugars. The function of zinc in plants is as a metal activator of enzymes. Deficiency of zinc in lowland rice occurs in near neural to alkaline soils, particularly in calcareous soils. Availability of both soil and applied zinc is higher in upland soil than in submerged soil. Soil submergence causes decrease in zinc concentration in the soil solution. Rice crop removes 30-40 g Zn per tonne of grain.BoronBoron facilitates the translocation of sugars by forming sugar borate complex. It involves in cell differentiation and development since boron is essential for DNA synthesis. Also involves in fertilization, hormone metabolism etc. CopperIt is an important constituent of plastocyanin (copper containing protein)."
                        DOCUMENT2 = "Systems of rice cultivation in various rice growing areas are largely depends upon the crop growing conditions like soil type, available water and prevailing monsoon. The principal rice ecosystems followed in Tamil Nadu, Kerala and Karnataka are: 1.Wet system 2.Dry system 3.Semidry system Wet System Paddy Root The wet system is also known as Irrigated rice. In this system, the crop is grown under wet (irrigated) conditions from seed to seed. The field is brought to a soft puddle by repeated ploughings with 5-7 cm standing water. After obtaining a soft puddle and perfect levelling, rice seedlings are transplanted or sprouted seeds dibbled or broadcasted on the puddle field. This system of cultivation is followed wherever assured irrigation water is available. This irrigated rice contributes to 55 per cent of the total rice production System of Rice Intensification (SRI) Transplanted Puddled Lowland Rice Direct Wet Seeded Puddled Lowland Rice METHODS FOLLOWED IN WET SYSTEM ARE SYSTEM OF RICE INTENSIFICATION TRANSPLANTED PUDDLED LOWLAND RICE DIRECT WET SEEDED PUDDLED LOWLAND RICE Top System of Rice Intensification System of Rice Intensification (SRI) is a methodology for increasing the productivity of irrigated rice by changing the management of plants, soil, water and nutrients particularly by eliciting greater root growth. SRI is not a technology because something still evolving and improving, season by season, as more experience is gained and as more farmers, scientists and others apply their intelligence and insights to making rice production more efficient and sustainable. Critical Steps in SRI SRI Practices Advantages and Constraints of SRI Crop Response Difference between Conventional and SRI method of cultivation Cost comparison for Conventional and SRI method of cultivation Critical steps in SRI Nursery area and Seed rate Seedling age Square planting Water management Mechanical (Cono) weeder usage Nursery area and seed rate Only 7-8 kg of seed is required to plant 1 ha. Nursery area is reduced to 100m2 / ha. For raised beds @ 1 x 5 m and 20 beds are required for 1 ha. Spread polythene sheets over the beds evenly. Fill the soil evenly over the Polythene sheets upto 4cm. Uniformly spread 375 g of seeds in each 5 sq.m. nursery bed. Watering through rose can is advisable. Cover the seed bed using locally available mulching materials like coirpith/straw nurseryarea Seedling age seedlingage Fourteen days old seedlings were recommended for transplanting (3 leaves stage) If the nursery bed is properly prepared with sufficient organic manure, the seedling growth will be good to handle. Water Management Water management is one of the critical steps in SRI and provision of aerobic environment in rice fields is the core point in SRI. Plants with truncated roots cannot access the residual soil moisture in lower horizons that is accessible to plants which have large and functioning roots systems to maintain their growth and productivity. Hence, alternate wetting and drying is advocated. Irrigation only to moist the soil in the early period of 10 days. Restoring irrigation to a maximum depth of 2.5cm after development of hairline cracks in the soil until panicle initiation. Increasing irrigation depth to 5.0 cm after Panicle initiation one day after disappearance of ponded water. watermgmt Mechanical (Cono) weeder usage mech8 Square planting eases the cono/rotary weeder operation in two directions, and thereby weed management could be effected efficiently. In SRI, weeder should be used at 10 days interval from the date of transplanting. Three labours are enough to weed one acre. Weeds are trampled and on decay the nutrient are ploughed back to the soil. Soil is frequently disturbed which has beneficial physico chemical – biological results in soil. Root pruning triggers the tillering that results in bursting out of tillers. Water level should be properly monitored for usage of weeder. It is important to remove the left out weeds by hand. By this the cost of weeding is reduced by 52.5%. Top SRI Practices The Principles of SRI are achieved by following certain practices Season Dry season with assured irrigation is more suitable. Difficulty in crop establishment may be seen in areas with heavy downpour (NE Monsoon periods of Tamil Nadu) Varieties Hybrids and varieties with heavy tillering. Seed rate 7- 8 kg / ha for single seedling per hill Nursery Management Required nursery area is 100 m2/ha (or) 2.5 cent/ha – 1cent/acre Usage of well decomposed good quality FYM judiciously. For raised beds @ 1 x 5 m and 20 beds are required for 1 ha. Powdered DAP may be applied @ 95g/raised bed in total 1.9 kg should be used. Spread polythene sheets over the beds evenly. Old polysacks can also be used. ill the soil evenly on the Polythene sheets upto 4cm. Seed treatment can be done with Pseudomonas 10g/kg seed. 75 g Azophos biofertiliser/kg seed. Uniformly spread 375 g of seeds in each 5 sq.m. nursery bed. Watering through rose can is advisable. Cover the seed bed using locally available mulching materials like coirpith/straw. Main field preparation Plough the land during summer to economize the water requirement for initial preparation of land. Flood the field 1 or 2 days before ploughing and allow water to soak in. Keep the surface of the field covered with water. Keep water to a depth of 2.5cm at the time of puddling. Good leveling (laser leveling) of the main field is essential in SRI. Field drainage is an important component in SRI. Transplanting The seedling along with the soil intact with the roots should be removed and plant them immediately. Fourteen days old seedlings were recommended for transplanting. At this stage the seedling will have 3 leaves. If the nursery bed is properly prepared with sufficient organic manure, the seedling growth will be good to handle. Plant spacing Square planting at 25 x 25cm ensures optimum space for efficient utilization of resources. Place single seedling at intersecting points marked with the marker. Place the seedling without plunging too deep into the soil. Nutirent Management Apply 12.5 t of FYM or compost or green leaf manure @ 6.25 t/ha. Organic manures addition is recommended in SRI cultivation, as they are found to supply essential nutrients, and creates favorable conditions for soil microbes being a source of carbon. Apply fertilizer nutrients as per soil test recommendations. N dose may be through Leaf Color Chart (LCC). P & K may be through Site Specific Nutrition Management. Depending on the necessity, top dress with chemical fertilizers. Water Management Water management is one of the critical steps in SRI and provision of aerobic environment in rice fields is the core point in SRI. Irrigate to 2.5 cm depth of water level after hairline crack formation up to panicle initiation and after that disappearance of ponded water. Water saving in this system is 40-50% from planting to harvest. Farmers using ground water will realize the water, time and electricity saving. Regular water application to keep soil moist but not saturated. Intermittent wetting and drying for adequate aeration during vegetative phase. Relatively frequent watering after vegetative phase. No water stagnation at any stage. Weeder Use Using weeder is of primary importance in SRI. Use simple rotary weeder between crop rows in both the directions starting from 10 days after planting About four rotary weedings at 10 to 15 days interval could be adequate till panicle initiation If necessary, one or two hand weedings may be necessary to remove weeds closer to rice plants."
                        DOCUMENT3 = "The rice variety called Padma, suited for Irrigated type of land, was released in the year 1968 by ICAR and takes 120 days to cultivate. The grain type of Padma is SB and it can be cultivated in the regions CVRC. Padma has the following reaction to diseases and pests and if available, its Average Grain Yield t/ha is MR-BLField tolerance to all major Diseases & Pest. The rice variety called Bala, suited for Upland type of land, was released in the year 1970 by ICAR and takes 105 days to cultivate. The grain type of Bala is SB and it can be cultivated in the regions CVRC. Bala has the following reaction to diseases and pests and if available, its Average Grain Yield t/ha is MR-BL, SB, Hard to thresh. The rice variety called Kiron, suited for Irrigated type of land, was released in the year 1970 by ICAR and takes 110 days to cultivate. The grain type of Kiron is MS and it can be cultivated in the regions West Bengal. Kiron has the following reaction to diseases and pests and if available, its Average Grain Yield t/ha is Field tolerance to all major Diseases & Pest, 2.3 t/ha."
                        texts = [DOCUMENT1, DOCUMENT2, DOCUMENT3]
                        df = pd.DataFrame(texts)
                        df.columns = ["Text"]

                        df["Embeddings"] = df["Text"].apply(embed_fn)
                        print(df)

                        query = prompt_from_user

                        passage = find_best_passage(query, df)

                        prompt = make_prompt(query, passage)
                        text_models = [
                            m
                            for m in palm.list_models()
                            if "generateText" in m.supported_generation_methods
                        ]

                        text_model = text_models[0]

                        temperature = 0.5
                        max_output_tokens = 100

                        answer = palm.generate_text(
                            prompt=prompt,
                            model=text_model,
                            candidate_count=1,
                            temperature=temperature,
                            max_output_tokens=max_output_tokens,
                        )

                        llm_response = answer.candidates[0]["output"]
                        if input_language != "en":
                            #st.write("non english input detected...")
                            llm_response_tl = bhashini_translate(llm_response, output_language, input_language, nmt_serviceid_val)
                            tts_audio = bhashini_tts(llm_response_tl, input_language, tts_serviceid_val)
                            audio_bytes = base64.b64decode(tts_audio)
                        else:
                            #st.write("english input detected...")
                            tts_audio = bhashini_tts(llm_response, input_language, tts_serviceid_val)
                            audio_bytes = base64.b64decode(tts_audio)
                        
                        with st.expander("See PALM2 model", expanded=False):
                            st.caption(f"**Model:** :green[{text_model.name}]")
                            #st.caption(f"**Input Token Limit:** :green[{text_model.input_token_limit}]")
                            st.caption(f"**Output Token Limit:** :green[{text_model.output_token_limit}]")
                            st.caption(f"**Temperature:** :green[{text_model.temperature}]")
                            #st.caption(f"**Top P:** :green[{text_model.top_p}]")
                            #st.caption(f"**Top K:** :green[{text_model.top_k}]")
                        with st.chat_message("🧑🏽‍🌾"):
                            st.write(f"**{st.session_state.orig_query}**")
                        with st.chat_message("💡"):
                            if input_language != "en":
                                st.write(llm_response_tl)
                                st.session_state.llm_history = f"{st.session_state.llm_history}\n{st.session_state.orig_query}\n{llm_response_tl}\n"
                                
                                st.audio(audio_bytes, format='audio/wav')
                                st.caption(llm_response)
                                num_tokens = math.ceil(len(llm_response)/4)
                                #print(max)
                                if num_tokens >= max_output_tokens:
                                    st.caption(f"Output tokens = :red[{num_tokens}/{max_output_tokens}]", help="1 token is around 4 characters in length")
                                else:
                                    st.caption(f"Output tokens = :green[{num_tokens}/{max_output_tokens}]", help="1 token is around 4 characters in length")
                            else:
                                st.write(llm_response)
                                st.audio(audio_bytes, format='audio/wav')
                                num_tokens = math.ceil(len(llm_response)/4)
                                if num_tokens >= max_output_tokens:
                                    st.caption(f"Output tokens = :red[{num_tokens}/{max_output_tokens}]", help="1 token is around 4 characters in length")
                                else:
                                    st.caption(f"Output tokens = :green[{num_tokens}/{max_output_tokens}]", help="1 token is around 4 characters in length")

                    except:
                        st.error("An unexpected error occured. Please check your input.")

    add_vertical_space(5)

    cola, colb, colc, cold, cole = st.columns(5)
    with colb:
        if st.button('💾', use_container_width=True):
            pass
        
    with colc:
        if st.button('⏱️', use_container_width=True):
            st.session_state.sidebar_state = 'collapsed' if st.session_state.sidebar_state == 'expanded' else 'expanded'
            st.experimental_rerun()

    with cold:
        if st.button('✨', use_container_width=True):
            st.experimental_rerun()
    
with st.sidebar:
    st.title("History")
    history_var = st.session_state.llm_history
    st.caption(history_var)
    st.download_button('Download history', history_var)
