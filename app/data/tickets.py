from app.data.db import connect_database
import pandas as pd


def ensure_ticket_schema():
    """
    Add missing columns (e.g., subject) to it_tickets table for older DBs.
    Safe to run repeatedly.
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(it_tickets)")
    cols = [row[1] for row in cursor.fetchall()]

    if "subject" not in cols:
        cursor.execute("ALTER TABLE it_tickets ADD COLUMN subject TEXT")

    conn.commit()
    conn.close()
def migrate_tickets_from_file(file_path="DATA/it_tickets.csv"):
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM it_tickets")

    if cursor.fetchone()[0] == 0:
        with open(file_path, 'r') as f:
            next(f)

            for line in f:
                parts = line.strip().split(',')

                if len(parts) != 7:
                    continue

                ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours = parts
                
                cursor.execute("""
                    INSERT INTO it_tickets
                    (ticket_id, priority, description, status, assigned_to, created_date, resolved_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours))

    conn.commit()
    conn.close()


def insert_ticket(ticket_id, priority, status, category, subject, description, created_date, assigned_to=None):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description, created_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description, created_date, assigned_to))
    conn.commit()
    lastid = cursor.lastrowid
    conn.close()
    return lastid

def get_all_tickets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", conn)
    conn.close()
    return df

def get_ticket_by_id(ticket_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_ticket_status(ticket_id, new_status):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE it_tickets SET status = ? WHERE ticket_id = ?", (new_status, ticket_id))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count 

def update_ticket(ticket_id, priority=None, status=None, category=None, subject=None, description=None, created_date=None, assigned_to=None, resolved_date=None):
    """ 
    Update a ticket. Only provided fields will be updated
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if priority is not None:
        updates.append("priority = ?")
        params.append(priority)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if subject is not None:
        updates.append("subject = ?")
        params.append(subject)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if created_date is not None:
        updates.append("created_date = ?")
        params.append(str(created_date))
    if assigned_to is not None:
        updates.append("assigned_to = ?")
        params.append(assigned_to)
    if resolved_date is not None:
        updates.append("resolved_date = ?")
        params.append(str(resolved_date))
    
    if updates:
        params.append(ticket_id)
        query = f"UPDATE it_tickets SET {', '.join(updates)} WHERE ticket_id = ?"
        cursor.execute(query, params)
        conn.commit()
        count = cursor.rowcount
    else:
        count = 0 
    
    conn.close()
    return count

def delete_ticket(ticket_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count
