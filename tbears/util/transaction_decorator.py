from iconcommons.logger.logger import Logger
from tbears.config.tbears_config import TBEARS_CLI_TAG


def tx_logger_deco(func, uri, tx_dict):
    return logger_deco(func, uri, tx_dict, 'icx_sendTransaction', make_tx_dict_to_rpc_dict)


def call_logger_deco(func, uri, call_obj):
    return logger_deco(func, uri, call_obj, 'icx_call', make_call_dict_to_rpc_dict)


def logger_deco(func, uri, param: dict, rpc_method, to_rpc_dict_func):

    req = to_rpc_dict_func(param, rpc_method)

    def log_decorator(*args, **kwargs):
        Logger.info(f"Send request to {uri}. Request body: {req}", TBEARS_CLI_TAG)
        result = func(*args, **kwargs)
        return result

    return log_decorator


def make_tx_dict_to_rpc_dict(obj: dict, method):
    rpc_dict = {
        'jsonrpc': '2.0',
        'method': method,
        'id': 1234
    }

    if obj:
        rpc_dict['params'] = obj

    return rpc_dict


def make_call_dict_to_rpc_dict(call, method):
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

    return make_tx_dict_to_rpc_dict(params, method)
