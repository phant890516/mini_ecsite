from flask import Flask, make_response, render_template, session, request

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # read Class from config.py
    app.config.from_object('config.Config')
        
    # Blueprint setting
    from .views import products,auth
    app.register_blueprint(products.products_bp)
    app.register_blueprint(auth.auth_bp)

    # top page route
    @app.route('/')
    def index():
        # get username, role from session and submit
        username=request.cookies.get('username')
        if not username:
            username=None
       
        resp=make_response(render_template('index.html',username=username))
        return resp

    return app