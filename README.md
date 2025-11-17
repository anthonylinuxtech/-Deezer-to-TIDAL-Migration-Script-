# 🌊 Deezer-to-TIDAL Migration Script 🎶
Ce script Python permet de transférer automatiquement toutes vos playlists Deezer vers votre compte TIDAL. Il a été optimisé pour être résilient face aux erreurs d'API et offre un mode interactif pour simplifier l'utilisation.

## ✨ Fonctionnalités

* **Migration Complète :** Transfère toutes les playlists Deezer vers TIDAL.
* **Recherche Optimisée :** Utilise les titres et artistes pour trouver la meilleure correspondance sur TIDAL.
* **Nettoyage Conditionnel :** Demande à l'utilisateur s'il souhaite supprimer toutes ses playlists TIDAL existantes avant le transfert, garantissant une migration propre.
* **Résilience Réseau :** Gère les interruptions de connexion (erreurs SSL/Timeout) pour reprendre le transfert.
* **Mode Interactif :** Aucune modification du code requise ; l'utilisateur fournit les informations via la console.

## 🛠️ Pré-requis

Vous devez avoir Python (version 3.6 ou supérieure) installé sur votre système.

### 📦 Installation des dépendances

Le script utilise trois bibliothèques principales : `tidalapi`, `requests` et `deezer-python`.

Ouvrez votre terminal ou invite de commande et exécutez la commande suivante :

```bash
pip install tidalapi requests deezer-python
```
## 🔑 Comment obtenir votre ARL Deezer
Le script utilise le cookie arl pour s'authentifier auprès de Deezer sans avoir besoin de mot de passe ou d'API Key. Ce cookie est sensible et est la clé de votre session.
1.	Connectez-vous à votre compte Deezer sur votre navigateur web.
2.	Ouvrez les Outils de Développement (généralement en appuyant sur F12 sur Windows/Linux ou Cmd+Option+I sur Mac).
3.	Allez dans l'onglet Application (ou Stockage / Storage).
4.	Dans le menu de gauche, développez Cookies et cliquez sur https://www.deezer.com.
