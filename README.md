# Expérimentations RAGaRenn 

Bienvenue dans ce dépôt consacré à mes expérimentations avec [RAGaRenn](https://ragarenn.eskemm-numerique.fr).  
Ce dépôt rassemble scripts, notebooks et autres ressources montrant les possibilités offertes par ce fantastique projet :smiley_cat:

## Objectifs
- Centraliser le code que j'utilise quotidiennement avec RAGaRenn.
- Partager des démonstrations reproductibles.
- Documenter quelques résultats.

## Contenu
- [Notebooks](notebooks/) : Prise en main de l'API OpenAI avec Python.
- [Scripts](scripts/) : Scripts shell pour s'interfacer avec l'API REST de RAGaRenn.
- [Démonstrations](demos/) :
  - [Support aux utilisateur·trices](demos/support_gradio_agent.py) : Un robot conversationnel de support informatique qui dispose de connaissances issues d'un intranet et d'un catalogue de services.
  <img alt="Capture d'écran support informatique" src="https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Support%20informatique.png" width="600" />
  
  - [Saisie de devis](demos/quotes_agent.py) : Un agent qui fait de la saisie de devis.
  <img alt="Capture d'écran outil de gestion de devis" src="https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Gestion%20des%20devis.png" width="600" />
  
  - [Assistant pédagogique MOOC](notebooks/chatbot.ipynb) : Un agent qui répond aux questions aux apprenant·es d'un cours en ligne avec l'aide d'humain·es.
  <img alt="Capture d'écran assistant pédagogique MOOC" src="https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Assistant%20p%C3%A9dagogique%20MOOC.png" width="600" />
  
  - [Agent connecté à un navigateur web](demos/mcp_browser_agent.py) : Un agent qui peut faire des recherches, écrire du code, prendre la main d'un navigateur web...
  <img alt="Capture d'écran agent connecté à un navigateur web" src="https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Agent%20connect%C3%A9%20%C3%A0%20un%20navigateur.png" width="600" />
  
  -  [Serveur MCP CalDAV](https://github.com/bgaultier/caldav-mcp-server/) : Un serveur MCP qui permet à un agent de gérer vos calendriers.
  <img alt="Capture d'écran client MCP CalDAV" src="https://raw.githubusercontent.com/bgaultier/caldav-mcp-server/refs/heads/master/capture_continue.png" width="400" />

  -  [Serveur MCP IMAP](https://github.com/bgaultier/imap-mcp-server) : Un serveur MCP qui permet à un agent de lire vos emails et de rédiger des brouillons.
  <img alt="Capture d'écran MCP IMAP" src="https://raw.githubusercontent.com/bgaultier/imap-mcp-server/refs/heads/master/capture_continue.png" width="280" />

  -  [Tri et classification d'emails avec n8n](demos/n8n%20-%20Tri%20et%20classification%20des%20emails.json) : Automatisation n8n permettant de trier, classifier et répondre à des emails.
  <img alt="Capture d'écran n8n" src="https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Tri%20et%20classification%20des%20emails%20avec%20n8n.png" width="600" />

  -  [Super assistant IA personnel et autonome OpenClaw](demos/openclaw.json) : Agent IA local capable d'automatiser vos tâches quotidiennes (gestion d'emails, calendrier, navigation web) via Mattermost, WhatsApp, Telegram, Matrix...
  <img alt="Capture d'écran OpenClaw" src="[https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Tri%20et%20classification%20des%20emails%20avec%20n8n.png](https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Agent%20OpenClaw%20avec%20un%20bot%20mattermost.png)" width="600" />
  
  - [Assistant commandes dans le terminal](demos/zsh-copilot/zsh-copilot.plugin.zsh) : Un assistant qui fournit des suggestions de commandes dans le terminal.
  - [Robot conversationnel vocal](https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Robot%20conversationnel%20vocal.jpg) Un agent qui peut répondre à des questions posées à voix haute.
  <img alt="Capture d'écran robot conversationnel vocal" src="https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Robot%20conversationnel%20vocal.jpg" width="280" />

  - [Agent IA Zimbra](demos/zimbra_smolagent) Un agent IA qui permet de manipuler vos emails, calendriers et tâches.
  <img alt="Capture d'écran zimbra smolagents" src="https://raw.githubusercontent.com/bgaultier/experimentations-ragarenn/refs/heads/main/screenshots/Zimbra%20smolagents.png" width="600" />

  - D'autres agents basés sur [smolagents](https://huggingface.co/learn/agents-course/fr/unit2/smolagents/introduction) (à venir 🙂)...

## Liens
- Site RAGaRenn : https://ragarenn.eskemm-numerique.fr
- FAQ RAGaRenn : https://projet-air.univ-rennes.fr/faq-ragarenn
- Cours sur les agents IA par Hugging Face : https://huggingface.co/learn/agents-course/fr/
- Cours sur Model Context Protocol par Hugging Face : https://huggingface.co/learn/mcp-course/

