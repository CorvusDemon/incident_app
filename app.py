from flask import Flask, render_template, request, redirect, url_for, flash, abort
import sqlite3
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "dev-secret-key"
DB_NAME = "incidents.db"

PRIORITY_MATRIX = {
    ("High", "High"): "Critical",
    ("High", "Medium"): "High",
    ("High", "Low"): "Medium",
    ("Medium", "High"): "High",
    ("Medium", "Medium"): "Medium",
    ("Medium", "Low"): "Low",
    ("Low", "High"): "Medium",
    ("Low", "Medium"): "Low",
    ("Low", "Low"): "Low",
}

ALLOWED_STATUSES = ["New", "In Progress", "Closed"]
ALLOWED_PRIORITIES = ["Critical", "High", "Medium", "Low"]


# ===========================================
# DATABASE
# ===========================================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            urgency TEXT NOT NULL,
            impact TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'New',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
        )
    """)
    conn.commit()
    conn.close()


def add_log(conn, incident_id, action, details=""):
    conn.execute(
        "INSERT INTO audit_log (incident_id, action, details, created_at) VALUES (?, ?, ?, ?)",
        (incident_id, action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )


def calculate_priority(urgency, impact):
    return PRIORITY_MATRIX.get((urgency, impact), "Low")


# ==============================
# HELPERS FOR TEMPLATES
# ==============================
def time_ago(date_str):
    try:
        past = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str
    diff = datetime.now() - past
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 30:
        return f"{days}d ago"
    months = days // 30
    return f"{months}mo ago"


def get_type_icon(title):
    """Icon select"""
    t = title.lower()
    if "phish" in t or "e-mail" in t or "email" in t or "mail" in t:
        return "📧"
    if "vpn" in t or "login" in t or "account" in t or "logowani" in t or "konto" in t:
        return "🔐"
    if "malware" in t or "virus" in t or "antivir" in t or "infect" in t or "wirus" in t or "antywir" in t or "infek" in t:
        return "🦠"
    if "edr" in t or "alert" in t or "monitor" in t:
        return "🚨"
    if "laptop" in t or "device" in t or "hardware" in t or "urządze" in t or "sprzęt" in t:
        return "💻"
    if "network" in t or "traffic" in t or "sieć" in t or "ruch" in t:
        return "🌐"
    if "leak" in t or "data" in t or "cloud" in t or "exfiltr" in t or "wyciek" in t or "dane" in t or "chmur" in t:
        return "📤"
    if "access" in t or "privilege" in t or "permission" in t or "dostęp" in t or "uprawni" in t:
        return "🔑"
    return "⚠️"


app.jinja_env.filters["time_ago"] = time_ago
app.jinja_env.filters["type_icon"] = get_type_icon


# ===========================================
# PAGES
# ===========================================
@app.route("/", methods=["GET", "POST"])
def index():
    init_db()

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        urgency = request.form.get("urgency", "").strip()
        impact = request.form.get("impact", "").strip()

        if not all([first_name, last_name, email, phone, title, description, urgency, impact]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("index"))

        priority = calculate_priority(urgency, impact)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        cursor = conn.execute("""
            INSERT INTO incidents
            (first_name, last_name, email, phone, title, description,
             urgency, impact, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'New', ?, ?)
        """, (first_name, last_name, email, phone, title, description,
              urgency, impact, priority, now, now))
        new_id = cursor.lastrowid
        add_log(conn, new_id, "Incident created",
                f"Priority: {priority}, Urgency: {urgency}, Impact: {impact}")
        conn.commit()
        conn.close()

        flash(f"Incident #{new_id} has been recorded. Priority: {priority}.", "success")
        return redirect(url_for("index"))

    # Filtering/search options
    search = request.args.get("search", "").strip()
    priority_filter = request.args.get("priority", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = "SELECT * FROM incidents WHERE 1=1"
    params = []

    if search:
        if search.isdigit():
            query += " AND (id = ? OR email LIKE ? OR title LIKE ?)"
            params.extend([int(search), f"%{search}%", f"%{search}%"])
        else:
            query += " AND (email LIKE ? OR title LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

    if priority_filter in ALLOWED_PRIORITIES:
        query += " AND priority = ?"
        params.append(priority_filter)

    if status_filter in ALLOWED_STATUSES:
        query += " AND status = ?"
        params.append(status_filter)

    query += """
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END,
            id DESC
    """

    conn = get_db_connection()
    incidents = conn.execute(query, params).fetchall()

    # Statistics
    total = conn.execute("SELECT COUNT(*) AS c FROM incidents").fetchone()["c"]
    critical = conn.execute("SELECT COUNT(*) AS c FROM incidents WHERE priority = 'Critical'").fetchone()["c"]
    high = conn.execute("SELECT COUNT(*) AS c FROM incidents WHERE priority = 'High'").fetchone()["c"]
    medium = conn.execute("SELECT COUNT(*) AS c FROM incidents WHERE priority = 'Medium'").fetchone()["c"]
    low = conn.execute("SELECT COUNT(*) AS c FROM incidents WHERE priority = 'Low'").fetchone()["c"]
    in_progress = conn.execute("SELECT COUNT(*) AS c FROM incidents WHERE status = 'In Progress'").fetchone()["c"]
    closed = conn.execute("SELECT COUNT(*) AS c FROM incidents WHERE status = 'Closed'").fetchone()["c"]

    safe_total = total if total > 0 else 1
    stats = {
        "total": total,
        "critical": critical,
        "in_progress": in_progress,
        "closed": closed,
        "by_priority": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "critical_pct": round(critical / safe_total * 100, 1),
            "high_pct": round(high / safe_total * 100, 1),
            "medium_pct": round(medium / safe_total * 100, 1),
            "low_pct": round(low / safe_total * 100, 1),
        },
        "critical_pct": round(critical / safe_total * 100),
        "in_progress_pct": round(in_progress / safe_total * 100),
        "closed_pct": round(closed / safe_total * 100),
    }

    conn.close()

    return render_template(
        "index.html",
        incidents=incidents,
        search=search,
        priority_filter=priority_filter,
        status_filter=status_filter,
        priorities=ALLOWED_PRIORITIES,
        statuses=ALLOWED_STATUSES,
        stats=stats,
    )


@app.route("/incident/<int:incident_id>")
def incident_detail(incident_id):
    init_db()
    conn = get_db_connection()
    incident = conn.execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()

    if not incident:
        conn.close()
        abort(404)

    logs = conn.execute(
        "SELECT * FROM audit_log WHERE incident_id = ? ORDER BY id DESC",
        (incident_id,)
    ).fetchall()
    conn.close()

    return render_template(
        "incident.html",
        incident=incident,
        logs=logs,
        statuses=ALLOWED_STATUSES,
    )


@app.route("/incident/<int:incident_id>/status", methods=["POST"])
def update_status(incident_id):
    init_db()
    new_status = request.form.get("status", "").strip()

    if new_status not in ALLOWED_STATUSES:
        flash("Invalid status value.", "error")
        return redirect(url_for("incident_detail", incident_id=incident_id))

    conn = get_db_connection()
    incident = conn.execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()

    if not incident:
        conn.close()
        abort(404)

    old_status = incident["status"]
    if old_status == new_status:
        conn.close()
        flash("Status remained unchanged.", "info")
        return redirect(url_for("incident_detail", incident_id=incident_id))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE incidents SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, incident_id)
    )
    add_log(
        conn,
        incident_id,
        "Status updated",
        f"{old_status} → {new_status}"
    )
    conn.commit()
    conn.close()

    flash(f"Status updated: {old_status} → {new_status}.", "success")
    return redirect(url_for("incident_detail", incident_id=incident_id))


@app.route("/seed")
def seed():
    init_db()
    conn = get_db_connection()

    first_names = ["Anna", "Jan", "Piotr", "Maria", "Katarzyna", "Tomasz", "Michal", "Ewa"]
    last_names = ["Kowalski", "Nowak", "Wisniewski", "Wojcik", "Mazur", "Krawczyk", "Kaminski", "Zielinski"]
    titles = [
        "Suspicious phishing email reported",
        "EDR endpoint detection alert",
        "Unauthorized VPN login attempt",
        "Missing corporate laptop reported",
        "Anomalous outbound network traffic",
        "Antivirus disabled on workstation",
        "After-hours privileged data access attempt",
        "Suspected malware infection on host",
        "Mass user account lockout spike",
        "Potential cloud storage data leak",
    ]
    descriptions = [
        "User reported suspicious activity. Review endpoint logs and verify potential compromise.",
        "Monitoring system flagged an anomaly indicating a possible cybersecurity incident.",
        "Report requires source verification, containment check, and risk assessment.",
    ]

    count = conn.execute("SELECT COUNT(*) AS total FROM incidents").fetchone()["total"]
    if count >= 20:
        conn.close()
        flash("Database already contains sample data.", "info")
        return redirect(url_for("index"))

    for i in range(25):
        first = random.choice(first_names)
        last = random.choice(last_names)
        title = random.choice(titles)
        description = random.choice(descriptions)
        urgency = random.choice(["Low", "Medium", "High"])
        impact = random.choice(["Low", "Medium", "High"])
        priority = calculate_priority(urgency, impact)
        email = f"user{i+1}@company.com"
        phone = f"+48 5{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.execute("""
            INSERT INTO incidents
            (first_name, last_name, email, phone, title, description,
             urgency, impact, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'New', ?, ?)
        """, (first, last, email, phone, title, description,
              urgency, impact, priority, now, now))
        add_log(conn, cursor.lastrowid, "Incident created",
                f"Seeded sample record. Priority: {priority}")

    conn.commit()
    conn.close()
    flash("Added 25 sample incidents.", "success")
    return redirect(url_for("index"))


@app.route("/clear")
def clear():
    init_db()
    conn = get_db_connection()
    conn.execute("DELETE FROM incidents")
    conn.execute("DELETE FROM audit_log")
    conn.commit()
    conn.close()
    flash("All incidents have been cleared.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
