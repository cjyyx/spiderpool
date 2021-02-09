from fake_useragent import UserAgent
def ranheaders():
    '''随机产生含有User-Agent的请求头'''
    headers={
        'User-Agent':UserAgent().chrome
    }
    return headers