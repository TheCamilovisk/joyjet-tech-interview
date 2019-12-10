from flask import Flask, request, jsonify


def _compute_cart_total(items, articles):
    '''Helper function that computes the sum of the prices of articles in one cart.

    :param items: The list of items of the cart.
    :param articles: Dictionary conaining the data of all items
    :returns: The total sum of the cart items.
    '''
    total = 0
    for item in items:
        article = articles[item['article_id']]
        total += article['price'] * item['quantity']
    return total


def create_app(config=None):
    app = Flask(__name__)
    if config == 'test':
        app.config['TEST'] = True

    @app.route('/checkout', methods=['POST'])
    def checkout():
        # Retrieve the request data.
        data = request.get_json()

        # Retrieve the articles and carts data. Return an error if none of them are found.
        articles = data.get('articles', None)
        carts = data.get('carts', None)
        if articles is None or carts is None:
            return jsonify(msg='The articles and carts data must be provided'), 400

        # Turns the list of articles into a dictionary. This will facilitate the retrieving of the items data.
        articles = {
            item['id']: {'name': item['name'], 'price': item['price']}
            for item in articles
        }

        # Computes the sum of the prices of articles in each cart.
        carts_totals = [
            {'id': cart['id'], 'total': _compute_cart_total(cart['items'], articles)}
            for cart in carts
        ]

        return jsonify(carts=carts_totals), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
