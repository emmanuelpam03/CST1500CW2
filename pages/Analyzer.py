import streamlit as st
from app.data.incidents import get_all_incidents
from google import genai
from google.genai import types

class IncidentAnalyzerApp:
    def __init__(self):
        self.incidents = None
        self.selected_incident = None
        self.model = "gemini-2.5-flash"
        self.client = genai.Client(
            api_key="AIzaSyB3fmYyMw62cMfNKtDW1dcGKVZgkzAHsR4"
        )

    def run(self):
        self._check_auth()
        self._render_title()
        self._load_incidents()
        self._render_incident_selector()
        self._render_incident_details()
        self._render_analysis_button()

    def _check_auth(self):
        if not st.session_state.get("logged_in"):
            st.switch_page("pages/Login.py")

    def _render_title(self):
        st.title("All Incident Analyzer")

    def _load_incidents(self):
        with st.spinner("Loading incidents..."):
            self.incidents = get_all_incidents()

        if self.incidents.empty:
            st.error("No incidents found.")

    def _render_incident_selector(self):
        if self.incidents.empty:
            return

        labels = [
            f"{row['id']}: {row['incident_type']} - {row['severity']}"
            for _, row in self.incidents.iterrows()
        ]

        choice = st.selectbox(
            label="Select incident to analyze:",
            options=labels,
            placeholder="Select an option",
            key="dashboard_option",
        )

        selected_id = int(choice.split(":")[0])
        self.selected_incident = self.incidents.loc[
            self.incidents["id"] == selected_id
        ].iloc[0]

    def _render_incident_details(self):
        if self.selected_incident is None:
            return

        st.subheader("Incident Details")
        st.write(f"Type: {self.selected_incident['incident_type']}")
        st.write(f"Severity: {self.selected_incident['severity']}")
        st.write(f"Description: {self.selected_incident['description']}")
        st.write(f"Status: {self.selected_incident['status']}")

    def _render_analysis_button(self):
        if self.selected_incident is None:
            return

        if st.button("Analyze with AI", type="primary"):
            self._analyze_incident()

    def _analyze_incident(self):
        with st.spinner("Analyzing incident..."):
            prompt = self._build_prompt()
            response = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
            )

            st.subheader("AI Analysis Results")
            self._stream_response(response)

    def _build_prompt(self):
        return f"""
        Analyze the following cyber incident and provide insights and recommendations:
        Incident ID: {self.selected_incident['id']}
        Type: {self.selected_incident['incident_type']}
        Severity: {self.selected_incident['severity']}
        Description: {self.selected_incident['description']}
        Status: {self.selected_incident['status']}

        Provide:
        1. Root cause analysis
        2. Immediate actions needed
        3. Long-term prevention measures
        4. Risk assessment
        """

    def _stream_response(self, response):
        container = st.empty()
        full_reply = ""

        for chunk in response:
            if chunk.text:
                full_reply += chunk.text
                container.markdown(full_reply)

if __name__ == "__main__":
    app = IncidentAnalyzerApp()
    app.run()
