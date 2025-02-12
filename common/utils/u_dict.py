def dict_filtered(data, unwanted_keys):
    """字典过滤"""
    filtered_dict = {}
    for key, value in data.items():
        if key not in unwanted_keys:
            filtered_dict[key] = value
    return filtered_dict


def dict_partitioned(data, unwanted_keys):
    """字典拆分"""
    filtered_dict = {}
    unwanted_dict = {}
    for key, value in data.items():
        if key in unwanted_keys:
            unwanted_dict[key] = value
        else:
            filtered_dict[key] = value
    return filtered_dict, unwanted_dict
