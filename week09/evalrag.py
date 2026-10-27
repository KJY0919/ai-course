import sqlite3
import ollama
import numpy as np

con = sqlite3.connect("campus.db")
rows = con.execute("SELECT id, name, embedding FROM facility").fetchall()
names = [r[1] for r in rows]
V = np.stack([np.frombuffer(r[2], dtype=np.float32) for r in rows])
V = V / np.linalg.norm(V, axis=1, keepdims=True)

# (질문, 정답 시설 이름)
TESTS = [
    ("과제 출력하려면 어디로 가?", "프린터실"),
    ("밤 늦게까지 공부할 수 있는 데 있어?", "열람실"),
    ("조별 과제 모여서 할 방 어떻게 빌려?", "그룹 스터디룸"),
    ("차 가지고 와도 돼?", "주차장"),
    ("휴학 서류 어디 내?", "학과 사무실"),
    ("학생증 다시 만들려면?", "학생지원팀"),
    ("재학증명서 뽑는 기계 어디 있어?", "무인 증명서 발급기"),
    ("점심 제일 싼 데가 어디야?", "학생 식당"),
    ("운동 기구 쓰려면 돈 내야 해?", "헬스장"),
    ("택배 보내려면?", "우체국"),
    ("빨래는 어디서 해?", "세탁실"),
    ("GPU 있는 컴퓨터 쓸 수 있는 데?", "소프트웨어 실습실 B"),
]

hit1 = hit3 = 0
for q, want in TESTS:
    qv = np.array(ollama.embed(model="bge-m3", input=q).embeddings[0])
    qv = qv / np.linalg.norm(qv)
    top = [names[i] for i in np.argsort(-(V @ qv))[:3]]
    ok1, ok3 = top[0] == want, want in top
    hit1 += ok1
    hit3 += ok3
    print("O" if ok1 else ("△" if ok3 else "X"), q, "->", top[0], "" if ok1 else f"(정답 {want}, 3위 안 {ok3})")
print(f"\n1위 적중 {hit1}/{len(TESTS)}, 3위 안 적중 {hit3}/{len(TESTS)}")