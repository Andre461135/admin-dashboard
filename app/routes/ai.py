from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required
from app.utilities.ai_helpers import AIAssistant

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/insights')
@login_required
def get_insights():
    insights = AIAssistant.dashboard_insights()
    return jsonify({'insights': insights})


@ai_bp.route('/sales-summary')
@login_required
def get_sales_summary():
    summary = AIAssistant.sales_summary()
    return jsonify({'summary': summary})


@ai_bp.route('/trends')
@login_required
def get_trends():
    analysis = AIAssistant.trend_analysis()
    return jsonify({'analysis': analysis})


@ai_bp.route('/search')
@login_required
def smart_search():
    query = request.args.get('q', '').strip()
    results = AIAssistant.smart_search(query)
    data = {
        'users': [{'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role}
                  for u in results['users']],
        'products': [{'id': p.id, 'name': p.name, 'category': p.category, 'price': p.price}
                     for p in results['products']],
        'transactions': [{'id': t.id, 'amount': t.amount, 'status': t.status}
                         for t in results['transactions']],
    }
    return jsonify(data)


@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    message = request.json.get('message', '').strip()
    if not message:
        return jsonify({'response': 'Please enter a message.'})

    response = AIAssistant.chatbot_response(message)
    return jsonify({'response': response})


@ai_bp.route('/assistant')
@login_required
def assistant():
    return render_template('ai_assistant.html')
