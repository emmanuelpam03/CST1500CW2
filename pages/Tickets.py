import streamlit as st
import pandas as pd
from datetime import datetime
from app.data.tickets import (
    get_all_tickets,
    get_ticket_by_id,
    insert_ticket as create_ticket,
    update_ticket,
    delete_ticket,
)

class TicketsDashboardApp:
    def run(self):
        self._check_auth()
        self._render_title()
        self._load_tickets()
        self._render_overview()
        self._render_tabs()

    def _check_auth(self):
        if not st.session_state.get("logged_in"):
            st.switch_page("pages/Login.py")

    def _render_title(self):
        st.title("Tickets Dashboard")

    def _load_tickets(self):
        with st.spinner("Loading tickets..."):
            raw = get_all_tickets()

        if isinstance(raw, pd.DataFrame):
            df = raw.copy()
        else:
            df = pd.DataFrame(raw)

        if "created_at" in df.columns:
            df = df.drop(columns=["created_at"])

        df = df.fillna("None")

        if df.empty:
            st.error("No tickets found.")
            st.stop()

        self.df = df

    def _render_overview(self):
        st.subheader("Tickets")
        st.dataframe(self.df)

        st.subheader("Tickets by Priority")

        high_count = (self.df["priority"] == "High").sum()
        total_count = len(self.df)

        left, right = st.columns(2)
        left.metric("High Priority", high_count)
        right.metric("Total Tickets", total_count)

        counts = self.df["priority"].value_counts().reset_index()
        counts.columns = ["priority", "count"]
        st.bar_chart(counts.set_index("priority")["count"])

        st.divider()

    def _render_tabs(self):
        tab1, tab2, tab3 = st.tabs(
            ["Create Ticket", "Update Ticket", "Delete Ticket"]
        )

        with tab1:
            self._create_ticket_tab()

        with tab2:
            self._update_ticket_tab()

        with tab3:
            self._delete_ticket_tab()

    def _create_ticket_tab(self):
        st.subheader("Create New Ticket")

        with st.form("add_ticket_form", clear_on_submit=True):
            import uuid

            ticket_id = st.text_input(
                "Ticket ID",
                value=f"TICKET-{uuid.uuid4().hex[:8].upper()}",
            )
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            status = st.selectbox(
                "Status", ["Open", "In Progress", "Resolved", "Closed"]
            )
            category = st.text_input("Category")
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            created_date = st.date_input(
                "Created Date", value=datetime.now().date()
            )
            assigned_to = st.text_input(
                "Assigned To (optional)", value=""
            )

            submitted = st.form_submit_button("Create Ticket")

            if submitted:
                if not ticket_id or not description:
                    st.error("Ticket ID and Description are required!")
                else:
                    try:
                        create_ticket(
                            ticket_id=ticket_id,
                            priority=priority,
                            status=status,
                            category=category if category else None,
                            subject=subject if subject else None,
                            description=description,
                            created_date=str(created_date),
                            assigned_to=assigned_to if assigned_to else None,
                        )
                        st.success("Ticket created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating ticket: {str(e)}")

    def _update_ticket_tab(self):
        st.subheader("Update Ticket")

        ticket_options = [
            f"{row['ticket_id']}: {row.get('status', 'N/A')} - {row.get('priority', 'N/A')}"
            for _, row in self.df.iterrows()
        ]

        if ticket_options:
            selected_ticket_label = st.selectbox(
                "Select Ticket to Update",
                options=ticket_options,
                key="update_ticket_select",
            )

            if selected_ticket_label:
                selected_ticket_id = selected_ticket_label.split(":")[0]
                ticket = get_ticket_by_id(selected_ticket_id)

                if ticket:
                    ticket_dict = dict(ticket)
                    with st.form("update_ticket_form"):
                        current_date = (
                            ticket_dict.get("created_date")
                            or ticket_dict.get("created_at")
                        )
                        try:
                            if current_date:
                                date_obj = datetime.strptime(
                                    str(current_date), "%Y-%m-%d"
                                ).date()
                            else:
                                date_obj = datetime.now().date()
                        except:
                            date_obj = datetime.now().date()

                        st.text_input(
                            "Ticket ID",
                            value=ticket_dict.get("ticket_id", ""),
                            disabled=True,
                        )
                        priority = st.selectbox(
                            "Priority",
                            ["Low", "Medium", "High"],
                            index=[
                                "Low",
                                "Medium",
                                "High",
                            ].index(ticket_dict.get("priority", ""))
                            if ticket_dict.get("priority")
                            in ["Low", "Medium", "High"]
                            else 0,
                        )
                        status = st.selectbox(
                            "Status",
                            ["Open", "In Progress", "Resolved", "Closed"],
                            index=[
                                "Open",
                                "In Progress",
                                "Resolved",
                                "Closed",
                            ].index(ticket_dict.get("status", ""))
                            if ticket_dict.get("status")
                            in [
                                "Open",
                                "In Progress",
                                "Resolved",
                                "Closed",
                            ]
                            else 0,
                        )
                        category = st.text_input(
                            "Category",
                            value=ticket_dict.get("category") or "",
                        )
                        subject = st.text_input(
                            "Subject",
                            value=ticket_dict.get("subject") or "",
                        )
                        description = st.text_area(
                            "Description",
                            value=ticket_dict.get("description") or "",
                        )
                        created_date = st.date_input(
                            "Created Date", value=date_obj
                        )
                        assigned_to = st.text_input(
                            "Assigned To",
                            value=ticket_dict.get("assigned_to") or "",
                        )

                        resolved_date_val = ticket_dict.get("resolved_date")
                        try:
                            if resolved_date_val:
                                resolved_date_obj = datetime.strptime(
                                    str(resolved_date_val), "%Y-%m-%d"
                                ).date()
                            else:
                                resolved_date_obj = None
                        except:
                            resolved_date_obj = None

                        set_resolved = st.checkbox(
                            "Set Resolved Date",
                            value=bool(resolved_date_val),
                        )
                        resolved_date = (
                            st.date_input(
                                "Resolved Date",
                                value=resolved_date_obj
                                or datetime.now().date(),
                            )
                            if set_resolved
                            else None
                        )

                        submitted = st.form_submit_button("Update Ticket")

                        if submitted:
                            if not description:
                                st.error("Description is required!")
                            else:
                                try:
                                    update_ticket(
                                        ticket_id=selected_ticket_id,
                                        priority=priority,
                                        status=status,
                                        category=category
                                        if category
                                        else None,
                                        subject=subject
                                        if subject
                                        else None,
                                        description=description,
                                        created_date=str(created_date),
                                        assigned_to=assigned_to
                                        if assigned_to
                                        else None,
                                        resolved_date=str(resolved_date)
                                        if resolved_date
                                        else None,
                                    )
                                    st.success(
                                        "Ticket updated successfully!"
                                    )
                                    st.rerun()
                                except Exception as e:
                                    st.error(
                                        f"Error updating ticket: {str(e)}"
                                    )
        else:
            st.info("No tickets available to update.")

    def _delete_ticket_tab(self):
        st.subheader("Delete Ticket")

        delete_options = [
            f"{row['ticket_id']}: {row.get('status', 'N/A')} - {row.get('priority', 'N/A')}"
            for _, row in self.df.iterrows()
        ]

        if delete_options:
            selected_delete_label = st.selectbox(
                "Select Ticket to Delete",
                options=delete_options,
                key="delete_ticket_select",
            )

            if selected_delete_label:
                selected_ticket_id = selected_delete_label.split(":")[0]
                ticket = get_ticket_by_id(selected_ticket_id)

                if ticket:
                    ticket_dict = dict(ticket)
                    st.warning(
                        f"Are you sure you want to delete Ticket ID {selected_ticket_id}?"
                    )
                    st.write(
                        f"**Category:** {ticket_dict.get('category', 'N/A')}"
                    )
                    st.write(
                        f"**Priority:** {ticket_dict.get('priority', 'N/A')}"
                    )
                    st.write(
                        f"**Status:** {ticket_dict.get('status', 'N/A')}"
                    )
                    st.write(
                        f"**Description:** {ticket_dict.get('description', 'N/A')}"
                    )

                    if st.button(
                        "Confirm Delete",
                        type="primary",
                        key="confirm_delete_ticket",
                    ):
                        try:
                            delete_ticket(selected_ticket_id)
                            st.success(
                                "Ticket deleted successfully!"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(
                                f"Error deleting ticket: {str(e)}"
                            )
        else:
            st.info("No tickets available to delete.")

if __name__ == "__main__":
    TicketsDashboardApp().run()
