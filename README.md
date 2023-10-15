# VSSLite

A vector similarity search engine for humans🥳


# 🎁 Install

```sh
$ pip install vsslite
```


# ✨ Features

VSSLite provides a user-friendly interface for langchain and sqlite-vss.


## 🧩 Start API server

```sh
$ export OPENAI_APIKEY="YOUR_API_KEY"
$ python -m vsslite
```

Or

```python
import uvicorn
from server import LangChainVSSLiteServer

app = LangChainVSSLiteServer(YOUR_API_KEY).app
uvicorn.run(app, host="127.0.0.1", port=8000)
```

Go http://127.0.0.1:8000/docs to know the details and try it out.


## 🔍 Search

```python
from vsslite import LangChainVSSLiteClient

# Initialize
vss = LangChainVSSLiteClient()

# Add data with embeddings
vss.add("The difference between eel and conger eel is that eel is more expensive.")
vss.add("Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
vss.add("There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")

# Search
print(vss.search("fish", count=1))
print(vss.search("animal", count=1))
print(vss.search("food", count=1))
```

Now you can get these search results.

```bash
$ python run.py

[{'page_content': 'The difference between eel and conger eel is that eel is more expensive.', 'metadata': {'source': 'inline'}}]
[{'page_content': 'Red pandas are smaller than pandas, but when it comes to cuteness, there is no "lesser" about them.', 'metadata': {'source': 'inline'}}]
[{'page_content': 'There is no difference between "Ohagi" and "Botamochi" themselves; they are used interchangeably depending on the season.', 'metadata': {'source': 'inline'}}]
```

## 🔧 Data management (Add, Get, Update, Delete)

Helps CRUD.

```python
# Add
id = vss.add("The difference between eel and conger eel is that eel is more expensive.")[0]
# Get
vss.get(id)
# Update
vss.update(id, "The difference between eel and conger eel is that eel is more expensive. Una-jiro is cheaper than both of them.")
# Delete
vss.delete(id)
# Delete all
vss.delete_all()
```

Upload data. Accept Text, PDF, CSV and JSON for now.

```python
vss.upload("path/to/data.json")
```


## 🍻 Asynchronous

Use async methods when you use VSSLite in server apps.

```python
await vss.aadd("~~~")
await vss.aupdate(id, "~~~")
await vss.aget(id)
await vss.adelete(id)
await vss.aupdate_all()
await vss.asearch("~~~")
await vss.aupload("~~~")
```


## 🧇 Namespace

VSSLite supports namespaces for dividing the set of documents to search or update.

```python
vss = LangChainVSSLiteClient()

# Search product documents
vss.search("What is the difference between super size and ultra size?", namespace="product")
# Search company documents
vss.search("Who is the CTO of Unagiken?", namespace="company")
```


# 🍪 Classic version (based on SQLite)

See [v0.3.0 README](https://github.com/uezo/vsslite/blob/6cee7e0421b893ed9e16fba0508e025270e2550a/README.md)


# 🥰 Special thanks

- sqlite-vss: https://github.com/asg017/sqlite-vss
- https://note.com/mahlab/n/n5d59b19be573
- https://qiita.com/Hidetoshi_Kawaguchi/items/f84f7a43d5d1c15a5a17
- https://zenn.dev/koron/articles/8925963f432361

