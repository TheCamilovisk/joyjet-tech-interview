from flask import Flask, request, jsonify


def _compute_discount(article_price, discount):
    '''Helper function that computes an item's discount amount.

    :param article_price: The product's original price.
    :param discount: The product's discount information.
        There are two kinds of discounts:
        - a direct cut to the article's price, e.g. get 50€ off your 300€ caviar tin and only pay 250€
        - a percentage discount, e.g. get 20% off your 5€ creme fraiche and only pay 4€
    '''
    # Direct cut to the article's price
    if discount['type'] == 'amount':
        return article_price - discount['value']
    # Percentage discount
    else:
        return int(article_price * (1 - discount['value'] / 100))


def _compute_cart_total(items, articles, discounts=None):
    '''Helper function that computes the sum of the prices of articles in one cart.

    :param items: The list of items of the cart.
    :param articles: Dictionary containing the data of all items.
    :param discounts: Dictionary containing the discounts data. If not supplied, no discounts are applied.
    :returns: The total sum of the cart items.
    '''
    total = 0
    for item in items:
        article_id = item['article_id']
        article = articles[article_id]
        article_price = article['price']

        if discounts is not None:
            discount = discounts.get(article_id, {'type': 'amount', 'value': 0})
            article_price = _compute_discount(article_price, discount)

        total += article_price * item['quantity']
    return total


def _get_delivery_fee(cart_total, delivery_fees):
    '''Helper function that retrieves the delivery fee cost of a cart given its total cost.

    :param cart_total: The total cost of a cart items.
    :param delivery_fee: A list of tuples containing the transaction volume min and max of the delivery fees and
    their cost values.
    :returns:  The delivery fee cost of the cart.
    '''
    return next(
        cost
        for min_price, max_price, cost in delivery_fees
        if cart_total >= min_price and (max_price is None or cart_total < max_price)
    )


def create_app(config=None):
    app = Flask(__name__)
    if config == 'test':
        app.config['TEST'] = True

    @app.route('/checkout', methods=['POST'])
    def checkout():
        # Retrieves the request data.
        data = request.get_json()

        # Retrieves the articles and carts data. Return an error if none of them are found.
        articles = data.get('articles', None)
        carts = data.get('carts', None)
        if articles is None or carts is None:
            return jsonify(msg='The articles and carts data must be provided'), 400

        # Turns the list of articles into a dictionary. This will facilitate the retrieving of the items data.
        articles = {
            item['id']: {'name': item['name'], 'price': item['price']}
            for item in articles
        }

        # Retrieves the discounts, if they were supplied.
        discounts = data.get('discounts', None)

        if discounts is not None:
            # Turns the list of discounts into a dictionary. This will facilitate the retrieving of the items data.
            discounts = {
                item['article_id']: {'type': item['type'], 'value': item['value']}
                for item in discounts
            }

        # Computes the sum of the prices of articles in each cart.
        carts_totals = [
            {
                'id': cart['id'],
                'total': _compute_cart_total(cart['items'], articles, discounts),
            }
            for cart in carts
        ]

        # Retrieves the delivery fees, if they were supplied.
        delivery_fees = data.get('delivery_fees', None)

        # Applies the delivery fees, if they were supplied.
        if delivery_fees is not None:
            # Turns the list of delivery fees dictionaries into a list of tuples, for easy manipulation.
            delivery_fees = [
                (
                    fee['eligible_transaction_volume']['min_price'],
                    fee['eligible_transaction_volume']['max_price'],
                    fee['price'],
                )
                for fee in delivery_fees
            ]

            # Applies the delivery fee of each cart.
            carts_totals = [
                {
                    **cart,
                    'total': cart['total']
                    + _get_delivery_fee(cart['total'], delivery_fees),
                }
                for cart in carts_totals
            ]

        return jsonify(carts=carts_totals), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
