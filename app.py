"""
Flask web application for the Multi-Agent Tourism System.
"""
import os
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from tourism_agent import TourismAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))  # For session management
CORS(app, supports_credentials=True)

# Initialize the tourism agent
tourism_agent = TourismAgent()


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def process_query():
    """
    Process user query and return response.
    
    Expected JSON: {"query": "user input", "history": [optional conversation history]}
    Returns JSON: {"response": "agent response", "success": true/false, "history": updated history}
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        user_query = data['query'].strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Get conversation history from request or session
        history = data.get('history', [])
        if not history and 'conversation_history' in session:
            history = session['conversation_history']
        
        # Process the query using the tourism agent
        response = tourism_agent.process_query(user_query, history)
        
        # Update session with conversation history
        session['conversation_history'] = tourism_agent.conversation_history
        
        return jsonify({
            'success': True,
            'response': response,
            'history': tourism_agent.conversation_history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Multi-Agent Tourism System'
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
