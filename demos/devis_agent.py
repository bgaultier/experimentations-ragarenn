"""
title: Gestion de devis Open WebUI
author: Baptiste Gaultier and RAGaRenn Codestral
version: 1.0.2
description: Gérer vos devis et leur saisie
required_open_webui_version: 0.3.9
"""

import os
import requests
from datetime import datetime
import random
import json

class Tools:
    def __init__(self):
        # Initialize an in-memory quote database
        self.quotes_db = []
        self.quote_counter = 1000

    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """
        print(__user__)
        result = ""

        if "name" in __user__:
            result += f"Utilisateur: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"

        if result == "":
            result = "Utilisateur: Inconnu"

        return result

    def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        :return: The current time.
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A %d %B %Y")

        return f"Date et Heure Actuelles = {current_date}, {current_time}"

    def calculator(self, equation: str) -> str:
        """
        Calculate the result of an equation.
        :param equation: The equation to calculate.
        """
        try:
            result = eval(equation)
            return f"{equation} = {result}"
        except Exception as e:
            print(e)
            return "Équation invalide"

    def create_quote(
        self,
        customer_name: str,
        product_name: str,
        quantity: int,
        unit_price: float,
        __user__: dict = {},
    ) -> str:
        """
        Créer un nouveau devis dans le système autonome de saisie des devis.
        :param customer_name: Le nom du client demandant le devis.
        :param product_name: Le nom du produit ou service faisant l'objet du devis.
        :param quantity: La quantité d'articles dans le devis.
        :param unit_price: Le prix unitaire.
        :return: Message de confirmation avec les détails du devis.
        """
        try:
            # Generate quote ID
            quote_id = f"DV-{self.quote_counter}"
            self.quote_counter += 1

            # Calculate total
            subtotal = quantity * unit_price
            tax_rate = 0.20  # 20% TVA
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount

            # Get current timestamp
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Get user info
            sales_rep = __user__.get("name", "Inconnu")
            sales_rep_email = __user__.get("email", "N/A")

            # Create quote object
            quote = {
                "quote_id": quote_id,
                "customer_name": customer_name,
                "product_name": product_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total": total,
                "sales_rep": sales_rep,
                "sales_rep_email": sales_rep_email,
                "status": "En Attente",
                "created_at": timestamp,
                "valid_until": self._calculate_expiry_date(),
            }

            # Store in database
            self.quotes_db.append(quote)

            return f"""✅ Devis Créé avec Succès !

N° Devis: {quote_id}
Client: {customer_name}
Produit: {product_name}
Quantité: {quantity}
Prix Unitaire: {unit_price:.2f}€
---
Sous-total: {subtotal:.2f}€
TVA (20%): {tax_amount:.2f}€
Total: {total:.2f}€
---
Commercial: {sales_rep} ({sales_rep_email})
Statut: En Attente
Créé le: {timestamp}
Valable jusqu'au: {quote['valid_until']}

Le devis a été enregistré dans le système et est en attente d'approbation."""

        except Exception as e:
            return f"❌ Erreur lors de la création du devis: {str(e)}"

    def get_quote(self, quote_id: str) -> str:
        """
        Récupérer un devis du système autonome de saisie des devis.
        :param quote_id: L'identifiant unique du devis à récupérer.
        :return: Détails du devis ou message d'erreur.
        """
        try:
            for quote in self.quotes_db:
                if quote["quote_id"] == quote_id:
                    return f"""📄 Détails du Devis:

N° Devis: {quote['quote_id']}
Client: {quote['customer_name']}
Produit: {quote['product_name']}
Quantité: {quote['quantity']}
Prix Unitaire: {quote['unit_price']:.2f}€
---
Sous-total: {quote['subtotal']:.2f}€
TVA: {quote['tax_amount']:.2f}€
Total: {quote['total']:.2f}€
---
Commercial: {quote['sales_rep']}
Email: {quote['sales_rep_email']}
Statut: {quote['status']}
Créé le: {quote['created_at']}
Valable jusqu'au: {quote['valid_until']}"""

            return f"❌ Devis {quote_id} introuvable dans le système."

        except Exception as e:
            return f"❌ Erreur lors de la récupération du devis: {str(e)}"

    def list_quotes(self, status: str = "tous") -> str:
        """
        Lister tous les devis du système autonome de saisie des devis, filtrés optionnellement par statut.
        :param status: Filtrer les devis par statut (tous, en attente, approuvé, rejeté). Par défaut 'tous'.
        :return: Liste des devis ou message si aucun devis trouvé.
        """
        try:
            if not self.quotes_db:
                return "📭 Aucun devis dans le système pour le moment."

            filtered_quotes = self.quotes_db
            status_mapping = {
                "tous": "all",
                "en attente": "En Attente",
                "approuvé": "Approuvé",
                "rejeté": "Rejeté",
                "terminé": "Terminé",
            }

            if status.lower() != "tous":
                status_filter = status_mapping.get(status.lower(), status)
                filtered_quotes = [
                    q for q in self.quotes_db if q["status"] == status_filter
                ]

            if not filtered_quotes:
                return f"📭 Aucun devis trouvé avec le statut '{status}'."

            result = f"📋 Devis (Statut: {status}):\n\n"
            for quote in filtered_quotes:
                result += f"""• {quote['quote_id']} - {quote['customer_name']}
  Produit: {quote['product_name']} | Total: {quote['total']:.2f}€
  Statut: {quote['status']} | Créé le: {quote['created_at']}
---
"""
            return result

        except Exception as e:
            return f"❌ Erreur lors du listage des devis: {str(e)}"

    def update_quote_status(
        self, quote_id: str, new_status: str, __user__: dict = {}
    ) -> str:
        """
        Mettre à jour le statut d'un devis dans le système autonome de saisie des devis.
        :param quote_id: L'identifiant unique du devis à mettre à jour.
        :param new_status: Le nouveau statut (En Attente, Approuvé, Rejeté, Terminé).
        :return: Message de confirmation ou erreur.
        """
        try:
            valid_statuses = ["En Attente", "Approuvé", "Rejeté", "Terminé"]
            if new_status not in valid_statuses:
                return f"❌ Statut invalide. Doit être l'un des suivants: {', '.join(valid_statuses)}"

            for quote in self.quotes_db:
                if quote["quote_id"] == quote_id:
                    old_status = quote["status"]
                    quote["status"] = new_status
                    quote["updated_by"] = __user__.get("name", "Inconnu")
                    quote["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                    return f"""✅ Statut du Devis Mis à Jour !

N° Devis: {quote_id}
Client: {quote['customer_name']}
Changement de Statut: {old_status} → {new_status}
Mis à jour par: {quote['updated_by']}
Mis à jour le: {quote['updated_at']}"""

            return f"❌ Devis {quote_id} introuvable dans le système."

        except Exception as e:
            return f"❌ Erreur lors de la mise à jour du statut du devis: {str(e)}"

    def _calculate_expiry_date(self) -> str:
        """
        Méthode auxiliaire pour calculer la date d'expiration du devis (30 jours à partir d'aujourd'hui).
        """
        from datetime import timedelta

        expiry = datetime.now() + timedelta(days=30)
        return expiry.strftime("%d/%m/%Y")
