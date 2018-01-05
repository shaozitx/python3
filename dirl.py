import os

"""
str     -- 要查找的字符串
path    -- 待查询路径
prefix  -- （当前相对路径）,用于打印相对路径
"""
def findStr(str, path, prefix=''):
    fileList = os.listdir(path)
    for file in fileList:
        temp_path = os.path.join(prefix, file)
        if os.path.isdir(file):
            findStr(str, file, temp_path)
        elif str in file:
            print(temp_path)


findStr('py', '.')
