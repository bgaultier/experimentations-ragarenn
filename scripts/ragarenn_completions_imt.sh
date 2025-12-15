#!/bin/bash

# Exemple de complétion avec RAGaRenn
# À modifier en fonction de votre instance
curl -X POST "https://ragarenn.eskemm-numerique.fr/sso/instance@imt/api/chat/completions" \
-H "Authorization: Bearer $RAGARENN_IMT_API_KEY" \
-H "Content-Type: application/json" \
-d '{
        "model": "codestral:latest",
        "messages": [
            {
            "role": "user",
            "content": "Peux-tu me donner le code micropython pour faire clignoter une LED branchée sur la broche 2 en fonction de la valeur d un potentiomètre branché sur la broche 26 ? Réponds uniquement avec le code sans autre texte ou balise."
            }
        ]
    }'|jq '.choices[0].message.content'