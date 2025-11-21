import gradio as gr

gr.load_chat("https://ragarenn.eskemm-numerique.fr/sso/instance@imt/api/", model="support-disi", token="sk-9ee9eabc6dd942488dc661851dd4fbfb").launch(pwa=True, share=True)