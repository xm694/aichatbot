import streamlit as st
from typing import Optional

class APIKeyManager:
    """Manages API keys in Streamlit session state with optional persistent storage."""
    
    def __init__(self):
        # Initialize session state for API keys if not exists
        if 'api_keys' not in st.session_state:
            st.session_state.api_keys = {
                'openai': '',
                'langchain': ''
            }
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key from session state."""
        return st.session_state.api_keys.get(key_name)
    
    def set_api_key(self, key_name: str, value: str):
        """Set API key in session state."""
        st.session_state.api_keys[key_name] = value

def render_api_key_form():
    """Render the API key input form in Streamlit."""
    key_manager = APIKeyManager()
    
    st.sidebar.header("API Configuration")
    
    with st.sidebar.expander("API Keys", expanded=True):
        # OpenAI API Key input
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=key_manager.get_api_key('openai') or "",
            help="Enter your OpenAI API key",
            key="openai_key_input"
        )
        
        # Langchain API Key input
        langchain_key = st.text_input(
            "Langchain API Key",
            type="password",
            value=key_manager.get_api_key('langchain') or "",
            help="Enter your Langchain API key",
            key="langchain_key_input"
        )
        
        if st.button("Save API Keys"):
            key_manager.set_api_key('openai', openai_key)
            key_manager.set_api_key('langchain', langchain_key)
            st.success("API keys saved successfully!")

def get_api_configuration():
    """Get the current API configuration."""
    key_manager = APIKeyManager()
    
    return {
        'openai_api_key': key_manager.get_api_key('openai'),
        'langchain_api_key': key_manager.get_api_key('langchain'),
        'langchain_tracing_v2': "true",
        'langchain_endpoint': "https://api.smith.langchain.com",
        'langchain_project': "database-chatbot"
    }