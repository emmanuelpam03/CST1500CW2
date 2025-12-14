import streamlit as st
import sqlite3
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file, ensure_default_admin
from app.data.incidents import migrate_incidents_from_file
from app.data.tickets import migrate_tickets_from_file, ensure_ticket_schema
from app.data.datasets import migrate_datasets_metadata_from_file

conn = connect_database()
create_all_tables(conn)
conn.close()

# Migrate users from file
migrate_users_from_file()

# Ensure default admin exists if no admins are present
ensure_default_admin()

# Ensure tickets table has latest columns (e.g., subject)
ensure_ticket_schema()

# Migrate incidents from file
migrate_incidents_from_file()

# Migrate tickets from file
migrate_tickets_from_file()

# Migrate datasets_metadata from file
migrate_datasets_metadata_from_file()

pg = st.navigation(
    [
        st.Page("pages/Dashboard.py"),
        st.Page("pages/Login.py"),
        st.Page("pages/Register.py"),
        st.Page("pages/Analyzer.py"),
        st.Page("pages/Cyber.py"),
        st.Page("pages/Tickets.py"),
        st.Page("pages/TicketAnalyzer.py"),
    ]
)

st.sidebar.page_link("pages/Dashboard.py", label="Dashboard")
st.sidebar.page_link("pages/Analyzer.py", label="AI Incident Analyzer")
st.sidebar.page_link("pages/Cyber.py", label="Cyber Dashboard")
st.sidebar.page_link("pages/Tickets.py", label="Tickets Dashboard")
st.sidebar.page_link("pages/TicketAnalyzer.py", label="AI Ticket Analyzer")


pg.run()
