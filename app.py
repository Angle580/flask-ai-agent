from flask import Flask, render_template, request, jsonify, session
from agent import run_agent

app = Flask(__name__)
app.secret_key = 'agent-demo'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '').strip()
    if not user_msg:
        return jsonify({"error": "empty"}), 400
    # 从 session 取历史（简单保存最近 10 轮）
    history = session.get('history', [])
    try:
        answer, trace = run_agent(user_msg, history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # 更新历史
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": answer})
    session['history'] = history[-20:]
    return jsonify({"answer": answer, "trace": trace})

@app.route('/api/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
