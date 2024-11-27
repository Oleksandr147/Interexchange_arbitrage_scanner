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


