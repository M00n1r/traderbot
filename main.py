import requests
import subprocess

# URL du fichier à récupérer
url = "https://raw.githubusercontent.com/M00n1r/traderbot/main/traderbot.py"

try:
    # Récupération du contenu du fichier
    response = requests.get(url)

    # Enregistrement du contenu dans un fichier local
    with open("traderbot.py", "wb") as f:
        f.write(response.content)

    # Exécution du fichier avec des arguments
    subprocess.run(["python", "traderbot.py", "1d", "BTCUSDT"])

except requests.exceptions.RequestException as e:
    print("Error while downloading traderbot.py : ", e)

except subprocess.CalledProcessError as e:
    print("Error while executing traderbot.py : ", e)
