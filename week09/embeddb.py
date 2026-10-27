import sqlite3
import ollama
import numpy as np

con = sqlite3.connect("campus.db")
columns = [c[1] for c in con.execute("PRAGMA table_info(facility)")]
if "embedding" not in columns:
    con.execute("ALTER TABLE facility ADD COLUMN embedding BLOB")


def row_to_text(name, building, floor, hours, category, description):
    return f"{name}. {building} {floor}층. {category}. 운영시간 {hours}. {description}"


rows = con.execute("SELECT id, name, building, floor, hours, category, description FROM facility").fetchall()
for i, (id_, *fields) in enumerate(rows):
    text = row_to_text(*fields)
    v = np.array(ollama.embed(model="bge-m3", input=text).embeddings[0], dtype=np.float32)
    con.execute("UPDATE facility SET embedding = ? WHERE id = ?", (v.tobytes(), id_))
    print(f"\r{i + 1}/{len(rows)} {text[:40]}", end="   ")
con.commit()
print("\n완료")
print("예:", row_to_text(*rows[0][1:]))