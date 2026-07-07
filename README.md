📦 Control d'Impressió Digital - Gestió de Feines d'Impressió
📝 Descripció
Aplicació web per al control de feines d'impressió digital. Permet gestionar comandes setmanals, seguir l'estat de cada feina (Pendent/Imprès/Acabat), i visualitzar resums mensuals amb comparatives anuals.

🚀 Funcionalitats
Funcionalitat	Descripció
Entrada ràpida	Formulari amb navegació per TAB (Comanda, Client, Unitats, Descripció, Import, Pressupost)
Autocompletat	Suggeriments de clients basats en l'històric
Estats visuals	Pendent (🟡 groc), Imprès (⬜ blanc), Acabat (🟢 verd)
Cerca	Local (setmana actual) i Global (totes les setmanes)
Edició	Modificació de tots els camps d'una feina
Eliminació	Eliminació de feines amb confirmació
Resum mensual	Gràfic comparatiu any actual vs any anterior
Indicador últim mes	Comparativa ràpida de l'últim mes complet vs mateix mes any anterior
Persistència	SQLite amb dades importades de 2025 i 2026
🛠️ Tecnologies
Backend: Flask (Python)

Base de dades: SQLite

Frontend: HTML, CSS, JavaScript

Gràfics: Chart.js

Servidor: Debian (producció) / macOS (desenvolupament)

📂 Estructura del Projecte
text
appControlPrintsPython2026/
├── app.py                     # Backend Flask
├── impressio.db               # Base de dades SQLite
├── templates/
│   └── index.html             # Interfície d'usuari
├── venv/                      # Entorn virtual (no inclòs al repo)
├── requirements.txt           # Dependències
├── setmana_XX_YYYY.csv        # Dades importades (opcional)
└── import_*.py                # Scripts d'importació (opcional)
📊 Base de Dades (SQLite)
Taula feines
Camp	Tipus	Descripció
id	INTEGER	Clau primària
comanda	TEXT	Número de comanda
client	TEXT	Nom del client
unitats	INTEGER	Quantitat d'unitats
descripcio	TEXT	Descripció de la feina
import	REAL	Import en €
pressupost	TEXT	Text lliure sobre el pressupost
estat	INTEGER	1=Pendent, 2=Imprès, 3=Acabat
data_entrada	DATE	Data d'entrada de la feina
created_at	TIMESTAMP	Data de creació del registre
🔧 Instal·lació
1. Clonar el repositori
bash
git clone <url-del-repositori>
cd appControlPrintsPython2026
2. Crear entorn virtual
bash
python3 -m venv venv
source venv/bin/activate
3. Instal·lar dependències
bash
pip install flask pandas
4. Executar l'aplicació
bash
python3 app.py
5. Accedir des del navegador
text
http://localhost:5007
🖥️ Desplegament a producció (Debian)
Opció 1: Execució directa (prova)
bash
python3 app.py
Opció 2: Amb Gunicorn (producció)
bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5007 app:app
Opció 3: Servei systemd (auto-inici)
bash
sudo nano /etc/systemd/system/impressio.service
ini
[Unit]
Description=Control d'Impressió Digital
After=network.target

[Service]
User=annasellares
WorkingDirectory=/home/annasellares/appControlPrintsPython2026
ExecStart=/home/annasellares/appControlPrintsPython2026/venv/bin/gunicorn -w 4 -b 0.0.0.0:5007 app:app
Restart=always

[Install]
WantedBy=multi-user.target
bash
sudo systemctl enable impressio
sudo systemctl start impressio
🔧 Configuració
Paràmetre	Valor	Descripció
Port	5007	Port del servidor Flask
Host	0.0.0.0	Escolta a totes les interfícies
Debug	True	Mode desenvolupament (canviar a False en producció)
BD	impressio.db	Nom de la base de dades SQLite
Canviar el port
A app.py:

python
app.run(debug=True, host='0.0.0.0', port=5007)
📥 Importació de dades
Des de CSV
Els fitxers CSV han de tenir el format:

text
setmana_XX_YYYY.csv
On XX és el número de setmana (1-52) i YYYY l'any.

Exemples:

setmana_01_2025.csv

setmana_02_2025.csv

setmana_27_2026.csv

Scripts d'importació disponibles
import_excel_netejat_v2.py: Importa una setmana específica

import_setmanari_totes.py: Importa només el client "SETMANARI TORELLÓ" de totes les setmanes

importar_totes.py: Importa totes les setmanes d'un any

🗄️ Backup
Backup manual
bash
cp impressio.db impressio_backup_$(date +%Y%m%d).db
Backup automàtic (cron)
Afegir a crontab -e:

bash
0 3 * * * cp /home/annasellares/appControlPrintsPython2026/impressio.db /home/annasellares/backups/impressio_$(date +\%Y\%m\%d).db
🔌 API Endpoints
Mètode	Endpoint	Descripció
GET	/api/feines	Obtenir feines d'una setmana (paràmetres: setmana, any)
POST	/api/feines	Crear una nova feina
PUT	/api/feines/<id>	Actualitzar totes les dades d'una feina
DELETE	/api/feines/<id>	Eliminar una feina
GET	/api/resum_mensual	Obtenir dades per al gràfic mensual (paràmetre: any)
GET	/api/ultim_mes	Obtenir comparativa de l'últim mes complet (paràmetre: any)
GET	/api/autocompletar	Suggeriments per autocompletar clients (paràmetre: client)
GET	/api/cerca	Cerca global (paràmetres: q, limit)
🎨 Personalització
Colors d'estat
A index.html, secció <style>:

css
.estat-pendent { background-color: #ffeb3b !important; font-weight: bold; }
.estat-impres { background-color: white !important; }
.estat-acabat { background-color: #c8e6c9 !important; }
Noms dels mesos
A app.py, funció ultim_mes():

python
noms_mesos = {
    '01': 'Gener', '02': 'Febrer', '03': 'Març', '04': 'Abril',
    '05': 'Maig', '06': 'Juny', '07': 'Juliol', '08': 'Agost',
    '09': 'Setembre', '10': 'Octubre', '11': 'Novembre', '12': 'Desembre'
}
❓ Solució de problemes
Error: ModuleNotFoundError: No module named 'flask'
bash
source venv/bin/activate
pip install flask pandas
Error: Port 5007 ja està en ús
bash
# Canviar el port a app.py
app.run(debug=True, host='0.0.0.0', port=5008)
Error: TemplateNotFound
bash
# Assegura't que templates/index.html existeix
ls -la templates/
Error de permisos a Debian
bash
sudo chown -R $USER:$USER ~/appControlPrintsPython2026/
📝 Llicència
Projecte privat — Ús intern de l'empresa.

🤝 Contacte
Per a dubtes o millores, contacta amb l'administrador del sistema.

Última actualització: 07/07/2026
