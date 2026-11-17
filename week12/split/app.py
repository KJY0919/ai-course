import base64, json, re
from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(base_url="https://krchoi.com/gemma4/v1", api_key="none")

def ask(prompt, image_bytes=None, mime="image/jpeg"):
    content = [{"type": "text", "text": prompt}]
    if image_bytes:
        url = f"data:{mime};base64," + base64.b64encode(image_bytes).decode()
        content.append({"type": "image_url", "image_url": {"url": url}})
    r = client.chat.completions.create(model="gemma4", messages=[{"role": "user", "content": content}])
    return r.choices[0].message.content

def parse_json(text):
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    try:
        return json.loads(m.group(1) if m else text)
    except (json.JSONDecodeError, TypeError):
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    total_amount = None
    people_count = None
    per_person = None
    error = None
    items = None

    if request.method == 'POST':
        try:
            people_count_form = request.form.get('people_count')
            
            # Case 1: Image Upload (OCR)
            if 'receipt_image' in request.files and request.files['receipt_image'].filename != '':
                image_file = request.files['receipt_image']
                image_bytes = image_file.read()
                
                prompt = "영수증 이미지에서 항목 이름과 금액을 추출해서 JSON 형식으로만 답해줘. 형식: [{\"item\": \"항목명\", \"price\": 1000}, ...]"
                ai_response = ask(prompt, image_bytes)
                items = parse_json(ai_response)

                if items:
                    total_amount = sum(item.get('price', 0) for item in items)
                    people_count = int(people_count_form) if people_count_form else 1
                    if people_count <= 0:
                        error = "인원수는 1명 이상이어야 합니다."
                        items = None
                        total_amount = None
                    else:
                        per_person = total_amount / people_count
                else:
                    error = "읽지 못했습니다"
                    items = None
                    total_amount = None
                    per_person = None
            
            # Case 2: Manual Input
            else:
                total_amount_form = request.form.get('total_amount')
                if total_amount_form:
                    total_amount = float(total_amount_form)
                    people_count = int(people_count_form) if people_count_form else 1
                    
                    if people_count <= 0:
                        error = "인원수는 1명 이상이어야 합니다."
                    else:
                        per_person = total_amount / people_count
                else:
                    error = "금액을 입력해주세요."

        except ValueError:
            error = "올바른 숫자를 입력해주세요."
        except Exception as e:
            error = f"오류 발생: {str(e)}"

    return render_template('index.html', 
                           total_amount=total_amount, 
                           people_count=people_count, 
                           per_person=per_person,
                           error=error,
                           items=items)

if __name__ == '__main__':
    app.run(debug=True)
