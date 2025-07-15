from setuptools import setup, find_packages

setup(
    name="agent-caddie",
    version="0.1.0",
    packages=find_packages(),            # finds agent_caddie
    install_requires=[
        "openai",
        "supabase",
        "click",
        "questionary",
        "tabulate",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            # makes `agent-caddie` available on your PATH
            "agent-caddie=agent_caddie.cli:cli"
        ]
    },
)
