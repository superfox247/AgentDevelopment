import os

from google.adk.apps.app import App

from agent_platform.callbacks import create_save_output_callback
from agent_platform.yaml_loader import load_agent_from_yaml

# --- Customer Service Agent ---
yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
customer_service = load_agent_from_yaml(yaml_path)
customer_service.after_agent_callback = create_save_output_callback("customer_service_output")

app = App(root_agent=customer_service, name="customer_service")
