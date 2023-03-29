def cancel_all_pending_orders(kite):
        '''
        cancels all the pending orders
        '''
        orders = kite.orders()
        for order in orders:
            if (order['status'] == 'TRIGGER PENDING') or (order['status'] == 'OPEN') | (order['status'] == 'AMO REQ RECEIVED'):
                print(order['tradingsymbol'])
                cancel_id = kite.cancel_order(variety=order['variety'],
                                                   order_id=order['order_id'],
                                                   parent_order_id=order['parent_order_id'])


def close_all_open_positions(kite):
    '''
    closes all the open positions whenever called
    '''
    positions = kite.positions()['net']
    for x in range(len(positions)):
        if abs(positions[x]['quantity']) > 0:
            tradingsymbol = positions[x]['tradingsymbol']
            quantity = positions[x]['quantity']
            if quantity > 0:
                exit_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                            tradingsymbol=tradingsymbol,
                                            exchange=kite.EXCHANGE_NFO,
                                            transaction_type=kite.TRANSACTION_TYPE_SELL,
                                            quantity=quantity,
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            product=kite.PRODUCT_NRML)
            elif quantity < 0:
                exit_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                            tradingsymbol=tradingsymbol,
                                            exchange=kite.EXCHANGE_NFO,
                                            transaction_type=kite.TRANSACTION_TYPE_BUY,
                                            quantity=abs(quantity),
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            product=kite.PRODUCT_NRML)
            else:
                pass


def kill_orders(kite):
    '''
    closes all the open positions whenever called
    '''
    for object in kite:
        positions = object.positions()['net']
        for x in range(len(positions)):
            if abs(positions[x]['quantity']) > 0:
                tradingsymbol = positions[x]['tradingsymbol']
                quantity = positions[x]['quantity']
                if quantity > 0:
                    exit_id = object.place_order(variety=object.VARIETY_REGULAR,
                                                tradingsymbol=tradingsymbol,
                                                exchange=object.EXCHANGE_NFO,
                                                transaction_type=object.TRANSACTION_TYPE_SELL,
                                                quantity=quantity,
                                                order_type=object.ORDER_TYPE_MARKET,
                                                product=object.PRODUCT_NRML)
                elif quantity < 0:
                    exit_id = object.place_order(variety=object.VARIETY_REGULAR,
                                                tradingsymbol=tradingsymbol,
                                                exchange=object.EXCHANGE_NFO,
                                                transaction_type=object.TRANSACTION_TYPE_BUY,
                                                quantity=abs(quantity),
                                                order_type=object.ORDER_TYPE_MARKET,
                                                product=object.PRODUCT_NRML)
                else:
                    pass
        '''
        cancels all the pending orders
        '''
        orders = object.orders()
        for order in orders:
            if (order['status'] == 'TRIGGER PENDING') or (order['status'] == 'OPEN') | (order['status'] == 'AMO REQ RECEIVED'):
                print(order['tradingsymbol'])
                cancel_id = object.cancel_order(variety=order['variety'],
                                                    order_id=order['order_id'],
                                                    parent_order_id=order['parent_order_id'])
    