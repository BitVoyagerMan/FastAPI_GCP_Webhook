from fastapi import APIRouter
from moralis import evm_api
from api.core.config import settings
api_key = settings.APP_MORALIS_KEY

router = APIRouter()
native_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
stable_coin_list = [
    '0xdac17f958d2ee523a2206206994597c13d831ec7',
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    '0x6b175474e89094c44da98b954eedeac495271d0f',
    '0x0000000000085d4780B73119b644AE5ecd22b376',
    '0x8e870d67f660d95d5be530380d0ec0bd388289e1',
    '0x0c10bf8fcb7bf5412187a595ab97a3609160b5c6',
    '0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd',
    '0xa47c8bf37f92aBed4A126BDA807A7b7498661acD',
    '0x853d955acef822db058eb8505911ed77f175b99e',
    '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0'
]

def getPriceByTokenAddress(address, balance, decimals):
    
    params = {
        "address": address,
        "include": "percent_change",
        "chain" : "eth"
    }
    try:
        result = evm_api.token.get_token_price(
            api_key=api_key,
            params=params,
        )
        return float(result["usdPrice"]) * int(balance) / (10**int(decimals))
    except:
        return -1

def getEthPrice(address):
    params = {
        "address": address,
        "chain": "eth"
    }
    result = evm_api.token.get_token_price(
            api_key=api_key,
            params=params,
    )
    return result["usdPrice"]
def getEthBalance(wallet_address):
    params = {
        "address": wallet_address,
        "chain": "eth",
    }
    result = evm_api.balance.get_native_balance(api_key = api_key, params = params)
    return result["balance"]
@router.get("/getMainInfo/{wallet_address}")
def get_Main_Info(wallet_address): 
    params = {
        "address": wallet_address,
        "chain": "eth",
    }
    
    result = evm_api.token.get_wallet_token_balances(
        api_key=api_key,
        params=params,
    )
    general_erc_token_list, stable_erc_token_list = [], []
    general_total_amount, stable_total_amount = 0.0, 0.0
    for item in result:
        if item['token_address'] in stable_coin_list:
            thisPrice = getPriceByTokenAddress(item["token_address"], item["balance"], item["decimals"])
            if thisPrice != -1:
                print(item["symbol"], thisPrice)
                stable_total_amount += thisPrice
                stable_erc_token_list.append({item["symbol"]: thisPrice})

        else:
            thisPrice = getPriceByTokenAddress(item["token_address"], item["balance"], item["decimals"])
            if thisPrice != -1:
                general_total_amount += thisPrice
                print(item["symbol"], thisPrice)
                general_erc_token_list.append({item["symbol"]: thisPrice})
    native_total_amount = int(getEthBalance(wallet_address)) * float(getEthPrice(native_address)) / (10**18)
    return {
        "total" : native_total_amount + stable_total_amount + general_total_amount,
        "eth" : {"total": native_total_amount},
        "stableCoin" : {"total" : stable_total_amount, "lists" : stable_erc_token_list}, 
            "erc20" : {"total" : general_total_amount, "lists": general_erc_token_list}
            }