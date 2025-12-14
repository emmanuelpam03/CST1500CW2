import streamlit as st
from app.services.user_service import login_user


class LoginApp:
    def run(self):
        self._redirect_if_logged_in()
        self._render_ui()
        self._handle_login()

    def _redirect_if_logged_in(self):
        if st.session_state.get("logged_in"):
            st.switch_page("pages/Dashboard.py")

    def _render_ui(self):
        st.title("Login")
        self.username = st.text_input("Username")
        self.password = st.text_input("Password", type="password")
        st.page_link("pages/Register.py", label="Don't have an account? Register")

    def _handle_login(self):
        if st.button("Login"):
            success, message = login_user(self.username, self.password)
            if success:
                from app.data.users import get_user_by_username

                user = get_user_by_username(self.username)
                st.session_state["logged_in"] = True
                st.session_state["username"] = self.username
                st.session_state["user_role"] = (
                    user["role"] if user else "user"
                )
                st.switch_page("pages/Dashboard.py")
            else:
                st.error(message)


if __name__ == "__main__":
    LoginApp().run()
