from flask import Flask, render_template, request, jsonify
import random
import string
import re
import math
import numpy as np
from sklearn.linear_model import LogisticRegression

# 🔥 TO‘G‘RI YOZILISH
app = Flask(__name__)

# Common weak passwords
COMMON_PASSWORDS = [
    "123456", "password", "123456789", "12345678", "12345", "qwerty",
    "abc123", "football", "monkey", "letmein"
]

# ======================
# 🤖 AI MODEL (Logistic Regression)
# ======================

X = [
    [4,0,1,0,0],
    [6,0,1,1,0],
    [10,1,1,1,1],
    [12,1,1,1,1],
    [5,0,1,0,0]
]

y = [0, 0, 2, 2, 1]  # 0=Weak, 1=Medium, 2=Strong

model = LogisticRegression()
model.fit(X, y)

def extract_features(password):
    return [
        len(password),
        int(bool(re.search(r"[A-Z]", password))),
        int(bool(re.search(r"[a-z]", password))),
        int(bool(re.search(r"\d", password))),
        int(bool(re.search(r"[!@#$%^&*]", password)))
    ]

def ai_predict(password):
    features = np.array(extract_features(password)).reshape(1, -1)
    prediction = model.predict(features)[0]

    if prediction == 0:
        return "Weak (AI)"
    elif prediction == 1:
        return "Medium (AI)"
    else:
        return "Strong (AI)"

# ======================
# ENTROPY
# ======================
def calculate_entropy(password):
    charset_size = 0

    if re.search(r"[a-z]", password):
        charset_size += 26
    if re.search(r"[A-Z]", password):
        charset_size += 26
    if re.search(r"\d", password):
        charset_size += 10
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        charset_size += 32

    if charset_size == 0:
        return 0

    entropy = len(password) * math.log2(charset_size)
    return round(entropy, 2)

# ======================
# PASSWORD GENERATOR
# ======================
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*(),.?\":{}|<>"
    return "".join(random.choice(characters) for _ in range(length))

# ======================
# ANALYZE FUNCTION
# ======================
def analyze_password(password):
    score = 0
    messages = []

    messages.append(f"You entered: {password}")

    if len(password) >= 8:
        score += 15
    else:
        messages.append("Password is too short (min 8 characters)")

    if len(password) >= 12:
        score += 10

    if re.search(r"[A-Z]", password):
        score += 15
    else:
        messages.append("Add uppercase letters")

    if re.search(r"[a-z]", password):
        score += 15
    else:
        messages.append("Add lowercase letters")

    if re.search(r"\d", password):
        score += 15
    else:
        messages.append("Add numbers")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 15
    else:
        messages.append("Add special symbols")

    if password.lower() in COMMON_PASSWORDS:
        messages.append("This password is very common!")
        score -= 20

    entropy = calculate_entropy(password)

    if entropy >= 60:
        score += 20
    else:
        messages.append(f"Low entropy ({entropy} bits)")

    score = max(0, min(score, 100))

    if score < 50:
        strength = "Weak ❌"
    elif score < 80:
        strength = "Medium ⚠️"
    else:
        strength = "Strong ✅"

    # 🔥 AI RESULT
    ai_strength = ai_predict(password)

    messages.append(f"Strength: {strength}")
    messages.append(f"AI Prediction: {ai_strength}")
    messages.append(f"Score: {score}/100")

    suggestion = None
    if strength != "Strong ✅":
        suggestion = generate_password()
        messages.append(f"Suggested password: {suggestion}")

    return messages, score, strength, suggestion, ai_strength

# ======================
# ROUTES
# ======================
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    password = data.get("password", "")

    messages, score, strength, suggestion, ai_strength = analyze_password(password)
    return jsonify({
        "messages": messages,
        "score": score,
        "strength": strength,
        "ai_strength": ai_strength,
        "suggestion": suggestion
    })

    # ======================
    # RUN
    # ======================
if __name__ == "__main__":
    app.run(debug=True)