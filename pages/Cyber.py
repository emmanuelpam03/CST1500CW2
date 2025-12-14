import streamlit as st
import pandas as pd
from datetime import datetime
from app.data.incidents import (
    get_all_incidents,
    get_incident_by_id,
    insert_incident as create_incident,
    update_incident,
    delete_incident,
)

class CyberDashboardApp:
    def run(self):
        self._check_auth()
        self._render_title()
        self._load_incidents()
        self._render_overview()
        self._render_tabs()

    def _check_auth(self):
        if not st.session_state.get("logged_in"):
            st.switch_page("pages/Login.py")

    def _render_title(self):
        st.title("Cyber Dashboard")

    def _load_incidents(self):
        with st.spinner("Loading incidents..."):
            raw = get_all_incidents()

        if isinstance(raw, pd.DataFrame):
            df = raw.copy()
        else:
            df = pd.DataFrame(raw)

        if "created_at" in df.columns:
            df = df.drop(columns=["created_at"])

        df = df.fillna("None")

        if df.empty:
            st.error("No incidents found.")
            st.stop()

        self.df = df

    def _render_overview(self):
        st.subheader("Cyber Incidents")
        st.dataframe(self.df)

        st.subheader("Incidents by Type")

        high_count = (self.df["severity"] == "High").sum()
        total_count = len(self.df)

        left, right = st.columns(2)
        left.metric("High", high_count)
        right.metric("Incidents", total_count)

        counts = self.df["severity"].value_counts().reset_index()
        counts.columns = ["severity", "count"]

        st.bar_chart(counts.set_index("severity")["count"])

        st.divider()

    def _render_tabs(self):
        tab1, tab2, tab3 = st.tabs(
            ["Create Incident", "Update Incident", "Delete Incident"]
        )

        with tab1:
            self._create_incident_tab()

        with tab2:
            self._update_incident_tab()

        with tab3:
            self._delete_incident_tab()

    def _create_incident_tab(self):
        st.subheader("Add New Incident")

        with st.form("add_incident_form", clear_on_submit=True):
            date = st.date_input("Date")
            incident_type = st.text_input("Incident Type")
            severity = st.selectbox("Severity", ["Low", "Medium", "High"])
            status = st.selectbox(
                "Status", ["Open", "In Progress", "Resolved", "Closed"]
            )
            description = st.text_area("Description")

            submitted = st.form_submit_button("Add Incident")

            if submitted:
                if not incident_type or not description:
                    st.error("Incident Type and Description are required!")
                else:
                    new_incident = {
                        "date": str(date),
                        "incident_type": incident_type,
                        "severity": severity,
                        "status": status,
                        "description": description,
                        "reported_by": st.session_state.get("username"),
                    }

                    try:
                        create_incident(**new_incident)
                        st.success("Incident added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error occurred: {str(e)}")

    def _update_incident_tab(self):
        st.subheader("Update Incident")

        incident_options = [
            f"{row['id']}: {row.get('incident_type', 'N/A')} - {row.get('severity', 'N/A')}"
            for _, row in self.df.iterrows()
        ]

        if incident_options:
            selected_incident_label = st.selectbox(
                "Select Incident to Update",
                options=incident_options,
                key="update_incident_select",
            )

            if selected_incident_label:
                selected_id = int(selected_incident_label.split(":")[0])
                incident = get_incident_by_id(selected_id)

                if incident:
                    with st.form("update_incident_form"):
                        current_date = incident["date"]
                        try:
                            if current_date:
                                date_obj = datetime.strptime(
                                    current_date, "%Y-%m-%d"
                                ).date()
                            else:
                                date_obj = datetime.now().date()
                        except:
                            date_obj = datetime.now().date()

                        date = st.date_input("Date", value=date_obj)
                        incident_type = st.text_input(
                            "Incident Type",
                            value=incident["incident_type"] or "",
                        )
                        severity = st.selectbox(
                            "Severity",
                            ["Low", "Medium", "High"],
                            index=(
                                ["Low", "Medium", "High"].index(
                                    incident["severity"]
                                )
                                if incident["severity"]
                                in ["Low", "Medium", "High"]
                                else 0
                            ),
                        )
                        status = st.selectbox(
                            "Status",
                            ["Open", "In Progress", "Resolved", "Closed"],
                            index=(
                                [
                                    "Open",
                                    "In Progress",
                                    "Resolved",
                                    "Closed",
                                ].index(incident["status"])
                                if incident["status"]
                                in [
                                    "Open",
                                    "In Progress",
                                    "Resolved",
                                    "Closed",
                                ]
                                else 0
                            ),
                        )
                        description = st.text_area(
                            "Description",
                            value=incident["description"] or "",
                        )

                        submitted = st.form_submit_button("Update Incident")

                        if submitted:
                            if not incident_type or not description:
                                st.error(
                                    "Incident Type and Description are required!"
                                )
                            else:
                                try:
                                    update_incident(
                                        incident_id=selected_id,
                                        date=str(date),
                                        incident_type=incident_type,
                                        severity=severity,
                                        status=status,
                                        description=description,
                                    )
                                    st.success(
                                        "Incident updated successfully!"
                                    )
                                    st.rerun()
                                except Exception as e:
                                    st.error(
                                        f"Error updating incident: {str(e)}"
                                    )
        else:
            st.info("No incidents available to update.")

    def _delete_incident_tab(self):
        st.subheader("Delete Incident")

        delete_options = [
            f"{row['id']}: {row.get('incident_type', 'N/A')} - {row.get('severity', 'N/A')}"
            for _, row in self.df.iterrows()
        ]

        if delete_options:
            selected_delete_label = st.selectbox(
                "Select Incident to Delete",
                options=delete_options,
                key="delete_incident_select",
            )

            if selected_delete_label:
                selected_id = int(selected_delete_label.split(":")[0])
                incident = get_incident_by_id(selected_id)

                if incident:
                    st.warning(
                        f"Are you sure you want to delete Incident ID {selected_id}?"
                    )
                    st.write(f"**Type:** {incident['incident_type']}")
                    st.write(
                        f"**Severity:** {incident['severity']}"
                    )
                    st.write(f"**Status:** {incident['status']}")
                    st.write(
                        f"**Description:** {incident['description']}"
                    )

                    if st.button(
                        "Confirm Delete",
                        type="primary",
                        key="confirm_delete",
                    ):
                        try:
                            delete_incident(selected_id)
                            st.success(
                                "Incident deleted successfully!"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(
                                f"Error deleting incident: {str(e)}"
                            )
        else:
            st.info("No incidents available to delete.")

if __name__ == "__main__":
    CyberDashboardApp().run()