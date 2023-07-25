import google.generativeai as palm
from streamlit_extras.add_vertical_space import add_vertical_space
import textwrap
import numpy as np
import pandas as pd
import streamlit as st
import os
import time
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


import requests
import json
import base64
import streamlit as st

# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

if "load_example" not in st.session_state:
    st.session_state.load_example = 0

if "orig_query" not in st.session_state:
    st.session_state.orig_query = "none"

if "llm_history" not in st.session_state:
    st.session_state.llm_history = "a"

def hide_examples():
    st.session_state.load_example += 1

def inc_ctr():
    st.session_state["counter"]  += 1

if "counter" not in st.session_state:
    st.session_state["counter"]  = 0
count = st.session_state["counter"]



palm.configure(api_key="AIzaSyA-63D6SrEGAUVKH3b6lDEogLTjs1ddXNE")
bhashini_api_key = 'Mt5dh5Qjr_TtwqpK5uNHGgApAngZjJGDM97-PGlbokBx_-BboOvMckDDOdKD9-VD'

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
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-right: 2rem;
        padding-left: 2rem;
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

    engineered_prompt_text = f"""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
        Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
        However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
        strike a friendly and converstional tone.\
        If the passage is irrelevant to the answer, you may ignore it.\
        The plot of land of the user is located in India, so answer their questions keeping that in mind.\
        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'
        ANSWER:
        """

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
    st.markdown("**Try out these examples!**")
    annotated_text(
        "What is the best ",
        ("time", "datetime", "#bba035"),
        " to plant ",
        ("paddy", "crop", "#c15519"),
        " in my ",
        ("plot", "location", "#107794"),
        "?",
    )

    annotated_text(
        "What is the ",
        ("forecast", "weather", "#829254"),
        " in my ",
        ("area", "location", "#107794"),
        "?",
    )

    annotated_text(
        "What are some ",
        ("govt schemes", "data", "#992414"),
        " launched in my ",
        ("state", "location", "#107794"),
        "?",
    )

    annotated_text(
        "How do I protect my ",
        ("millets", "crop", "#c15519"),
        " against pests? ",
    )

    annotated_text(
        "Tell me where I can purchase ",
        ("fertilisers", "data", "#992414"),
        " in my ",
        ("area", "location", "#107794"),
        ".",
    )

tagline = "FOR INDIAN FARMERS"

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
            prompt_from_user = st.text_input(":mag: Enter your question", label_visibility='collapsed', placeholder="Enter your question", key=f"input_count{count}")
            original_prompt_from_user = prompt_from_user
            st.session_state.orig_query = prompt_from_user
        with col1_row6:
            add_vertical_space(1)
            audio = None
            audio = audiorecorder("🎙️", "🔴")

        if len(audio) > 0:
            try:
                st.success("Recorded audio")
                wav_file = open("audio.mp3", "wb")
                wav_file.write(audio.tobytes())
                mp3_to_wav("audio.mp3", "audio_wav.wav")
                enc = base64.b64encode(open("audio_wav.wav", "rb").read())
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
                lottie_progress = load_lottiefile("./lottieFiles/loading.json")
                with st_lottie_spinner(lottie_progress, loop=True, key="progress", height=180):
                    try: 
                        if not prompt_from_user:
                            prompt_from_user = recorded_audio
                            st.session_state.orig_query = prompt_from_user
                        if input_language != "en":
                            #st.write("translating...")
                            prompt_from_user = bhashini_translate(st.session_state.orig_query, input_language, output_language, nmt_serviceid_val)
                        #st.write(prompt_from_user)
                        DOCUMENT1 = "Rice cultivation is well-suited to countries and regions with low labor costs and high rainfall, as it is labor-intensive to cultivate and requires ample water. The traditional method for cultivating rice is flooding the fields while, or after, setting the young seedlings. This simple method requires sound planning and servicing of the water damming and channeling, but reduces the growth of less robust weed and pest plants that have no submerged growth state. While flooding is not mandatory for the cultivation of rice, all other methods of irrigation require higher effort in weed and pest control during growth periods and a different approach for fertilizing the soil.  Nutrient ManagementImportance of NutrientsNutritional DisordersManuring Fertilizer Requirement INM Nutrient ManagementImportance of NutrientsPaddy requires the following essential nutrients for its normal development:CarbonNitrogenCalciumHydrogenPhosphorusMagnesiumOxygenPotassiumSulphurIronZincChlorineManganeseBoronCopperMolybdenumNitrogen, phosphorus and potassium are known as primary plant nutrients; calcium, magnesium and sulphur, as secondary nutrients; iron manganese, copper, zinc, boron, molybdenum and chlorine as trace elements or micro-nutrients. The primary and secondary nutrient elements are known as major elements. This classification is based on their relative abundance, and not on their relative importance. The micronutrients are required in small quantities, but they are important as the major elements in plant nutrition.Nitrogen Nitrogen, the most important nutrient for rice, is universally limiting the rice productivity.Nitrogen encourages the vegetative development of plants by imparting a healthy green color to the leaves.It seems that majority of Indica varieties are adapted to relatively low levels of nitrogen in the region of 25 kg N/ha.Rice plant depends mainly for its nitrogen upon the decomposition of organic matter under anaerobic conditions and in the early stages of growth takes up nitrogen in the form of ammonia which is the stable form of nitrogen in submerged soils.There are two stages in the growth of rice crop when nitrogen is most needed; early vegetative and panicle initiation stages.Fertilizing the crop during early vegetative growth promotes tillering leading to higher yield. Application at panicle initiation or early booting stage will help the plant produce more and heavier grains per panicle.PhosphorusPhosphorus is particularly important in early growth stages.It is mobile within the plant and promotes root development (Particularly the development of fibrous roots),tillering and early flowering.Addition of mineral P fertilizer is required when the rice plants root system is not yet fully developed and the native soil P supply is inadequate.Phosphorus is remobilized within the plant during later growth stages if sufficient P has been absorbed during early growth.It also increases resistance to disease and strengthens the stems of cereal plants, thus reducing their tendency to lodge. It offsets the harmful effects of excess nitrogen in the plant.PotassiumPotassium enhances the ability of the plants to resist diseases, insect attacks, cold and other adverse conditions.It plays an essential part in the formation of starch and in the production and translocation of sugars, and is thus of special value to carbohydrate-rich crops.Involves in working of enzymes.Helps in production and movement of photosynthates to sink.Helps in proper uptake of other nutrients.Influences tillering or branching of plant and size and weight of grain.Over 80 per cent of the absorbed potassium by the plant is found in straw.Need for potassium is most likely to occur on sandy soils.CalciumCalcium combines with pectin in the plant to form calcium pectate, which is an essential constituent of the cell-wall.It also promotes the activity of soil bacteria concerned with the fixation of free nitrogen or the formation of nitrates from organic forms of nitrogen.Furthermore, it is necessary for the development of a good root system. MagnesiumMagnesium is an essential constituent of chlorophyll.It is usually needed by plant in relatively small quantities.Hence its deficiency in the soil is experienced later than that of potassium.SulphurIt involve in chlorophyll production, protein synthesis and plant function and structure. Sulphur forms an important constituent of straw and plant stalks.IronIron is necessary for the synthesis of chlorophyll. Mainly a problem in upland soils. ZincEssential for the transformation of carbohydrates. Regulates consumption of sugars. The function of zinc in plants is as a metal activator of enzymes. Deficiency of zinc in lowland rice occurs in near neural to alkaline soils, particularly in calcareous soils. Availability of both soil and applied zinc is higher in upland soil than in submerged soil. Soil submergence causes decrease in zinc concentration in the soil solution. Rice crop removes 30-40 g Zn per tonne of grain.BoronBoron facilitates the translocation of sugars by forming sugar borate complex. It involves in cell differentiation and development since boron is essential for DNA synthesis. Also involves in fertilization, hormone metabolism etc. CopperIt is an important constituent of plastocyanin (copper containing protein)."
                        # DOCUMENT2 = "Your Googlecar has a large touchscreen display that provides access to a variety of features, including navigation, entertainment, and climate control. To use the touchscreen display, simply touch the desired icon.  For example, you can touch the \"Navigation\" icon to get directions to your destination or touch the \"Music\" icon to play your favorite songs."
                        # DOCUMENT3 = "Shifting Gears  Your Googlecar has an automatic transmission. To shift gears, simply move the shift lever to the desired position.  Park: This position is used when you are parked. The wheels are locked and the car cannot move. Reverse: This position is used to back up. Neutral: This position is used when you are stopped at a light or in traffic. The car is not in gear and will not move unless you press the gas pedal. Drive: This position is used to drive forward. Low: This position is used for driving in snow or other slippery conditions."
                        texts = [DOCUMENT1]
                        # texts = [DOCUMENT1, DOCUMENT2, DOCUMENT3]
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
                        answer = palm.generate_text(
                            prompt=prompt,
                            model=text_model,
                            candidate_count=3,
                            temperature=temperature,
                            max_output_tokens=2000,
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

                        with st.chat_message("🧑🏽‍🌾"):
                            st.write(f"**{st.session_state.orig_query}**")
                        with st.chat_message("💡"):
                            if input_language != "en":
                                st.write(llm_response_tl)
                                st.session_state.llm_history = f"{st.session_state.llm_history}\n{llm_response_tl}"
                                
                                st.audio(audio_bytes, format='audio/wav')
                                st.caption(llm_response)
                            else:
                                st.write(llm_response)
                                st.audio(audio_bytes, format='audio/wav')
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
            pass
    
with st.sidebar:
    st.title("History")
    history_var = st.session_state.llm_history
    st.caption(history_var)
    st.download_button('Download history', history_var)
