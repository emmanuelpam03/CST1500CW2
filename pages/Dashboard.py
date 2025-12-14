import streamlit as st
import pandas as pd
from app.data.users import get_user_by_username, list_users
from app.data.datasets import get_all_datasets_metadata
from app.services.user_service import register_user

class DashboardApp:
    def run(self):
        self._check_auth()
        self._render_header()
        self._resolve_user_role()
        self._render_logout()
        st.divider()
        self._render_datasets()
        st.divider()
        self._render_user_management()

    def _check_auth(self):
        if not st.session_state.get("logged_in"):
            st.switch_page("pages/Login.py")

    def _render_header(self):
        st.title("Dashboard")
        self.username = st.session_state.get("username", "User")
        st.write(f"Welcome, {self.username}!")

    def _resolve_user_role(self):
        self.user_role = st.session_state.get("user_role")
        if not self.user_role:
            current_user = get_user_by_username(self.username)
            self.user_role = current_user["role"] if current_user else "user"
            st.session_state["user_role"] = self.user_role

    def _render_logout(self):
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["user_role"] = None
            st.switch_page("pages/Login.py")

    def _render_datasets(self):
        st.subheader("Datasets Metadata")
        with st.spinner("Loading datasets metadata..."):
            datasets_df = get_all_datasets_metadata()

        if datasets_df.empty:
            st.info("No datasets metadata found.")
        else:
            display_df = datasets_df.copy()
            if "created_at" in display_df.columns:
                display_df = display_df.drop(columns=["created_at"])
            display_df = display_df.fillna("N/A")
            st.dataframe(display_df, use_container_width=True)

    def _render_user_management(self):
        if self.user_role == "admin":
            st.subheader("User Management")

            st.write("**Users List**")
            users = list_users()
            if users:
                users_data = []
                for user in users:
                    users_data.append(
                        {
                            "ID": user["id"],
                            "Username": user["username"],
                            "Role": user["role"],
                            "Created At": user["created_at"],
                        }
                    )
                users_df = pd.DataFrame(users_data)
                st.dataframe(users_df, use_container_width=True)
            else:
                st.info("No users found.")

            st.write("**Create New User**")
            with st.form("create_user_form", clear_on_submit=True):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["user", "admin"], index=0)

                submitted = st.form_submit_button("Create User")

                if submitted:
                    if not new_username or not new_password:
                        st.error("Username and password are required!")
                    else:
                        success, message = register_user(
                            new_username, new_password, new_role
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("User management is only available for administrators.")

if __name__ == "__main__":
    DashboardApp().run()
