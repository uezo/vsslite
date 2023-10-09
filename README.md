# VSSLite

A vector similarity search engine on SQLite.

# ✨ Features

VSSLite provides a simple wrapper features for sqlite-vss.

## 🔍 Search

```python
from vsslite import VSSLite

# Initialize
vss = VSSLite(YOUR_API_KEY)

# Add data with embeddings
vss.add("The difference between eel and conger eel is that eel is more expensive.")
vss.add("Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
vss.add("There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")

# Search
print(vss.search("fish"))
print(vss.search("animal"))
print(vss.search("food"))
```

Now you can get these search results.

```bash
$ python run.py
[{'id': 1, 'updated_at': '2023-10-09 16:05:50.171643', 'namespace': 'default', 'body': 'The difference between eel and conger eel is that eel is more expensive.', 'data': {}, 'distance': 0.41116979718208313}]
[{'id': 2, 'updated_at': '2023-10-09 16:05:50.694124', 'namespace': 'default', 'body': 'Red pandas are smaller than pandas, but when it comes to cuteness, there is no "lesser" about them.', 'data': {}, 'distance': 0.4909055233001709}]
[{'id': 3, 'updated_at': '2023-10-09 16:05:50.942491', 'namespace': 'default', 'body': 'There is no difference between "Ohagi" and "Botamochi" themselves; they are used interchangeably depending on the season.', 'data': {}, 'distance': 0.474251925945282}]
```

## 🔧 Data management (Add, Get, Update, Delete)

Helps CRUD.

```python
# Add
vss.add("The difference between eel and conger eel is that eel is more expensive.")
# Get
vss.get(1)
# Update
vss.update(1, "The difference between eel and conger eel is that eel is more expensive. Una-jiro is cheaper than both of them.")
# Delete
vss.delete(1)
# Delete all
vss.delete_all()
```

## 🧩 REST APIs

```python
import uvicorn
from server import VSSLiteServer

app = VSSLiteServer(YOUR_API_KEY).app
uvicorn.run(app, host="127.0.0.1", port=8000)
```

Go http://127.0.0.1:8000/docs to know the details and try it out.


# 🙏 Pre-Requirements

Python environment that allows you to use SQLite extentions is required. Use the build option below when you install Python:

```bash
$ export PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions"
```

# 📦 Install VSSLite

👍

```bash
$ pip install vsslite
```

# 🥰 Special thanks

- sqlite-vss: https://github.com/asg017/sqlite-vss
- https://note.com/mahlab/n/n5d59b19be573
- https://qiita.com/Hidetoshi_Kawaguchi/items/f84f7a43d5d1c15a5a17
- https://zenn.dev/koron/articles/8925963f432361
