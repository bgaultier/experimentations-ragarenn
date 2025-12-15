import gradio as gr
import random
import os
from mcp import StdioServerParameters
from smolagents import MCPClient, GradioUI, CodeAgent, OpenAIServerModel
from openai import OpenAI

# Import our custom tools from their modules
from tools import DuckDuckGoSearchTool, WeatherInfoTool

# Initialize RAGaRenn API client
RAGARENN_BASE_URL = "https://ragarenn.eskemm-numerique.fr/sso/instance@imt/api/"
RAGARENN_IMT_API_KEY = os.getenv("RAGARENN_IMT_API_KEY")

if not RAGARENN_IMT_API_KEY:
    raise ValueError("Rennes API Key not set - please check your .env file")

ragarenn = OpenAI(base_url=RAGARENN_BASE_URL, api_key=RAGARENN_IMT_API_KEY)

# List available models from ragarenn
try:
    models = ragarenn.models.list()
    print("Available models from ragarenn:")
    for model in models.data:
        print(model.id)
except Exception as e:
    print(f"Error fetching models: {str(e)}")

model = OpenAIServerModel(
    model_id=models.data[0].id,
    api_base=RAGARENN_BASE_URL,   # your OpenAI-compatible base URL
    api_key=RAGARENN_IMT_API_KEY,
    temperature=0.95,
    max_tokens=2048,
    flatten_messages_as_text=True,  # key workaround for picky servers
)

# Initialize the web search tool
search_tool = DuckDuckGoSearchTool()

# Initialize the weather tool
weather_info_tool = WeatherInfoTool()

# Initialize playwright tool
server_parameters = StdioServerParameters(
    command="npx",
    args=["@playwright/mcp@latest"]
)

playwright_client = MCPClient(server_parameters, structured_output=True)
playwright_tools = playwright_client.get_tools()

# Create Alfred with all the tools
alfred = CodeAgent(
    tools=[weather_info_tool, search_tool, *playwright_tools], 
    model=model,
    add_base_tools=True,  # Add any additional base tools
    planning_interval=3   # Enable planning every 3 steps
)

if __name__ == "__main__":
    GradioUI(alfred).launch()