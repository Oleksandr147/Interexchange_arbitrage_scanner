import ccxt
import time

#initialize exchanges
mexc = ccxt.mexc()
gateio = ccxt.gateio()



#normalize all symbols
def normalize_symbols(symbol: str) -> str:
    """

    :param symbol: the trading pair symbol
    :return: the normalized symbol in the format of "BTC/USDT"
    """

    if symbol[-4:] in ["USDT", "USDC"] and "_" not in symbol\
        and "-" not in symbol and "/" not in symbol:
        new_symbol = symbol[:-4] + "/" + symbol[-4:]
        return new_symbol
    else:
        return symbol.replace("-", "/").replace("_", "/")



#find common symbols
def find_common_symbols(tickers_1: dict, tickers_2: dict) -> set:
    """
    :param tickers_1: the ticker data of exchange 1
    :param tickers_2:
    :return: a set of common symbols between the two exchanges
    """
    symbols_1 = set(map(normalize_symbols, tickers_1.keys()))
    symbols_2 = set(map(normalize_symbols, tickers_2.keys()))
    common_symbols = symbols_1 & symbols_2
    return common_symbols



#calculate orderbook depth to get the acquired coin data
def calculate_orderbook_depth(symbol: str, exchange_1, exchange_2, amt_in: float) -> float:
    """
    :param symbol: the trading pair for the coins to be calculated
    :param exchange_1: the exchange from which we buy
    :param exchange_2: the exchange where we swap the acquired coin
    :param amt_in: starting amount (USDT)
    :return: the acqiured number of USDT after we swap the coin on exchange 2
    """

    orderbook_1 = exchange_1.fetch_order_book(symbol)
    ref_orderbook_1 = reformat_orderbook(orderbook_1, "quote_to_base")

    orderbook_2 = exchange_2.fetch_order_book(symbol)
    ref_orderbook_2 = reformat_orderbook(orderbook_2, "base_to_quote")

    acquired_coin_1 = calculate_acquired_coin(ref_orderbook_1, amt_in)

    acquired_coin_2 = calculate_acquired_coin(ref_orderbook_2, acquired_coin_1)

    return acquired_coin_2



#reformat orderbook data
def reformat_orderbook(orderbook: dict, trade_direction: str) -> list:
    """

    :param orderbook: the exchange orderbook data
    :param trade_direction: direction in which we swap the
    :return:
    """

    data_list = []
    if trade_direction == "quote_to_base":
        for item in orderbook["asks"]:
            ask_price = float(item[0])
            adj_price = 1 / ask_price if ask_price != 0 else 0
            adj_quantity = float(item[1]) * ask_price
            data_list.append([adj_price, adj_quantity])
    if trade_direction == "base_to_quote":
        for item in orderbook["bids"]:
            bid_price = float(item[0])
            adj_price = bid_price if bid_price != 0 else 0
            adj_quantity = float(item[1])
            data_list.append([adj_price, adj_quantity])
    return data_list



#how the amount of the coin we can get from the orderbook
def calculate_acquired_coin(orderbook: list, amt_in: float) -> float:
    """

    :param orderbook: the reformated orderbook data
    :param amt_in: the starting amount
    :return: the acquired coin we get through buying the quantity of the desired
    coin from the orderbook
    """
    trading_balance = amt_in
    acquired_coin = 0
    quantity_bought = 0
    amount_bought = 0
    calculated = 0

    for level in orderbook:
        level_price = level[0]
        level_quantity = level[1]

        if trading_balance <= level_quantity:
            quantity_bought = trading_balance
            trading_balance = 0
            amount_bought = quantity_bought * level_price

        if trading_balance > level_quantity:
            quantity_bought = level_quantity
            trading_balance -= quantity_bought
            amount_bought = quantity_bought * level_price

        acquired_coin += amount_bought

        if trading_balance == 0:
            return acquired_coin

        calculated += 1
        if calculated == len(orderbook):
            return 0



#find the arbitrage opportunities
def calculate_arbitrage(symbol: str, exchange_1, exchange_2, ticker_1: dict,
                        ticker_2: dict, amt_in) -> dict:
    """

    :param symbol: the trading pair symbol
    :param ticker_1: ticker data from exchange 1
    :param ticker_2: ticker data from exchange 2
    :return: the dict with the arbirtage opportunities description
    """

    starting_amount = amt_in
    symbol_split = symbol.split("/")
    base = symbol_split[0]
    quote = symbol_split[1]
    ask_1 = float(ticker_1["ask"])
    bid_1 = float(ticker_1["bid"])
    ask_2 = float(ticker_2["ask"])
    bid_2 = float(ticker_2["bid"])
    acquired_coin = 0
    exchange_to_buy = ""
    exchange_to_sell = ""
    buy_price = 0
    sell_price = 0
    surface_dict = {}

    if ask_1 < bid_2:
        exchange_to_buy = exchange_1
        exchange_to_sell = exchange_2
        buy_price = ask_1
        sell_price = bid_2
        acquired_coin = calculate_orderbook_depth(symbol, exchange_to_buy, exchange_to_sell, starting_amount)

    if ask_2 < bid_1:
        exchange_to_buy = exchange_2
        exchange_to_sell = exchange_1
        buy_price = ask_2
        sell_price = bid_1
        acquired_coin = calculate_orderbook_depth(symbol, exchange_to_buy, exchange_to_sell, starting_amount)

    #calculate the profit
    profit = acquired_coin - starting_amount
    trade_description = f"{symbol}:Buy {base} on {exchange_to_buy}" \
                        f" at {buy_price} selling on {exchange_to_sell} at {sell_price}. the profit is {profit} " \
                        f"{quote}. " \
                        f"Please mind the network fee and exchange commission."
    if 0 < profit < 5:
        surface_dict = {
            "buy from": exchange_to_buy.id,
            "sell at": exchange_to_sell.id,
            "starting_amount": starting_amount,
            "acquired_coin": acquired_coin,
            "profit": f"{profit} USDT",
            "trade_description": trade_description
        }
        return surface_dict
    return surface_dict



#write the arbitrage bot that applies the above functions to the real exchange data
def arbitrage_bot(exchange_1, exchange_2, amt_in: float):
    """

    :param exchange_1: centralized exchange 1
    :param exchange_2: centralized exchange 2
    :param amt_in: starting amount of USDT
    :return: the string that describes the arbitrage opportunity
    """
    tickers_1 = exchange_1.fetch_tickers()
    tickers_2 = exchange_2.fetch_tickers()

    try:
        common_symbols = find_common_symbols(tickers_1, tickers_2)

        for symbol in common_symbols:
            ticker_1 = tickers_1.get(symbol)
            ticker_2 = tickers_2.get(symbol)

            arb_opportunities = calculate_arbitrage(symbol, exchange_1, exchange_2, ticker_1,
                                                    ticker_2, amt_in)
            if len(arb_opportunities) > 0:
                print(arb_opportunities)
                time.sleep(10)

    except Exception as e:
        print(f"failed to calcukate arbitrage: {e}")



if __name__ == "__main__":
    while True:
        arbitrage_bot(mexc, gateio, 300)