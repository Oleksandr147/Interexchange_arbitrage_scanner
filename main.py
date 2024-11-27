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
    print(ref_orderbook_1)


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

# print(calculate_orderbook_depth("STRUMP/USDT", gateio, mexc, 100))
