import tidalapi
import requests
from deezer import Client 
import time
import json
import re
import sys # Pour quitter proprement

# ===============================
# CONFIGURATION ET PRÉPARATION
# ===============================
def setup_and_get_config():
    """
    Récupère l'ARL Deezer et les préférences de l'utilisateur de manière interactive.
    """
    print("--- 🎶 Configuration de la Migration Deezer vers TIDAL 🎶 ---")
    
    # 1. Récupération de l'ARL
    deezer_arl = input("Veuillez entrer votre cookie ARL Deezer (il est long et sensible) : ").strip()
    if not deezer_arl:
        print("❌ L'ARL ne peut pas être vide. Arrêt du script.")
        sys.exit(1)

    # 2. Demande de confirmation pour la suppression
    while True:
        confirm_delete = input(
            "Voulez-vous **SUPPRIMER TOUTES** vos playlists TIDAL actuelles avant de commencer le transfert ? (O/N) : "
        ).strip().upper()
        if confirm_delete in ('O', 'N'):
            should_delete = confirm_delete == 'O'
            break
        else:
            print("Veuillez répondre par 'O' (Oui) ou 'N' (Non).")
            
    print("-" * 50)
    return deezer_arl, should_delete

# Exécution de la configuration interactive
DEEZER_ARL, SHOULD_DELETE_TIDAL = setup_and_get_config()

# --- Connexion à Tidal ---
print("Connexion à Tidal… (Veuillez suivre les instructions du navigateur pour l'authentification)")
tidal_session = tidalapi.Session()
# Tente de se connecter
try:
    tidal_session.login_oauth_simple()
except Exception as e:
    print(f"❌ Erreur de connexion TIDAL : {e}. Assurez-vous d'avoir entré le code dans le navigateur correctement.")
    sys.exit(1)

print(f"✅ Connecté à Tidal. Utilisateur: {tidal_session.user.username}")

# --- Client Deezer officiel (avec header ARL) ---
dz_client = Client(headers={"Cookie": f"arl={DEEZER_ARL}"})
print("Initialisation du client Deezer...")

# ===============================
# FONCTIONS DEEZER
# ===============================
def get_deezer_user_info_and_playlists(deezer_arl):
    session = requests.Session()
    session.headers.update({"Cookie": f"arl={deezer_arl}"})

    resp = session.get(
        "https://www.deezer.com/ajax/gw-light.php",
        params={
            "method": "deezer.getUserData",
            "api_version": "1.0",
            "api_token": ""
        }
    )
    user_data = resp.json()
    
    if "results" not in user_data or "USER" not in user_data["results"]:
        raise Exception("Impossible de récupérer l’ID utilisateur Deezer. Vérifiez l'ARL.")

    user_id = user_data["results"]["USER"]["USER_ID"]
    print(f"✅ Connecté à Deezer — ID utilisateur : {user_id}")
    
    print("Récupération des playlists Deezer...")
    try:
        deezer_user = dz_client.get_user(user_id)
        user_playlists = deezer_user.get_playlists()
    except Exception as e:
         raise Exception(f"Erreur lors de la récupération des playlists Deezer: {e}")

    playlists = [{"id": pl.id, "title": pl.title} for pl in user_playlists]
    return playlists

def get_deezer_playlist_tracks(playlist_id):
    playlist = dz_client.get_playlist(playlist_id)
    tracks = [f"{t.artist.name} {t.title}" for t in playlist.tracks]
    return tracks

# ===============================
# FONCTIONS TIDAL
# =================================

def create_tidal_playlist(title, description=""):
    safe_title = title[:100]
    try:
        pl = tidal_session.user.create_playlist(safe_title, description)
        
        if pl is None:
             raise Exception("create_playlist a retourné None. Problème d'authentification ou d'API.")
             
        return pl
    except Exception as e:
        print(f"❌ Erreur lors de la création de la playlist Tidal '{title}': {e}")
        return None

def search_tidal_track(track_name):
    results = tidal_session.search(track_name, limit=1)
    tracks_list = results.get('tracks', [])
    
    if tracks_list and isinstance(tracks_list[0], tidalapi.media.Track):
        return tracks_list[0] 
        
    return None

def add_tracks_to_tidal_playlist(playlist, tracks):
    track_ids_to_add = []
    print(f"  🔍 Recherche de {len(tracks)} pistes...")
    
    for track_name in tracks:
        track = search_tidal_track(track_name)
        if track:
            track_ids_to_add.append(track.id)
        else:
            print(f"  ⚠️ Non trouvé sur TIDAL : {track_name}")

    if track_ids_to_add:
        try:
            playlist.add(track_ids_to_add)
            print(f"  👍 Ajout de {len(track_ids_to_add)} pistes réussi.")
        except Exception as e:
            print(f"  ❌ Erreur lors de l'ajout des pistes en bloc : {e}")
    else:
        print("  Aucune piste trouvée ou ajoutée à la playlist.")

def delete_all_tidal_playlists(session):
    """
    Supprime toutes les playlists créées par l'utilisateur sur Tidal.
    """
    print("\n--- Démarrage de la SUPPRESSION TOTALE des playlists TIDAL ---")
    user = session.user
    
    try:
        all_playlists = user.playlists() 
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des playlists pour la suppression : {e}")
        return

    if not all_playlists:
        print("✅ Aucune playlist TIDAL trouvée à supprimer. Base propre.")
        return

    print(f"🛑 {len(all_playlists)} playlists TIDAL trouvées. Suppression en cours...")
    
    deleted_count = 0
    for pl in all_playlists:
        try:
            pl.delete()
            print(f"   🗑️ Supprimé : {pl.name}")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Erreur lors de la suppression de '{pl.name}' : {e}")

    print(f"--- Suppression totale terminée. {deleted_count} playlists effacées. ---")


# ===============================
# EXECUTION DE LA MIGRATION
# ===============================
try:
    print("\n--- Démarrage de la migration Deezer vers Tidal ---\n")
    
    # Étape 1: Nettoyage conditionnel
    if SHOULD_DELETE_TIDAL:
        delete_all_tidal_playlists(tidal_session)
    else:
        print("ℹ️ Le nettoyage des playlists TIDAL a été ignoré.")
        
    # Étape 2: Récupération des données Deezer
    deezer_playlists = get_deezer_user_info_and_playlists(DEEZER_ARL)
    
    if not deezer_playlists:
        print("🛑 Aucune playlist Deezer récupérée. Fin du script.")
    else:
        print(f"✅ {len(deezer_playlists)} playlists Deezer trouvées. Démarrage du transfert...")
        
        # Étape 3: Boucle de Transfert
        for pl in deezer_playlists:
            deezer_title = pl['title']
            
            # Gestion de la reprise et de l'anti-doublon (si la suppression n'a pas été faite)
            try:
                print(f"\n🎵 Traitement de la playlist : **{deezer_title}**")

                # Si l'utilisateur n'a pas voulu effacer, on vérifie l'existence pour éviter les doublons.
                if not SHOULD_DELETE_TIDAL:
                    existing_pl = tidal_session.user.get_playlist_by_name(deezer_title)
                    if existing_pl:
                        print(f"⚠️ Playlist '{deezer_title}' existe déjà. **Transfert ignoré**.")
                        continue


                tidal_pl = create_tidal_playlist(deezer_title)
                
                if tidal_pl:
                    tracks = get_deezer_playlist_tracks(pl['id'])
                    if tracks:
                        add_tracks_to_tidal_playlist(tidal_pl, tracks)
                        print(f"✓ Playlist terminée : **{tidal_pl.name}**")
                    else:
                        print(f"⚠️ Playlist Deezer '{deezer_title}' vide. Création de la playlist Tidal mais elle restera vide.")
                else:
                    print(f"❌ Saut de la playlist '{deezer_title}' en raison d'une erreur de création Tidal.")
            
            except requests.exceptions.SSLError as e:
                 # Gestion de la perte de connexion (SSL)
                 print(f"\n🛑 ERREUR SSL sur la playlist '{deezer_title}'. Connexion perdue. Attente de 5 secondes...")
                 time.sleep(5)
                 print("Reprise du traitement à la prochaine playlist.")
                 continue # Passe à la prochaine playlist

except Exception as e:
    print(f"\n💥 ERREUR CRITIQUE : {e}")

print("\n--- Fin du script de migration ---")
