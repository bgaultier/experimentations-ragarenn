"""
Assistant Email & Calendrier — Gradio 6 + smolagents + Zimbra (IMAP/CalDAV)
Auth = validation IMAP | Isolation par session
"""

from dotenv import load_dotenv
load_dotenv()

import os
import imaplib
import json
import gradio as gr
from smolagents import CodeAgent, OpenAIServerModel

from tools import (
    ImapCredentials,
    ListEmailsTool,
    GetEmailTool,
    SearchEmailsTool,
    CreateDraftTool,
    GetCurrentTimeTool,
    ListCalendarsTool,
    CreateEventTool,
    GetEventsTool,
    CreateTaskTool,
    GetTasksTool
)

ILAAS_BASE_URL = "https://llm.ilaas.fr/v1"
ILAAS_API_KEY = os.getenv("ILAAS_API_KEY")
IMAP_SERVER = os.getenv("IMAP_SERVER")

SESSION_CREDS: dict[str, ImapCredentials] = {}

def _try_imap_login(server: str, username: str, password: str) -> bool:
    try:
        mail = imaplib.IMAP4_SSL(server, 993)
        mail.login(username, password)
        mail.logout()
        return True
    except Exception:
        return False

def verify_credentials(username: str, password: str) -> bool:
    if _try_imap_login(IMAP_SERVER, username, password):
        SESSION_CREDS[username] = ImapCredentials(IMAP_SERVER, username, password)
        return True
    return False

def build_agent(creds: ImapCredentials) -> CodeAgent:
    tools = [
        # IMAP Tools
        ListEmailsTool(creds),
        GetEmailTool(creds),
        SearchEmailsTool(creds),
        CreateDraftTool(creds),
        
        # CalDAV Tools
        GetCurrentTimeTool(),
        ListCalendarsTool(creds),
        CreateEventTool(creds),
        GetEventsTool(creds),
        CreateTaskTool(creds),
        GetTasksTool(creds)
    ]
    model = OpenAIServerModel(
        model_id="qwen-3.6-35b-instruct", # Ensure this model handles CodeAgent well (Qwen usually does)
        api_base=ILAAS_BASE_URL,
        api_key=ILAAS_API_KEY,
    )
    return CodeAgent(tools=tools, model=model, max_steps=24, verbosity_level=1)

def chat_response(message, history, agent_state, request: gr.Request):
    if agent_state is None:
        if request is None or not getattr(request, "username", None):
            return "⚠️ Session non authentifiée.", agent_state
        creds = SESSION_CREDS.get(request.username)
        if creds is None:
            return "⚠️ Identifiants introuvables, reconnectez-vous.", agent_state
        agent_state = build_agent(creds)

    try:
        result = agent_state.run(message)
        return str(result), agent_state
    except Exception as exc:
        return f"⚠️ Erreur : {exc}", agent_state

EXAMPLES = [
    ["Résume les 5 derniers emails non-lus.", None],
    ["Quels sont mes rendez-vous prévus pour demain ?", None],
    [("Trie et résume mes emails reçus hier. Écris un brouillon de réponse "
      "pour chacun des messages qui te semble important."), None],
    ["Crée un événement 'Réunion de projet' demain à 10h sur le calendrier "
     "'Calendar' et répète-le toutes les semaines.", None],
    ["Peux-tu me fournir mes disponibilités pour la semaine prochaine de 9h à "
     "17h en excluant 12h à 14h. Agrège au maximum les créneaux, par exemple :"
     "- Demain après-midi"
     "- Lundi prochain de 10h à 12h", None],
    ["Crée une tâche 'Préparer la présentation' avec pour échéance vendredi à "
     "17h.", None],
]



# --- FONCTIONS PYTHON DE MISE À JOUR ---
def sync_dropdown(json_str):
    """Met à jour le menu déroulant à partir du JSON renvoyé par le JS"""
    try:
        prompts = json.loads(json_str) if json_str else []
        return gr.update(choices=prompts, value=prompts[0] if prompts else None)
    except:
        return gr.update(choices=[], value=None)

def clear_input():
    return gr.update(value="")

# --- SCRIPTS JAVASCRIPT (Gèrent le localStorage) ---
JS_LOAD = """
function() {
    let saved = localStorage.getItem("zimbra_agent_prompts");
    return saved ? saved : "[]";
}
"""

JS_SAVE = """
function(new_val) {
    if (!new_val || new_val.trim() === "") {
        return localStorage.getItem("zimbra_agent_prompts") || "[]";
    }
    let saved = localStorage.getItem("zimbra_agent_prompts");
    let prompts = saved ? JSON.parse(saved) : [];
    if (!prompts.includes(new_val)) {
        prompts.push(new_val);
        localStorage.setItem("zimbra_agent_prompts", JSON.stringify(prompts));
    }
    return JSON.stringify(prompts);
}
"""

JS_DELETE = """
function(selected_val) {
    if (!selected_val) return localStorage.getItem("zimbra_agent_prompts") || "[]";
    let saved = localStorage.getItem("zimbra_agent_prompts");
    let prompts = saved ? JSON.parse(saved) : [];
    prompts = prompts.filter(item => item !== selected_val);
    localStorage.setItem("zimbra_agent_prompts", JSON.stringify(prompts));
    return JSON.stringify(prompts);
}
"""
with gr.Blocks() as demo:
    gr.Markdown("## Agent IA pour Zimbra <img src=\"https://www.imt.fr/wp-content/uploads/2025/03/logo_imt_rvb_900px.png\" alt=\"Logo IMT\" style=\"height:44px; float:left\" /> ")
    gr.Markdown("Cet agent IA permet de gérer la messagerie (lire, rechercher, rédiger des brouillons d'emails via IMAP) et le calendrier (consulter, créer des événements et tâches via CalDAV) via z.imt.fr.")
    
    # --- COMPOSANT INVISIBLE SERVANT DE PONT JS <-> PYTHON ---
    local_storage_state = gr.Textbox(visible=False, elem_id="local_storage_state")

    agent_state = gr.State(value=None)
    chat_ui = gr.ChatInterface(
        fn=chat_response,
        additional_inputs=[agent_state],
        additional_outputs=[agent_state],
        examples=EXAMPLES,
        chatbot=gr.Chatbot(buttons=["copy", "copy_all"]),
    )
    
    # --- ACCORDÉON DES FAVORIS ---
    with gr.Accordion("⭐️ Mes prompts favoris", open=False):
        with gr.Row():
            prompt_dropdown = gr.Dropdown(label="Vos favoris sauvegardés localement", choices=[], interactive=True, scale=3)
            btn_use = gr.Button("⬆️ Utiliser", scale=1)
            btn_delete = gr.Button("🗑️ Supprimer", variant="stop", scale=1)
        
        with gr.Row():
            new_prompt_input = gr.Textbox(label="Nouveau prompt", placeholder="Tapez votre prompt à sauvegarder...", scale=4)
            btn_save = gr.Button("💾 Sauvegarder", variant="primary", scale=1)


    # --- ÉVÉNEMENTS ---
    # 1. Au chargement de la page, on exécute le JS_LOAD qui met le JSON dans le composant invisible
    demo.load(fn=None, inputs=None, outputs=local_storage_state, js=JS_LOAD)
    
    # 2. Quand le composant invisible change (suite au JS), on met à jour le menu déroulant en Python
    local_storage_state.change(fn=sync_dropdown, inputs=local_storage_state, outputs=prompt_dropdown)

    # 3. Sauvegarder un prompt (Exécute JS, met à jour le pont invisible, efface le champ de texte)
    btn_save.click(fn=None, inputs=[new_prompt_input], outputs=[local_storage_state], js=JS_SAVE).then(
        fn=clear_input, inputs=None, outputs=[new_prompt_input]
    )

    # 4. Supprimer un prompt (Exécute JS et met à jour le pont invisible)
    btn_delete.click(fn=None, inputs=[prompt_dropdown], outputs=[local_storage_state], js=JS_DELETE)

    # 5. Utiliser : Injecte simplement la valeur du menu déroulant dans la textbox du ChatInterface
    btn_use.click(fn=lambda x: x, inputs=[prompt_dropdown], outputs=[chat_ui.textbox])

if __name__ == "__main__":
    demo.launch(
        auth=verify_credentials,
        auth_message="⚠️ Ce service est développé par Baptiste avec de l'intelligence artificielle, il y a donc très peu de chance qu'il fonctionne ! Si vous voulez le tester néanmoins, merci d'indiquer vos identifiants z.imt.fr (adresse email et mot de passe école) :",
        theme=gr.themes.Base(primary_hue=gr.themes.colors.cyan),
        footer_links=["api", "gradio", "settings", {"💬 Contact", "mailto:baptiste.gaultier@imt-atlantique.fr"},]
    )