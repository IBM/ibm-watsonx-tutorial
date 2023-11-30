#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

sys.path.append('<workspcae>\\Django-Prj\\WatsonxPrj\\WatsonxPrj')
''' ----------------------------------------------------'''




from WatsonxPrj import settings
from dotenv import load_dotenv
#Set  load .env 
load_dotenv(dotenv_path=f"{settings.BASE_DIR}/WatsonxPrj/.env")

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WatsonxPrj.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    url = os.environ.get("WATSONX_URL")
    print(f"***LOG: - url: {url}")
    main()
