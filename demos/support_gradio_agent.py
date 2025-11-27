import gradio as gr
import os

RAGARENN_IMT_API_KEY = os.environ["RAGARENN_IMT_API_KEY"]

gr.load_chat("https://ragarenn.eskemm-numerique.fr/sso/instance@imt/api/", model="support-disi", token=RAGARENN_IMT_API_KEY).launch(pwa=True, share=True)
