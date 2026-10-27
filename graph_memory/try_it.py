from pathlib import Path

from db import get_connection
from memory import preferences_as_text, remember_preference

# Throwaway DB, so the real data/graph.kuzu is never touched.
conn = get_connection(Path("try_it.kuzu"))

remember_preference(conn, "sai", "express", "fastify")
remember_preference(conn, "sai", "fastify", "express")
remember_preference(conn, "sai", "react", "express")

print(preferences_as_text(conn, "sai"))
print(preferences_as_text(conn, "nobody"))
