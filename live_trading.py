from pybit.unified_trading import HTTP
import dotenv
import os

import logging
logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")


dotenv.load_dotenv()

print("Loading environment variables...")
print("BYBIT_API_KEY: ", os.getenv("BYBIT_API_KEY"))
print("BYBIT_API_SECRET: ", os.getenv("BYBIT_API_SECRET"))

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = True  # True means your API keys were generated on testnet.bybit.com


# Create direct HTTP session instance

session = HTTP(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    testnet=TESTNET,
)

# Get the orderbook of the USDT Perpetual, BTCUSDT
print(session.get_orderbook(category="linear", symbol="BTCUSDT"))
# Note how the "category" parameter determines the type of market to fetch this
# data for. Look at the docstring of the get_orderbook to navigate to the API
# documentation to see the supported categories for this and other endpoints.

# Get wallet balance of the Unified Trading Account
print(session.get_wallet_balance(accountType="UNIFIED"))

# # Place an order on that USDT Perpetual
# print(session.place_order(
#     category="linear",
#     symbol="BTCUSDT",
#     side="Buy",
#     orderType="Market",
#     qty="0.001",
# ))

# # Place an order on the Inverse Contract, ETHUSD
# print(session.place_order(
#     category="inverse",
#     symbol="ETHUSD",
#     side="Buy",
#     orderType="Market",
#     qty="1",
# ))

# # Place an order on the Spot market, MNTUSDT
# print(session.place_order(
#     category="spot",
#     symbol="MNTUSDT",
#     side="Buy",
#     orderType="Market",
#     qty="10",
# ))