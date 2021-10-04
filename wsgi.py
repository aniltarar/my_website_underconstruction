from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9000, ssl_context=('/etc/letsencrypt/live/www.neil-tarar.com/fullchain.pem', '/etc/letsencrypt/live/www.neil-tarar.com/privkey.pem'))