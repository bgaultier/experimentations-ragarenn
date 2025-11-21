#!/bin/bash

# Remplacez <votre_cle_api> par votre clé API depuis votre instance RAGaRenn
# Documentation : https://projet-air.univ-rennes.fr/faq-ragarenn#p-276
RAGARENN_API_KEY="<votre_cle_api>"

# Récupérer la liste des id des modèles disponibles sur une instance RAGaRenn
# À modifier en fonction de votre instance
curl -X GET "https://ragarenn.eskemm-numerique.fr/sso/ch@t/api/models" \
-H "Authorization: Bearer $RAGARENN_API_KEY" \
-H "Content-Type: application/json"|jq .data[].id