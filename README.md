# PyGo


## pymongo
### 一、先写个配置文件config.py
```
MONGO_URI = 'localhost'     #本地
MONGO_DB = 'dbname'
MONGO_TABLE = 'tbname'
```

### 二、连接并操作数据库
```python
import pymongo
from config import *     #导入配置文件

client = pymongo.MongoClient(MONGO_URI)     #创建连接
db = client[MONGO_DB]     #选择目标数据库
 

db[MONGO_TABLE].insert({"key1":"value1","key2","value2"})      #写入
db[MONGO_TABLE].remove()    #删除记录
db[MONGO_TABLE].remove({"key1":"value1"})     #选择删除
db[MONGO_TABLE].updata({"key1": "value1"}, {"$set": {"key2": "value2", "key3": "value3"}})     #更新记录
```