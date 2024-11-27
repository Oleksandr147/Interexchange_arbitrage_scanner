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
