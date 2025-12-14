import pandas as pd
from app.data.db import connect_database

def migrate_incidents_from_file(file_path="DATA/cyber_incidents.csv"):
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
    if cursor.fetchone()[0] == 0:
        with open(file_path, 'r') as f:
            next(f)  # Skip the header line
            for line in f:
                incident_id, timestamp, severity, category, status, description = line.strip().split(',')
                cursor.execute("""
                    INSERT OR IGNORE INTO cyber_incidents
                    (date, incident_type, severity, status, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, category, severity, status, description))
    conn.commit()
    conn.close()

def insert_incident(date, incident_type, severity, status, description, reported_by=None):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cyber_incidents
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))
    conn.commit()
    lastid = cursor.lastrowid
    conn.close()
    return lastid

def get_all_incidents():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY id DESC", conn)
    conn.close()
    return df

def get_incident_by_id(incident_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cyber_incidents WHERE id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_incident_status(incident_id, new_status):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE cyber_incidents SET status = ? WHERE id = ?", (new_status, incident_id))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count

def update_incident(incident_id, date=None, incident_type=None, severity=None, status=None, description=None, reported_by=None):
    """
    Update an incident. Only provided fields will be updated.
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if date is not None:
        updates.append("date = ?")
        params.append(str(date))
    if incident_type is not None:
        updates.append("incident_type = ?")
        params.append(incident_type)
    if severity is not None:
        updates.append("severity = ?")
        params.append(severity)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if reported_by is not None:
        updates.append("reported_by = ?")
        params.append(reported_by)
    
    if updates:
        params.append(incident_id)
        query = f"UPDATE cyber_incidents SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        count = cursor.rowcount
    else:
        count = 0
    
    conn.close()
    return count

def delete_incident(incident_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count
