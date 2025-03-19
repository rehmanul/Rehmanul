"""
Web Application for Web Stryker R7 Python Edition
"""
from flask import Flask, jsonify, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, emit
from config import config
from web.database import init_db_pool, get_db_cursor
import logging
import os
import asyncio

# Initialize SocketIO globally
socketio = SocketIO()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder=os.path.join('web', 'templates'),
                static_folder=os.path.join('web', 'static'))
    
    # Load configuration
    app.config.from_object(config)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
    
    # Initialize extensions
    socketio.init_app(app, async_mode='gevent', logger=True, engineio_logger=True)

    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        app.logger.info('Client connected via WebSocket')
        emit('connection_response', {'status': 'connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        app.logger.info('Client disconnected from WebSocket')

    # Register routes
    @app.route('/')
    def home():
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    def dashboard():
        try:
            with get_db_cursor() as cursor:
                # Get total extractions
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                        COUNT(DISTINCT url) as unique_urls
                    FROM extractions
                """)
                stats = cursor.fetchone()
                
                # Get recent activity
                cursor.execute("""
                    SELECT url, status, created_at, result
                    FROM extractions 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                recent_activity = cursor.fetchall()
                
                # Get extraction categories
                cursor.execute("""
                    SELECT category, COUNT(*) as count
                    FROM extractions 
                    GROUP BY category
                """)
                category_data = cursor.fetchall()
                total = sum(row['count'] for row in category_data)
                categories = [
                    {
                        'name': row['category'],
                        'percentage': (row['count'] / total) * 100
                    }
                    for row in category_data
                ] if total > 0 else []
                
        except Exception as e:
            app.logger.error(f"Database error in dashboard: {str(e)}")
            stats = {'total': 0, 'successful': 0, 'pending': 0, 'unique_urls': 0}
            recent_activity = []
            categories = []
        
        theme = session.get('theme', 'light')
        
        return render_template('dashboard.html', 
                             active_page='dashboard',
                             stats=stats,
                             recent_activity=recent_activity,
                             categories=categories,
                             theme=theme)

    @app.route('/extract')
    def extract_data():
        theme = session.get('theme', 'light')
        return render_template('extraction.html', active_page='extract', theme=theme)

    @app.route('/api/extract', methods=['POST'])
    async def start_extraction():
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        from web.extractors.web_content import WebContentExtractor
        
        extraction_id = f'ext_{hash(data["url"])}'
        socketio.emit('extraction_started', {
            'id': extraction_id,
            'url': data['url'],
            'status': 'pending'
        })
        
        def perform_extraction():
            async def extract():
                try:
                    extractor = WebContentExtractor()
                    # Update progress
                    socketio.emit('extraction_progress', {
                        'id': extraction_id,
                        'progress': 25,
                        'status': 'fetching'
                    })
                    
                    async with extractor:
                        result = await extractor.extract(data['url'])
                    
                    # Update progress
                    socketio.emit('extraction_progress', {
                        'id': extraction_id,
                        'progress': 75,
                        'status': 'processing'
                    })
                    
                    if result.status == 'success':
                        socketio.emit('extraction_complete', {
                            'id': extraction_id,
                            'status': 'success',
                            'data': {
                                'title': result.title,
                                'content': result.content,
                                'metadata': result.metadata
                            }
                        })
                    else:
                        socketio.emit('extraction_error', {
                            'id': extraction_id,
                            'error': result.error or 'Unknown error'
                        })
                except Exception as e:
                    app.logger.error(f'Extraction error for {data["url"]}: {str(e)}')
                    socketio.emit('extraction_error', {
                        'id': extraction_id,
                        'error': str(e)
                    })

            socketio.start_background_task(
                lambda: asyncio.run(extract())
            )
        
        return jsonify({
            'status': 'success',
            'message': 'Extraction started',
            'extraction_id': extraction_id
        })

    @app.route('/data-center')
    def data_center():
        theme = session.get('theme', 'light')
        return render_template('data_center.html', active_page='data_center', theme=theme)

    @app.route('/recent')
    def recent_extractions():
        theme = session.get('theme', 'light')
        extractions = []  # TODO: Get from database
        return render_template('results.html', 
                             active_page='recent', 
                             extractions=extractions,
                             theme=theme)

    @app.route('/logs')
    def logs():
        theme = session.get('theme', 'light')
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # Get total log entries count
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM logs")
            total = cursor.fetchone()[0]
            
            # Get paginated log entries
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT timestamp, level, message 
                FROM logs 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            """, (per_page, offset))
            log_entries = cursor.fetchall()
        
        # Create pagination object
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'has_prev': page > 1,
            'has_next': page * per_page < total,
            'iter_pages': lambda left_edge=2, right_edge=2, left_current=2, right_current=5: 
                range(max(1, page - left_current), min(page + right_current + 1, (total // per_page) + 1))
        }
        
        return render_template('logs.html', 
                             active_page='logs',
                             logs=log_entries,
                             pagination=pagination,
                             theme=theme)

    @app.route('/api/theme', methods=['POST'])
    def update_theme():
        data = request.get_json()
        if 'theme' in data:
            session['theme'] = data['theme']
            return jsonify({'status': 'success'})
        return jsonify({'error': 'No theme specified'}), 400

    @app.route('/health')
    def health_check():
        """Health check endpoint for container orchestration"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'uptime': 'OK'
        }), 200

    @app.errorhandler(404)
    def not_found_error(error):
        theme = session.get('theme', 'light')
        return render_template('404.html', theme=theme), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        theme = session.get('theme', 'light')
        return render_template('500.html', theme=theme), 500

    return app

# Create the Flask application
app = create_app()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
</environment_details>
