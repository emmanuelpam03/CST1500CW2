import streamlit as st
from app.data.tickets import get_all_tickets
from google import genai

class AITicketAnalyzerApp:
    def run(self):
        self._check_auth()
        self._render_title()
        self._load_tickets()
        self._render_selector_and_details()

    def _check_auth(self):
        if not st.session_state.get("logged_in"):
            st.switch_page("pages/Login.py")

    def _render_title(self):
        st.title("AI Ticket Analyzer")

    def _load_tickets(self):
        with st.spinner("Loading tickets..."):
            self.tickets = get_all_tickets()

        if self.tickets.empty:
            st.error("No tickets found.")

    def _render_selector_and_details(self):
        if self.tickets.empty:
            return

        labels = [
            f"{row['ticket_id']}: {row.get('category', 'N/A')} - {row['priority']}"
            for _, row in self.tickets.iterrows()
        ]

        choice = st.selectbox(
            label="Select ticket to analyze:",
            options=labels,
            placeholder="Select a ticket",
            key="ticket_option",
        )

        if choice:
            selected_ticket_id = choice.split(":")[0]
            selected_ticket = self.tickets.loc[
                self.tickets["ticket_id"] == selected_ticket_id
            ].iloc[0]

            st.subheader("Ticket Details")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Ticket ID:** {selected_ticket['ticket_id']}")
                st.write(f"**Priority:** {selected_ticket['priority']}")
                st.write(f"**Status:** {selected_ticket['status']}")
            with col2:
                st.write(
                    f"**Category:** {selected_ticket.get('category', 'N/A')}"
                )
                st.write(
                    f"**Assigned To:** {selected_ticket.get('assigned_to', 'Unassigned')}"
                )
                st.write(
                    f"**Created Date:** {selected_ticket.get('created_date', 'N/A')}"
                )

            st.write(
                f"**Description:** {selected_ticket.get('description', 'No description')}"
            )

            if st.button("Analyze with AI", type="primary"):
                self._analyze_ticket(selected_ticket)

    def _analyze_ticket(self, selected_ticket):
        with st.spinner("Analyzing ticket..."):
            try:
                client = genai.Client(
                    api_key="AIzaSyB3fmYyMw62cMfNKtDW1dcGKVZgkzAHsR4"
                )
                model = "gemini-2.5-flash"

                analysis_prompt = f"""
                    Analyze the following IT ticket and provide insights and recommendations:
                    Ticket ID: {selected_ticket['ticket_id']}
                    Priority: {selected_ticket['priority']}
                    Status: {selected_ticket['status']}
                    Category: {selected_ticket.get('category', 'N/A')}
                    Description: {selected_ticket.get('description', 'N/A')}
                    Assigned To: {selected_ticket.get('assigned_to', 'Unassigned')}
                    Created Date: {selected_ticket.get('created_date', 'N/A')}

                    Provide:
                    1. Root cause analysis
                    2. Immediate actions needed
                    3. Resolution recommendations
                    4. Priority assessment
                    5. Estimated resolution time
                """

                response = client.models.generate_content_stream(
                    model=model,
                    contents=analysis_prompt,
                )

                st.subheader("AI Analysis Results")

                container = st.empty()
                full_reply = ""

                for chunk in response:
                    if chunk.text:
                        full_reply += chunk.text
                        container.markdown(full_reply)
            except Exception as e:
                st.error(f"Error analyzing ticket: {str(e)}")


if __name__ == "__main__":
    AITicketAnalyzerApp().run()