from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import numpy as np
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ---------------------------
# INITIALISATION BASE
# ---------------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            filiere TEXT,
            niveau TEXT,
            course TEXT,
            teacher TEXT,
            satisfaction INTEGER,
            best_teacher_vote INTEGER,
            comment TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()


# ---------------------------
# FORMULAIRE
# ---------------------------
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/form', methods=['GET', 'POST'])
def form():

    if request.method == 'POST':

        student_name = request.form['student_name']
        filiere = request.form['filiere']
        niveau = request.form['niveau']
        course = request.form['course']
        teacher = request.form['teacher']
        satisfaction = request.form['satisfaction']
        comment = request.form['comment']

        best_teacher_vote = 1 if request.form.get('best_teacher_vote') else 0

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO feedback (
                student_name, filiere, niveau,
                course, teacher, satisfaction,
                best_teacher_vote, comment, date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_name,
            filiere,
            niveau,
            course,
            teacher,
            satisfaction,
            best_teacher_vote,
            comment,
            datetime.now()
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('responses'))

    return render_template('form.html')


# ---------------------------
# RESPONSES
# ---------------------------
@app.route('/responses')
def responses():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()

    return render_template('responses.html', data=data)


# ---------------------------
# DASHBOARD
@app.route('/dashboard')
def dashboard():

    import sqlite3
    import numpy as np

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # =========================
    # TOTAL FEEDBACKS
    # =========================
    cursor.execute("SELECT COUNT(*) FROM feedback")
    total = cursor.fetchone()[0] or 0

    # =========================
    # SATISFACTION MOYENNE
    # =========================
    cursor.execute("SELECT satisfaction FROM feedback")
    rows = cursor.fetchall()

    sats = [r[0] for r in rows if r[0] is not None]
    avg_satisfaction = round(np.mean(sats), 2) if len(sats) > 0 else 0

    # =========================
    # TEACHERS VOTES
    # =========================
    cursor.execute("""
        SELECT teacher, COUNT(*)
        FROM feedback
        WHERE best_teacher_vote = 1
        GROUP BY teacher
    """)
    teacher_votes = cursor.fetchall() or []

    # =========================
    # FILIÈRES
    # =========================
    cursor.execute("""
        SELECT filiere, COUNT(*)
        FROM feedback
        GROUP BY filiere
    """)
    filiere_data = cursor.fetchall() or []

    conn.close()

    # =========================
    # SCATTER DATA SAFE
    # =========================
    scatter_x = sats if sats else []
    scatter_y = list(range(1, len(scatter_x) + 1)) if scatter_x else []

    # =========================
    # REGRESSION (placeholder safe)
    # =========================
    # =========================
    # REGRESSION LINÉAIRE
    # =========================

    regression_line = []

    if len(scatter_x) >= 2:

      # calcul pente et intercept
      a, b = np.polyfit(scatter_x, scatter_y, 1)

      # calcul valeurs ligne
      regression_line = [
        a*x + b
        for x in scatter_x
    ]

    return render_template(
        'dashboard.html',
        total=total,
        avg_satisfaction=avg_satisfaction,
        teacher_votes=teacher_votes,
        filiere_data=filiere_data,
        scatter_x=scatter_x,
        scatter_y=scatter_y,
        regression_line=regression_line
    )
# CALCUL STATISTIQUES
# ---------------------------
def calcul_stats():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT satisfaction FROM feedback")
    x = [row[0] for row in cursor.fetchall()]
    y = list(range(1, len(x)+1))

    conn.close()

    if len(x) < 2:
        return None

    x_mean = np.mean(x)
    y_mean = np.mean(y)

    covariance = np.mean([
        (xi - x_mean)*(yi - y_mean)
        for xi, yi in zip(x,y)
    ])

    variance = np.var(x)

    r = covariance / np.sqrt(
        variance * np.var(y)
    )

    r2 = r**2

    a = covariance / variance
    b = y_mean - a*x_mean

    return variance, covariance, r, r2, a, b


# ---------------------------
# RAPPORT HTML
# ---------------------------
@app.route('/rapport')
def rapport():

    stats = calcul_stats()

    if stats is None:
        return "Pas assez de données"

    variance, covariance, r, r2, a, b = stats

    return render_template(
        'rapport.html',
        variance=variance,
        covariance=covariance,
        r=r,
        r2=r2,
        a=a,
        b=b
    )


# ---------------------------
# EXPLICATION IA
# ---------------------------
@app.route('/explication')
def explication():

    stats = calcul_stats()

    if stats is None:
        texte = "Pas assez de données."
    else:

        variance, covariance, r, r2, a, b = stats

        texte = f"""
        Le coefficient r = {round(r,2)}
        indique la force de relation.

        Le coefficient R² = {round(r2,2)}
        indique la qualité du modèle.

        La droite y = {round(a,2)}x + {round(b,2)}
        représente la tendance générale.
        """

    return render_template(
        'explication.html',
        texte=texte
    )


# ---------------------------
# PDF
# ---------------------------
@app.route('/pdf_graphique')
def pdf_graphique():

    stats = calcul_stats()

    if stats is None:
        return "Pas assez de données"

    variance, covariance, r, r2, a, b = stats

    buffer = io.BytesIO()

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(buffer)

    content = []

    content.append(
        Paragraph("Rapport Statistique", styles["Title"])
    )

    content.append(Spacer(1,12))

    content.append(
        Paragraph(f"Variance : {variance:.4f}", styles["Normal"])
    )

    content.append(
        Paragraph(f"Covariance : {covariance:.4f}", styles["Normal"])
    )

    content.append(
        Paragraph(f"Coefficient r : {r:.4f}", styles["Normal"])
    )

    content.append(
        Paragraph(f"Coefficient R² : {r2:.4f}", styles["Normal"])
    )

    content.append(
        Paragraph(
            f"Régression : y = {a:.4f}x + {b:.4f}",
            styles["Normal"]
        )
    )

    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="rapport_statistique.pdf",
        mimetype="application/pdf"
    )


# ---------------------------
# LANCEMENT
# ---------------------------
if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)