import ollama

def ask_server(model, prompt):
    r = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}],
                    think=False, options={"temperature": 0, "num_predict": 60})
    return r.message.content.strip().split("\n")[0]

tests = [("프랑스", "파리"), ("일본", "도쿄"), ("이집트", "카이로"), ("캐나다", "오타와"), ("호주", "캔버라")]
shots = {
    0: "",
    1: "한국 → 서울\n",
    3: "한국 → 서울\n독일 → 베를린\n브라질 → 브라질리아\n",
}

for model in ["qwen3:1.7b", "qwen3:8b"]:
    for k, examples in shots.items():
        correct = 0
        for country, capital in tests:
            answer = ask_server(model, examples + f"{country} →")
            correct += capital in answer
        print(f"{model:11s} 예시 {k}개  정답 {correct}/5")