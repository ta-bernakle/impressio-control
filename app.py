# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('impressio.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/feines', methods=['GET'])
def get_feines():
    setmana = request.args.get('setmana', type=int)
    any = request.args.get('any', type=int, default=2026)
    
    if not setmana:
        today = datetime.now()
        setmana = today.isocalendar()[1]
        any = today.year
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            id,
            comanda,
            client,
            unitats,
            descripcio,
            import,
            pressupost,
            estat,
            data_entrada
        FROM feines
        WHERE strftime('%Y', data_entrada) = ?
          AND strftime('%W', data_entrada) = ?
        ORDER BY id
    ''', (str(any), f'{setmana:02d}'))
    
    feines = cursor.fetchall()
    conn.close()
    
    resultat = []
    for row in feines:
        # Calcular preu per miler (si unitats > 0)
        unitats = row['unitats']
        import_valor = row['import']
        preu_miler = (import_valor / unitats * 1000) if unitats > 0 else 0.0
        
        resultat.append({
            'id': row['id'],
            'comanda': row['comanda'],
            'client': row['client'],
            'unitats': unitats,
            'descripcio': row['descripcio'],
            'import': import_valor,
            'preu_miler': round(preu_miler, 2),
            'pressupost': row['pressupost'],
            'estat': row['estat'],
            'data_entrada': row['data_entrada']
        }) 

    primer_dia = datetime(any, 1, 1)
    if primer_dia.weekday() != 0:
        dies_fins_dilluns = (7 - primer_dia.weekday()) % 7
        primer_dilluns = primer_dia + timedelta(days=dies_fins_dilluns)
    else:
        primer_dilluns = primer_dia
    
    data_inici = primer_dilluns + timedelta(weeks=setmana-1)
    data_fi = data_inici + timedelta(days=6)
    
    return jsonify({
        'feines': resultat,
        'setmana': setmana,
        'any': any,
        'data_inici': data_inici.strftime('%d/%m/%Y'),
        'data_fi': data_fi.strftime('%d/%m/%Y')
    })

@app.route('/api/feines', methods=['POST'])
def crear_feina():
    data = request.json
    
    # 🔧 VALIDACIÓ: Rebutjar dades buides
    client = data.get('client', '').strip()
    descripcio = data.get('descripcio', '').strip()
    
    if not client or client == '':
        return jsonify({'error': 'El camp "Client" és obligatori'}), 400
    
    if not descripcio or descripcio == '':
        return jsonify({'error': 'El camp "Descripció" és obligatori'}), 400
    
    unitats = data.get('unitats', 0)
    if unitats <= 0:
        return jsonify({'error': 'El camp "Unitats" ha de ser un número positiu'}), 400
    
    import_valor = data.get('import', 0.0)
    if import_valor <= 0:
        return jsonify({'error': 'El camp "Import" ha de ser un número positiu'}), 400
    
    # Obtenir la setmana i any del formulari
    setmana = data.get('setmana')
    any = data.get('any')
    
    if not setmana or not any:
        data_entrada = datetime.now().strftime('%Y-%m-%d')
    else:
        primer_dia = datetime(int(any), 1, 1)
        if primer_dia.weekday() != 0:
            dies_fins_dilluns = (7 - primer_dia.weekday()) % 7
            primer_dilluns = primer_dia + timedelta(days=dies_fins_dilluns)
        else:
            primer_dilluns = primer_dia
        
        data_inici = primer_dilluns + timedelta(weeks=int(setmana)-1)
        data_entrada = data_inici.strftime('%Y-%m-%d')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO feines 
        (comanda, client, unitats, descripcio, import, pressupost, estat, data_entrada)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('comanda', '').strip(),
        client,
        unitats,
        descripcio,
        import_valor,
        data.get('pressupost', '').strip(),
        1,  # Estat: Pendent
        data_entrada
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/feines/<int:id>/estat', methods=['PUT'])
def actualitzar_estat(id):
    """Actualitza només l'estat d'una feina"""
    data = request.json
    nou_estat = data.get('estat')
    if nou_estat is None:
        return jsonify({'error': 'Estat no proporcionat'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE feines SET estat = ? WHERE id = ?', (nou_estat, id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/feines/<int:id>', methods=['PUT'])
def actualitzar_feina(id):
    """Actualitza totes les dades d'una feina"""
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "UPDATE feines SET comanda = ?, client = ?, unitats = ?, descripcio = ?, import = ?, pressupost = ?, estat = ? WHERE id = ?"
    
    cursor.execute(sql, (
        data.get('comanda', ''),
        data.get('client', ''),
        data.get('unitats', 0),
        data.get('descripcio', ''),
        data.get('import', 0.0),
        data.get('pressupost', ''),
        data.get('estat', 1),
        id
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/feines/<int:id>', methods=['DELETE'])
def eliminar_feina(id):
    """Elimina una feina"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM feines WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/resum_mensual', methods=['GET'])
def resum_mensual():
    any = request.args.get('any', type=int, default=2026)
    any_anterior = any - 1
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            strftime('%m', data_entrada) AS mes,
            SUM(import) AS total
        FROM feines
        WHERE strftime('%Y', data_entrada) = ?
            AND estat IN (2, 3)
        GROUP BY mes
        ORDER BY mes
    ''', (str(any),))
    
    any_actual = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute('''
        SELECT 
            strftime('%m', data_entrada) AS mes,
            SUM(import) AS total
        FROM feines
        WHERE strftime('%Y', data_entrada) = ?
            AND estat IN (2, 3)
        GROUP BY mes
        ORDER BY mes
    ''', (str(any_anterior),))
    
    any_anterior_dict = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    mesos = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    noms_mesos = ['Gen', 'Feb', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Des']
    
    dades_any_actual = [any_actual.get(mes, 0) for mes in mesos]
    dades_any_anterior = [any_anterior_dict.get(mes, 0) for mes in mesos]
    
    return jsonify({
        'mesos': noms_mesos,
        'any_actual': dades_any_actual,
        'any_anterior': dades_any_anterior,
        'any_actual_nom': str(any),
        'any_anterior_nom': str(any_anterior)
    })

@app.route('/api/ultim_mes', methods=['GET'])
def ultim_mes():
    """Retorna la comparativa de l'últim mes complet amb l'any anterior"""
    any = request.args.get('any', type=int, default=2026)
    any_anterior = any - 1
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Trobar l'últim mes COMPLET (que ja ha acabat)
    # Només considerem mesos anteriors al mes actual
    avui = datetime.now()
    mes_actual = avui.month
    any_actual = avui.year
    
    # Construir la condició: només mesos complets (anteriors al mes actual)
    if any == any_actual:
        # Per a l'any actual, només mesos < mes_actual
        condicio_mes = f"AND CAST(strftime('%m', data_entrada) AS INTEGER) < {mes_actual}"
    else:
        # Per a anys anteriors, tots els mesos són complets
        condicio_mes = ""
    
    cursor.execute(f'''
        SELECT 
            strftime('%Y-%m', data_entrada) AS mes,
            strftime('%m', data_entrada) AS mes_num,
            COUNT(*) AS total_feines,
            SUM(import) AS total_import
        FROM feines
        WHERE strftime('%Y', data_entrada) = ?
            AND estat IN (2, 3)
            {condicio_mes}
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT 1
    ''', (str(any),))
    
    ultim_mes = cursor.fetchone()
    
    if not ultim_mes:
        # Si no hi ha mesos complets, buscar l'últim mes amb dades (per defecte)
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', data_entrada) AS mes,
                strftime('%m', data_entrada) AS mes_num,
                COUNT(*) AS total_feines,
                SUM(import) AS total_import
            FROM feines
            WHERE strftime('%Y', data_entrada) = ?
                AND estat IN (2, 3)
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT 1
        ''', (str(any),))
        ultim_mes = cursor.fetchone()
    
    if not ultim_mes:
        return jsonify({
            'error': 'No hi ha dades per a l\'any seleccionat',
            'mes': None,
            'any': any,
            'any_anterior': any_anterior
        })
    
    mes_actual_str = ultim_mes[1]  # 'MM'
    total_actual = ultim_mes[3] or 0
    mes_nom = ultim_mes[0]  # 'YYYY-MM'
    feines_actual = ultim_mes[2]
    
    # Buscar el mateix mes de l'any anterior
    cursor.execute('''
        SELECT 
            SUM(import) AS total_import,
            COUNT(*) AS total_feines
        FROM feines
        WHERE strftime('%Y', data_entrada) = ?
            AND strftime('%m', data_entrada) = ?
            AND estat IN (2, 3)
    ''', (str(any_anterior), mes_actual_str))
    
    mes_anterior = cursor.fetchone()
    total_anterior = mes_anterior[0] or 0
    feines_anterior = mes_anterior[1] or 0
    
    conn.close()
    
    # Càlculs
    diferencia = total_actual - total_anterior
    percent = (diferencia / total_anterior * 100) if total_anterior > 0 else 0
    
    # Noms dels mesos en català
    noms_mesos = {
        '01': 'Gener', '02': 'Febrer', '03': 'Març', '04': 'Abril',
        '05': 'Maig', '06': 'Juny', '07': 'Juliol', '08': 'Agost',
        '09': 'Setembre', '10': 'Octubre', '11': 'Novembre', '12': 'Desembre'
    }
    
    return jsonify({
        'mes': mes_nom,
        'mes_nom': noms_mesos.get(mes_actual_str, mes_actual_str),
        'mes_num': mes_actual_str,
        'any': any,
        'any_anterior': any_anterior,
        'total_actual': total_actual,
        'total_anterior': total_anterior,
        'feines_actual': feines_actual,
        'feines_anterior': feines_anterior,
        'diferencia': diferencia,
        'percent': percent,
        'tendencia': 'positiva' if diferencia > 0 else 'negativa' if diferencia < 0 else 'neutral'
    })

@app.route('/api/autocompletar', methods=['GET'])
def autocompletar():
    client = request.args.get('client', '')
    
    if not client or len(client) < 2:
        return jsonify([])
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            comanda,
            client,
            descripcio,
            pressupost,
            import
        FROM feines
        WHERE client LIKE ?
        ORDER BY data_entrada DESC
        LIMIT 10
    ''', (f'%{client}%',))
    
    resultats = []
    for row in cursor.fetchall():
        resultats.append({
            'comanda': row[0],
            'client': row[1],
            'descripcio': row[2],
            'pressupost': row[3],
            'import': row[4]
        })
    
    conn.close()
    return jsonify(resultats)

@app.route('/api/cerca', methods=['GET'])
def cerca_feines():
    """Cerca feines per client, descripció o comanda a TOTES les setmanes"""
    query = request.args.get('q', '').strip()
    any = request.args.get('any', type=int)
    setmana = request.args.get('setmana', type=int)
    limit = request.args.get('limit', type=int, default=200)
    
    if not query or len(query) < 2:
        return jsonify({'feines': [], 'total': 0})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Cerca per client, descripció o comanda
    sql = '''
        SELECT 
            id,
            comanda,
            client,
            unitats,
            descripcio,
            import,
            pressupost,
            estat,
            data_entrada,
            strftime('%W', data_entrada) AS setmana,
            strftime('%Y', data_entrada) AS any
        FROM feines
        WHERE client LIKE ?
           OR descripcio LIKE ?
           OR comanda LIKE ?
    '''
    params = [f'%{query}%', f'%{query}%', f'%{query}%']
    
    if setmana and any:
        sql += ' AND strftime("%W", data_entrada) = ? AND strftime("%Y", data_entrada) = ?'
        params.append(f'{setmana:02d}')
        params.append(str(any))
    
    sql += ' ORDER BY data_entrada DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(sql, params)
    feines = cursor.fetchall()
    conn.close()
    
    resultat = []
    for row in feines:
        unitats = row[3]
        import_valor = row[5]
        preu_miler = (import_valor / unitats * 1000) if unitats > 0 else 0.0
        
        resultat.append({
            'id': row[0],
            'comanda': row[1],
            'client': row[2],
            'unitats': unitats,
            'descripcio': row[4],
            'import': import_valor,
            'preu_miler': round(preu_miler, 2),
            'pressupost': row[6],
            'estat': row[7],
            'data_entrada': row[8],
            'setmana': row[9],
            'any': row[10]
        })
    
    return jsonify({
        'feines': resultat,
        'total': len(resultat),
        'query': query
    })

@app.route('/api/pendents', methods=['GET'])
def get_pendents():
    """Retorna les feines pendents de setmanes anteriors a la setmana actual"""
    setmana_actual = request.args.get('setmana', type=int)
    any_actual = request.args.get('any', type=int, default=2026)
    
    if not setmana_actual:
        return jsonify({'error': 'Setmana no especificada'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtenir les feines pendents (estat = 1) de setmanes anteriors a la setmana actual
    cursor.execute('''
        SELECT 
            id,
            comanda,
            client,
            unitats,
            descripcio,
            import,
            pressupost,
            estat,
            data_entrada,
            strftime('%W', data_entrada) AS setmana,
            strftime('%Y', data_entrada) AS any
        FROM feines
        WHERE estat IN (1, 2)
          AND (strftime('%Y', data_entrada) < ? 
               OR (strftime('%Y', data_entrada) = ? AND strftime('%W', data_entrada) < ?))
        ORDER BY data_entrada DESC
    ''', (str(any_actual), str(any_actual), f'{setmana_actual:02d}'))
    
    feines = cursor.fetchall()
    conn.close()
    
    resultat = []
    for row in feines:
        unitats = row[3]
        import_valor = row[5]
        preu_miler = (import_valor / unitats * 1000) if unitats > 0 else 0.0
        
        resultat.append({
            'id': row[0],
            'comanda': row[1],
            'client': row[2],
            'unitats': unitats,
            'descripcio': row[4],
            'import': import_valor,
            'preu_miler': round(preu_miler, 2),
            'pressupost': row[6],
            'estat': row[7],
            'data_entrada': row[8],
            'setmana': row[9],
            'any': row[10]
        })
    
    return jsonify({
        'feines': resultat,
        'total': len(resultat)
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5007)
