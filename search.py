import ollama
import numpy as np

def emb(text):
    return np.array(ollama.embed(model="bge-m3", input=text).embeddings[0])

docs = [
    "기말고사는 12월 셋째 주에 실시한다",
    "도서관은 평일 오전 9시부터 오후 10시까지 연다",
    "장학금 신청은 학기 시작 후 2주 안에 해야 한다",
    "휴학 신청은 학과 사무실에서 서류를 받아 제출한다",
    "동아리 등록은 매년 3월에 한 번 받는다",
    "학생증을 잃어버리면 학생지원팀에서 재발급한다",
    "수강 신청 변경 기간은 개강 후 첫 주다",
    "기숙사는 2인 1실이며 식당은 1층에 있다",
    "졸업 요건은 130학점 이상 이수와 졸업 작품 제출이다",
    "주차장은 학생증을 등록한 차량만 이용할 수 있다",
]
D = np.stack([emb(d) for d in docs])          # 문서 10개를 미리 벡터로 (10 x 1024)

def search(question, k=3):
    q = emb(question)
    sims = D @ q / (np.linalg.norm(D, axis=1) * np.linalg.norm(q))   # 문서 10개와의 코사인을 한 번에
    for i in np.argsort(-sims)[:k]:
        print(f"   {sims[i]:.3f}  {docs[i]}")

for question in ["시험 언제야?", "책 빌리는 곳 몇 시에 닫아?", "학교 그만두려면 어떻게 해?",
                 "졸업하려면 뭐가 필요해?", "장학금 신청 기간이 지났으면 어떻게 해?"]:
    print("Q:", question)
    search(question)