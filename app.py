from flask import Flask, redirect, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '172.19.0.2'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'toor'
app.config['MYSQL_DB'] = 'spkwp'

mysql = MySQL(app)

@app.route("/home")
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/hasil", methods=['GET', 'POST'])
def hasil():
    bobot = mysql.connection.cursor()
    bobot.execute('''SELECT SUM(bobot) FROM kriteria''')
    rb = bobot.fetchone()
    normbobot = mysql.connection.cursor()
    normbobot.execute('''SELECT IF(jenis="keuntungan", bobot/100, bobot*-1/100) bobot FROM kriteria;''')
    normalizebobot = normbobot.fetchall()
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM kriteria''')
    rk = cur.fetchall()
    curs = mysql.connection.cursor()
    curs.execute('''SELECT * FROM alternatif;''')
    ria = curs.fetchall()
    isialt=[]
    nilais=[]
    nilaiv=0
    for i in range(len(ria)):
        cursa = mysql.connection.cursor()
        if i<9:
            cursa.execute('''SELECT nilai FROM isiAlternatif WHERE kodeA ='%s' ORDER BY kodeA, kodeK;''' % ('A0'+str(i+1)))
        else:
            cursa.execute('''SELECT nilai FROM isiAlternatif WHERE kodeA ='%s' ORDER BY kodeA, kodeK;''' % ('A'+str(i+1)))
        hasilisi=cursa.fetchall()
        isialt.append(hasilisi)
        if i<9:
            cursa.execute('''CALL hitungS('%s')''' % ('A0'+str(i+1)))
        else:
            cursa.execute('''CALL hitungS('%s')''' % ('A'+str(i+1)))
        sval=cursa.fetchone()
        nilais.append(sval)
        nilaiv += sval[0]
    
    return render_template('hasil.html', rk=rk, ria=ria, rb=rb, isialt=isialt, normalizebobot=normalizebobot, nilais=nilais, nilaiv=nilaiv)

@app.route("/kriteria", methods=['GET', 'POST'])
def kriteria():
    if request.method == 'POST':
        if request.form['action'] == 'update':
            kode = request.form['kodek']
            nama = request.form['namak']
            jenis = request.form['jenis']
            bobot = request.form['bobot']
            cursor = mysql.connection.cursor()
            cursor.execute(
                """ UPDATE kriteria SET kode='%s',nama='%s',jenis='%s',bobot='%s' WHERE kode = '%s'"""
                % (kode, nama, jenis, bobot, kode))
            mysql.connection.commit()

        else:
            kode = request.form['kodek']
            nama = request.form['namak']
            jenis = request.form['jenis']
            bobot = request.form['bobot']
            cursor = mysql.connection.cursor()
            cursor.execute(''' INSERT INTO kriteria VALUES(%s,%s,%s,%s)''',
                           (kode, nama, jenis, bobot))
            mysql.connection.commit()

    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM kriteria''')
    rv = cur.fetchall()
    return render_template('kriteria.html', rv=rv)

@app.route("/tambahkriteria")
def tambahkriteria():
    return render_template('tambahkriteria.html')

@app.route("/ubahkriteria")
def ubahkriteria():
    kode = request.args.get('kode')
    cursor = mysql.connection.cursor()
    cursor.execute(f""" SELECT * FROM kriteria WHERE kode = '{kode}'""")
    res = cursor.fetchone()
    return render_template('ubahkriteria.html', res=res)

@app.route("/hapuskriteria", methods=['GET'])
def hapuskriteria():
    kode = request.args.get('kode')
    cursor = mysql.connection.cursor()
    cursor.execute(""" Delete from kriteria where kode = '%s'""" % str(kode))
    mysql.connection.commit()
    return redirect("http://localhost:5000/kriteria")

@app.route("/alternatif", methods=['GET', 'POST'])
def alternatif():
    if request.method == 'POST':
        kode = request.form['kodea']
        nama = request.form['namaa']

        cursor = mysql.connection.cursor()
        if request.form['action'] == 'update':
            cursor.execute(
                """ UPDATE alternatif SET kode='%s',nama='%s' WHERE kode = '%s'"""
                % (kode, nama, kode))
            mysql.connection.commit()

        else:
            cursor.execute(''' INSERT INTO alternatif VALUES('%s','%s')''' % (
                kode,
                nama,
            ))
            mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM alternatif''')
    rv = cur.fetchall()
    return render_template('alternatif.html', rv=rv)

@app.route("/tambahalternatif")
def tambahalternatif():
    return render_template('tambahalternatif.html')

@app.route("/ubahalternatif")
def ubahalternatif():
    kode = request.args.get('kode')
    cursor = mysql.connection.cursor()
    cursor.execute(f""" SELECT * FROM alternatif WHERE kode = '{kode}'""")
    res = cursor.fetchone()
    return render_template('ubahalternatif.html', res=res)

@app.route("/hapusalternatif")
def hapusalternatif():
    kode = request.args.get('kode')
    cursor = mysql.connection.cursor()
    cursor.execute(""" Delete from alternatif where kode = '%s'""" % str(kode))
    mysql.connection.commit()
    return redirect("http://localhost:5000/alternatif")

@app.route("/isialternatif")
def isialternatif():
    kode = request.args.get('kode')
    cursor = mysql.connection.cursor()
    cursor.execute(f""" SELECT * FROM alternatif WHERE kode = '{kode}'""")
    res = cursor.fetchone()
    cursor.execute(""" SELECT kode, nama FROM kriteria """)
    resk = cursor.fetchall()
    isi = []
    print(isi)
    cursor.execute(
        f""" SELECT kodeK FROM isiAlternatif WHERE kodeA = '{kode}'""")
    isian = cursor.fetchall()
    for i in range(len(resk)):
        kodek = "".join(isian[i])
        cursor.execute(
            f""" SELECT nilai FROM isiAlternatif WHERE kodeK = '{kodek}' AND kodeA = '{kode}'"""
        )
        asd = cursor.fetchone()
        try:
            nilai = float(asd[0])
        except:
            nilai = ""
        isi.append(nilai)
    print(isi)
    return render_template('isialternatif.html', res=res, resk=resk, isi=isi)

@app.route("/updateisi", methods=['GET', 'POST'])
def updateisi():
    if request.method == 'POST':
        kodeA = request.form['kodeA']
        cursor = mysql.connection.cursor()
        if request.form['action'] == 'update':
            for i in range(int(request.form['clength'])):
                kodek = request.form[f"kodeK{i+1}"]
                nilai = request.form[f"C{i+1}"]
                cursor.execute(
                    """ UPDATE isiAlternatif SET nilai='%s' WHERE kodeA = '%s' AND kodeK = '%s' """
                    % (nilai, kodeA, kodek))
                mysql.connection.commit()
    return redirect("http://localhost:5000/alternatif")
