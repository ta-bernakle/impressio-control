# 📦 Control d'Impressió Digital - Gestió de Feines d'Impressió

## 📝 Descripció

Aplicació web per al control de feines d'impressió digital. Permet gestionar comandes setmanals, seguir l'estat de cada feina (Pendent/Imprès/Acabat), i visualitzar resums mensuals amb comparatives anuals.

## 🚀 Funcionalitats

| Funcionalitat | Descripció |
|---------------|------------|
| **Entrada ràpida** | Formulari amb navegació per TAB (Comanda, Client, Unitats, Descripció, Import, Pressupost) |
| **Autocompletat** | Suggeriments de clients basats en l'històric |
| **Estats visuals** | Pendent (🟡 groc), Imprès (⬜ blanc), Acabat (🟢 verd) |
| **Cerca** | Local (setmana actual) i Global (totes les setmanes) |
| **Edició** | Modificació de tots els camps d'una feina |
| **Eliminació** | Eliminació de feines amb confirmació |
| **Resum mensual** | Gràfic comparatiu any actual vs any anterior |
| **Indicador últim mes** | Comparativa ràpida de l'últim mes complet vs mateix mes any anterior |
| **Persistència** | SQLite amb dades importades de 2025 i 2026 |

## 🛠️ Tecnologies

- **Backend**: Flask (Python)
- **Base de dades**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Gràfics**: Chart.js
- **Servidor**: Debian (producció) / macOS (desenvolupament)

## 📂 Estructura del Projecte
appControlPrintsPython2026/
├── app.py # Backend Flask
├── impressio.db # Base de dades SQLite
├── templates/
│ └── index.html # Interfície d'usuari
├── venv/ # Entorn virtual (no inclòs al repo)
├── requirements.txt # Dependències
├── setmana_XX_YYYY.csv # Dades importades (opcional)
└── import_*.py # Scripts d'importació (opcional)

text

## 📊 Base de Dades (SQLite)

### Taula `feines`

| Camp | Tipus | Descripció |
|------|-------|------------|
| `id` | INTEGER | Clau primària |
| `comanda` | TEXT | Número de comanda |
| `client` | TEXT | Nom del client |
| `unitats` | INTEGER | Quantitat d'unitats |
| `descripcio` | TEXT | Descripció de la feina |
| `import` | REAL | Import en € |
| `pressupost` | TEXT | Text lliure sobre el pressupost |
| `estat` | INTEGER | 1=Pendent, 2=Imprès, 3=Acabat |
| `data_entrada` | DATE | Data d'entrada de la feina |
| `created_at` | TIMESTAMP | Data de creació del registre |

## 🔧 Instal·lació

### 1. Clonar el repositori
```bash
git clone https://github.com/ta-bernakle/impressio-control.git
cd impressio-control
2. Crear entorn virtual
bash
python3 -m venv venv
source venv/bin/activate
3. Instal·lar dependències
bash
pip install flask pandas gunicorn
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
User=santi
Group=santi
WorkingDirectory=/home/santi/impressio-control
Environment="PATH=/home/santi/impressio-control/venv/bin"
ExecStart=/home/santi/impressio-control/venv/bin/gunicorn -w 4 -b 0.0.0.0:5007 app:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
bash
sudo systemctl enable impressio
sudo systemctl start impressio
🔧 Configuració
Paràmetre	Valor	Descripció
Port	5007	Port del servidor Flask
Host	0.0.0.0	Escolta a totes les interfícies
Debug	False	Mode producció (canviar a True per desenvolupament)
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
0 3 * * * cp /home/santi/impressio-control/impressio.db /home/santi/backups/impressio_$(date +\%Y\%m\%d).db
🔌 API Endpoints
Mètode	Endpoint	Descripció
GET	/api/feines	Obtenir feines d'una setmana (paràmetres: setmana, any)
POST	/api/feines	Crear una nova feina
PUT	/api/feines/<id>	Actualitzar totes les dades d'una feina
PUT	/api/feines/<id>/estat	Actualitzar només l'estat d'una feina
DELETE	/api/feines/<id>	Eliminar una feina
GET	/api/resum_mensual	Obtenir dades per al gràfic mensual (paràmetre: any)
GET	/api/ultim_mes	Obtenir comparativa de l'últim mes complet (paràmetre: any)
GET	/api/autocompletar	Suggeriments per autocompletar clients (paràmetre: client)
GET	/api/cerca	Cerca global (paràmetres: q, limit)
🎨 Personalització
Colors d'estat
A index.html, secció <style>:

css
.estat-pendent { background-color: #ffeb3b !important; font-weight: bold; color: #000 !important; }
.estat-impres { background-color: white !important; color: #000 !important; }
.estat-acabat { background-color: #c8e6c9 !important; color: #000 !important; }
Noms dels mesos
A app.py, funció ultim_mes():

python
noms_mesos = {
    '01': 'Gener', '02': 'Febrer', '03': 'Març', '04': 'Abril',
    '05': 'Maig', '06': 'Juny', '07': 'Juliol', '08': 'Agost',
    '09': 'Setembre', '10': 'Octubre', '11': 'Novembre', '12': 'Desembre'
}
🔧 PROBLEMES CONEGUTS I SOLUCIONS
1. Línies buides a la taula (Pèrdua de dades)
🔍 Símptoma
Quan es canvia l'estat d'una feina a "Imprès" o "Acabat", la línia es queda en blanc, perdent el text i posant 0 a Unitats i Import.

🎯 Causa
La funció canviarEstat() enviava una petició PUT a /api/feines/<id> amb només { estat: X }. Això feia que el backend, en rebre camps buits, els sobreescrigués a la BD amb valors buits ('' i 0).

✅ Solució
Separar les rutes d'actualització:

PUT /api/feines/<id> → per actualitzar TOTES les dades (edició completa)

PUT /api/feines/<id>/estat → per actualitzar NOMÉS l'estat (selector d'estat)

Backend (app.py):

python
@app.route('/api/feines/<int:id>/estat', methods=['PUT'])
def actualitzar_estat(id):
    data = request.json
    nou_estat = data.get('estat')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE feines SET estat = ? WHERE id = ?', (nou_estat, id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
Frontend (index.html):

javascript
function canviarEstat(id, nouEstat) {
    fetch(`/api/feines/${id}/estat`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ estat: parseInt(nouEstat) })
    })
    .then(() => carregarSetmana());
}
2. El text de les línies no es veu (blanc sobre blanc)
🔍 Símptoma
Les línies amb estat "Imprès" o "Acabat" tenen el text invisible (blanc sobre blanc).

🎯 Causa
El CSS no té definit el color del text per a aquests estats, i el navegador el té en cache.

✅ Solució
Afegir color: #000 !important; a tots els estats al CSS de index.html:

css
.estat-pendent {
    background-color: #ffeb3b !important;
    font-weight: bold;
    color: #000 !important;
}
.estat-impres {
    background-color: white !important;
    color: #000 !important;
}
.estat-acabat {
    background-color: #c8e6c9 !important;
    color: #000 !important;
    font-weight: 600 !important;
}
Per forçar la recàrrega del CSS al navegador: Cmd+Shift+R (recàrrega forçada) o netejar la cache.

3. Autocompletat no funciona
🔍 Símptoma
Quan s'escriu un client al camp "Client", no apareixen suggeriments.

🎯 Causa
L'endpoint /api/autocompletar no està retornant resultats perquè la cerca no troba coincidències amb caràcters especials o accents.

✅ Solució
Assegurar que la cerca a la BD utilitza LIKE amb % i que la codificació és correcta (UTF-8).

python
cursor.execute('''
    SELECT comanda, client, descripcio, pressupost, import
    FROM feines
    WHERE client LIKE ?
    ORDER BY data_entrada DESC
    LIMIT 10
''', (f'%{client}%',))
4. Cerca global no retorna resultats
🔍 Símptoma
Quan es cerca a "Totes les setmanes", no apareixen resultats.

🎯 Causa
L'endpoint /api/cerca té un límit de 200 resultats o la cerca no està ben configurada.

✅ Solució
Augmentar el límit i assegurar que la cerca es fa a tots els camps:

python
@app.route('/api/cerca', methods=['GET'])
def cerca_feines():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'feines': [], 'total': 0})
    
    cursor.execute('''
        SELECT id, comanda, client, unitats, descripcio, import, pressupost, estat, data_entrada,
               strftime('%W', data_entrada) AS setmana,
               strftime('%Y', data_entrada) AS any
        FROM feines
        WHERE client LIKE ? OR descripcio LIKE ? OR comanda LIKE ?
        ORDER BY data_entrada DESC
        LIMIT 500
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
5. La BD no es carrega al Debian
🔍 Símptoma
L'aplicació no mostra dades al Debian, però al desenvolupament local sí.

🎯 Causa
La base de dades impressio.db no està al servidor Debian (no es puja a GitHub pel .gitignore).

✅ Solució
Copiar la BD des de local al Debian:

bash
scp -P 55555 ~/appControlPrintsPython2026/impressio.db santi@192.168.1.66:/home/santi/impressio-control/
O reimportar les dades des dels CSVs al Debian.

📝 Llicència
Projecte privat — Ús intern de l'empresa.

🤝 Contacte
Per a dubtes o millores, contacta amb l'administrador del sistema.

Última actualització: 07/07/2026
