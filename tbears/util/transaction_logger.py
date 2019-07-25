from iconcommons.logger.logger import Logger

from tbears.config.tbears_config import TBEARS_CLI_TAG


def send_transaction_with_logger(icon_service, signed_transaction, uri):
    tx_dict = make_dict_to_rpc_dict(signed_transaction.signed_transaction_dict, 'icx_transaction')
    Logger.info(f"Send request to {uri}. Request body: {tx_dict}", TBEARS_CLI_TAG)

    return icon_service.send_transaction(signed_transaction, True)


def call_with_logger(icon_service, call_obj, uri):
    call_dict = make_call_dict_to_rpc_dict(call_obj)
    Logger.info(f"Send request to {uri}. Request body: {call_dict}", TBEARS_CLI_TAG)

    return icon_service.call(call_obj, True)


def make_dict_to_rpc_dict(obj: dict, method):
    rpc_dict = {
        'jsonrpc': '2.0',
        'method': method,
        'id': 1234
    }

    if obj:
        rpc_dict['params'] = obj

    return rpc_dict


def make_call_dict_to_rpc_dict(call):
    params = {
        "to": call.to,
        "dataType": "call",
        "data": {
            "method": call.method
        }
    }

    if call.from_ is not None:
        params["from"] = call.from_

    if isinstance(call.params, dict):
        params["data"]["params"] = call.params

    return make_dict_to_rpc_dict(params, 'icx_call')
