import os
from dotenv import load_dotenv
from pathlib import Path

def update_proxy_links(m3u8_filepath, env_filepath):
    """
    Aggiorna i link nel file m3u8 utilizzando un URL base e pattern configurabili da un file .env.
    """
    # Carica le variabili dal file .env specificato
    load_dotenv(dotenv_path=env_filepath)

    # Ottieni le configurazioni dal file .env
    proxy_base_url = os.getenv("MPDPROXYMFP")

    # Validazione delle variabili d'ambiente necessarie
    if not proxy_base_url:
        print(f"Errore: La variabile PROXYMFPMPD non è stata trovata nel file {env_filepath}")
        return

    print(f"Utilizzo del proxy base URL: {proxy_base_url}")

    # Configurazione per le sostituzioni
    from urllib.parse import urlparse
    proxy_url_parts = urlparse(proxy_base_url)
    proxy_hostname = f"{proxy_url_parts.scheme}://{proxy_url_parts.hostname}:{proxy_url_parts.port}"
    placeholder = "{MPDPROXYMFP}"
    
    lines_to_write = []
    updated_count = 0
    m3u8_path = Path(m3u8_filepath)

    try:
        with open(m3u8_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_number, original_line in enumerate(lines, 1):
            stripped_line = original_line.strip()
            processed_line = original_line

            if not stripped_line or stripped_line.startswith("#"):
                lines_to_write.append(original_line)
                continue
            
            modified_content = stripped_line
            
            # Caso 1: Sostituisci il placeholder se presente
            if placeholder in stripped_line:
                modified_content = stripped_line.replace(placeholder, proxy_base_url.rstrip('/'))
                if modified_content != stripped_line:
                    processed_line = modified_content + '\n'
                    updated_count += 1
            
            # Caso 2: Aggiorna l'hostname negli URL esistenti
            elif "proxy/mpd/manifest.m3u8" in stripped_line:
                current_url_parts = urlparse(stripped_line.split("?")[0])
                if current_url_parts.hostname and current_url_parts.port:  # Verifica che l'URL sia valido
                    current_hostname = f"{current_url_parts.scheme}://{current_url_parts.hostname}:{current_url_parts.port}"
                    if current_hostname != proxy_hostname:
                        modified_content = stripped_line.replace(current_hostname, proxy_hostname)
                        if modified_content != stripped_line:
                            processed_line = modified_content + '\n'
                            updated_count += 1
                    
            lines_to_write.append(processed_line)


        # Scrivi le modifiche nello stesso file
        with open(m3u8_path, 'w', encoding='utf-8') as f:
            f.writelines(lines_to_write)

        if updated_count > 0:
            print(f"File {m3u8_path.name} aggiornato con successo. {updated_count} link modificati.")
        else:
            print(f"Nessun link da aggiornare trovato in {m3u8_path.name} con i criteri specificati.")

    except FileNotFoundError:
        print(f"Errore: Il file {m3u8_path} non è stato trovato.")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

if __name__ == "__main__":
    import sys
    
    # Definisci i percorsi relativi allo script
    script_dir = Path(__file__).resolve().parent
    
    # Usa il file specificato come argomento o usa mpd.m3u8 come default
    m3u8_filename = sys.argv[1] if len(sys.argv) > 1 else "mpd.m3u8"
    m3u8_file = script_dir / m3u8_filename
    env_file = script_dir / ".env"      # Assumendo che .env sia nella stessa cartella

    update_proxy_links(m3u8_file, env_file)
