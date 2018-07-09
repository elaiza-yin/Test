from qiniu import Auth, put_data

# 公钥
access_key = "yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW"
# 密钥
secret_key = "bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW"
# 你自己创建的空间
bucket_name = "ihome"


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        # ret是个字典:里面有上传到千牛云的图片key值,和千牛云上的前缀外链默认域名拼接就可以获取图片
        # info 中的有个status_code:200 表示图片上传成功
        print("图片的key值 : %s " % ret["key"])
        print("200表示为上传成功 : %s" % info.status_code)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception("上传图片失败")
    # 返回后和外链的默认域名前缀 + key 形成图片
    return ret["key"]


if __name__ == '__main__':
    file = input('请输入文件路径:')
    with open(file, 'rb') as f:
        storage(f.read())