# 📧 Assistant Zimbra Agentique

Interface Gradio 6 + smolagents permettant de manipuler vos emails, calendriers et tâches de manière agentique via un assistant IA connecté à votre compte Zimbra.

## Fonctionnalités

### 📧 Messagerie (IMAP/Zimbra)

- **📬 Lister les emails** : Voir les emails récents dans votre boîte de réception ou tout autre dossier
- **📖 Lire les emails** : Obtenir le contenu complet d'un email spécifique (en-têtes + corps text/plain)
- **🔍 Rechercher** : Trouver des emails par expéditeur, sujet ou date (critères combinables)
- **📁 Lister les dossiers** : Voir tous les dossiers de votre boîte mail
- **✏️ Créer des brouillons** : Préparer des emails en brouillon dans le dossier Drafts

### 📅 Calendrier & Tâches (CalDAV/Zimbra)

- **📆 Lister les calendriers** : Voir tous les calendriers disponibles sur le serveur CalDAV
- **📝 Créer des événements** : Planifier des événements avec récurrence (rrule) et participants
- **📅 Voir les événements** : Rechercher des événements dans une plage de dates (expansion des récurrences)
- **✅ Créer des tâches** : Ajouter de nouvelles tâches avec date d'échéance
- **📋 Lister les tâches** : Voir les tâches avec filtrage (en cours, complétées, etc.)

### 🕐 Utilitaires

- **🕐 Heure actuelle** : Obtenir l'heure locale du système pour les calculs de dates relatives

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Utilisateur                    │
│                    (Gradio 6 - ChatInterface)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent smolagents                         │
│         (CodeAgent avec outils IMAP + CalDAV)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Modèle LLM (ILaaS)                        │
│            (qwen-3.6-35b-instruct via API REST)              │
└──────────────────────────────────────────────────────────────┘
                         
```

## Installation

### Prérequis

- Python 3.10+
- Accès à l'API ILaaS pour un modèle LLM
- Compte Zimbra avec accès IMAP et CalDAV

### Configuration

1. **Cloner le dépôt**
2. **Installer les dépendances** :

```bash
pip install -r requirements.txt
```

1. **Configurer les variables d'environnement** :

```bash
cp .env.example .env
```

Puis éditer le fichier `.env` avec vos informations :

```bash
# Configuration du modèle LLM (ILaaS)
ILAAS_API_KEY=votre_clé_api_ilaas

# Configuration IMAP pour Zimbra
IMAP_SERVER=imap.zimbra.example.com
USERNAME=votre_email@example.com
PASSWORD=votre_mot_de_passe

# Configuration CalDAV pour Zimbra (optionnel - pour calendrier et tâches)
CALDAV_URL=https://z.imt.fr/
```

## Utilisation

### Lancer l'application

```bash
python app.py
```

L'interface sera accessible à l'adresse : `http://localhost:7860`

### Exemples de commandes

Vous pouvez interagir avec l'assistant en utilisant des commandes naturelles :

```
# Messagerie
- "Liste mes 5 derniers emails"
- "Montre-moi les dossiers de ma boîte mail"
- "Recherche les emails de l'expéditeur@example.com"
- "Crée un brouillon pour test@example.com avec le sujet 'Test' et le corps 'Bonjour'"
- "Lis l'email avec le sujet 'Réunion de demain'"

# Calendrier
- "Montre-moi mes calendriers"
- "Crée un événement pour demain à 14h30 avec pour sujet 'Point équipe' et une durée de 1h"
- "Quels événements ai-je la semaine prochaine ?"

# Tâches
- "Crée une tâche 'Faire le rapport mensuel' avec pour échéance vendredi"
- "Montre-moi mes tâches en cours"

# Utilitaires
- "Quelle est l'heure actuelle ?"
```

## Structure du projet

```
.
├── app.py                  # Application principale Gradio + smolagents
├── tools.py                # Outils IMAP et CalDAV (Tool implementations)
├── requirements.txt        # Dépendances Python
├── .env.example           # Exemple de configuration
└── README.md              # Documentation
```

## Configuration avancée

### Variables d'environnement

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `ILAAS_API_KEY` | Clé API pour le modèle LLM | Oui |
| `ILAAS_BASE_URL` | URL de base de l'API ILaaS | Non (défaut: `https://llm.ilaas.fr/v1`) |
| `IMAP_SERVER` | Serveur IMAP (ex: imap.zimbra.example.com) | Oui |
| `CALDAV_URL` | URL du serveur CalDAV | Non (défaut: `https://z.imt.fr/`) |

### Outils disponibles

L'agent utilise les outils suivants, définis dans [`tools.py`](tools.py) :

#### Outils IMAP

| Outil | Nom | Description |
|-------|-----|-------------|
| `list_emails` | `ListEmailsTool` | Liste les emails récents d'un dossier IMAP (paramètres: `limit`, `folder`) |
| `get_email_content` | `GetEmailTool` | Récupère le contenu complet d'un email (paramètres: `email_id`, `folder`) |
| `search_emails` | `SearchEmailsTool` | Recherche des emails par expéditeur, sujet, date (paramètres: `from_address`, `subject`, `since`, `folder`, `limit`) |
| `create_draft` | `CreateDraftTool` | Crée un brouillon dans le dossier Drafts (paramètres: `to`, `subject`, `body`) |

#### Outils CalDAV - Calendrier

| Outil | Nom | Description |
|-------|-----|-------------|
| `get_current_time` | `GetCurrentTimeTool` | Obtient l'heure locale du système |
| `list_calendars` | `ListCalendarsTool` | Liste tous les calendriers disponibles |
| `create_event` | `CreateEventTool` | Crée un événement avec récurrence et participants (paramètres: `calendar_name`, `summary`, `start_time`, `end_time`, `rrule`, `description`) |
| `get_events` | `GetEventsTool` | Récupère les événements dans une plage de dates (paramètres: `calendar_name`, `start_time`, `end_time`) |

#### Outils CalDAV - Tâches

| Outil | Nom | Description |
|-------|-----|-------------|
| `create_task` | `CreateTaskTool` | Crée une tâche VTODO avec date d'échéance (paramètres: `calendar_name`, `summary`, `due_date`, `status`) |
| `get_tasks` | `GetTasksTool` | Récupère les tâches avec filtrage (paramètres: `calendar_name`, `pending_only`) |


## Sécurité

- Les credentials IMAP/CalDAV sont stockés uniquement en RAM (bien laissé Debug=False)
- Ne jamais committer le fichier `.env`
- L'application ne stocke aucun email ni donnée calendrier localement

## Dépannage

### Erreurs courantes

1. **"RuntimeError: Environment variable ILAAS_API_KEY not set"**
   - Vérifier que le fichier `.env` est correctement configuré
2. **"Error: Cannot select INBOX"**
   - Vérifier les credentials IMAP
   - Vérifier que le dossier INBOX existe
3. **"Connection refused"**
   - Vérifier la connectivité au serveur IMAP
   - Vérifier le port SSL (généralement 993)
4. **"Calendar not found"**
   - Vérifier que le nom du calendrier correspond à un calendrier existant sur le serveur CalDAV (souvent 'Calendar' ou 'primary')
5. **"Invalid date format"**
   - Utiliser le format ISO 8601 pour les dates (ex: `2026-07-20T14:30:00`)

## Licence

Ce projet est fourni tel quel à des fins de démonstration.

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
