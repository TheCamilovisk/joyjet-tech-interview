from flask import Flask, make_response


def create_app(config=None):
    app = Flask(__name__)
    if config == 'test':
        app.config['TEST'] = True

    @app.route('/checkout', methods=['POST'])
    def checkout():
        response = make_response({'msg': 'This is the response'}, 200)
        response.mimetype = 'application/json'
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
