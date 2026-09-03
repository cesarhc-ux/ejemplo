import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        raise ValueError("Falta SUPABASE_URL en el archivo .env")

    if not supabase_key:
        raise ValueError("Falta SUPABASE_KEY en el archivo .env")

    return create_client(supabase_url, supabase_key)