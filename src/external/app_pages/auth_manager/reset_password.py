import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

from src.adapters.controller import Controller


def reset_password_page(authenticator, credentials, username, placeholder_msg):
    try:
        col1, col2 = st.columns(2)
        if "admin" == username:
            selected_username = col1.selectbox(
                "Select username",
                list(credentials["usernames"]),
                index=list(credentials["usernames"]).index(username),
            )
            submited = authenticator.reset_password(selected_username, "Reset password")
        else:
            selected_username = username
            submited = authenticator.reset_password(username, "Reset password")

        if submited:
            #############################################################
            ### UPDATE USER PASSWORD ###
            #############################################################
            request = {
                "resource": "/user/update_detail",
                "user_username": selected_username,
                "user_password": credentials["usernames"][username]["password"],
            }

            controller = Controller()
            resp = controller(request=request)
            msg = resp.get("messages")

            messages = resp["messages"]
            entities = resp["entities"]

            if messages:
                raise Exception("\n\n".join(messages))
            #############################################################

            st.success(f"User password has been updated successfully")

    except Exception as e:
        placeholder_msg.error(e)
        st.error(e)
