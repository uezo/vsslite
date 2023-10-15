import os
import pytest
from vsslite.lcclient import LangChainVSSLiteClient as VSSClient

API_KEY = os.environ.get("OPENAI_APIKEY")


@pytest.mark.asyncio
async def test_acurd():
    vss = VSSClient()
    await vss.adelete_all()

    # add
    id1 = await vss.aadd("The difference between eel and conger eel is that eel is more expensive.")
    id2 = await vss.aadd("Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    id3 = await vss.aadd("There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")

    r1 = await vss.aget(id1)
    assert r1["documents"][0]["page_content"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = await vss.aget(id2)
    assert r2["documents"][0]["page_content"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = await vss.aget(id3)
    assert r3["documents"][0]["page_content"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # update
    await vss.aupdate(id1, "up:The difference between eel and conger eel is that eel is more expensive.")
    await vss.aupdate(id2, "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    await vss.aupdate(id3, "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")

    r4 = await vss.aget(id1)
    assert r4["documents"][0]["page_content"] == "up:The difference between eel and conger eel is that eel is more expensive."
    r5 = await vss.aget(id2)
    assert r5["documents"][0]["page_content"] == "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r6 = await vss.aget(id3)
    assert r6["documents"][0]["page_content"] == "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # search
    s1 = await vss.asearch("fish")
    assert s1[0]["page_content"] == r4["documents"][0]["page_content"]
    s2 = await vss.asearch("animal")
    assert s2[0]["page_content"] == r5["documents"][0]["page_content"]
    s3 = await vss.asearch("food")
    assert s3[0]["page_content"] == r6["documents"][0]["page_content"]

    # delete
    await vss.adelete(id1)
    assert await vss.aget(id1) == {"documents": [], "ids": []}
    assert await vss.aget(id2) == r5
    assert await vss.aget(id3) == r6

    # delete_all
    await vss.adelete_all()
    assert await vss.aget(id1) == {"documents": [], "ids": []}
    assert await vss.aget(id2) == {"documents": [], "ids": []}
    assert await vss.aget(id3) == {"documents": [], "ids": []}


@pytest.mark.asyncio
async def test_abulk_json():
    vss = VSSClient()
    await vss.adelete_all()

    # import for add
    ids = (await vss.aimport_file("tests/data/sample.json", content_key="body"))["ids"]

    r1 = await vss.aget(ids[0])
    assert r1["documents"][0]["page_content"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = await vss.aget(ids[1])
    assert r2["documents"][0]["page_content"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = await vss.aget(ids[2])
    assert r3["documents"][0]["page_content"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."


@pytest.mark.asyncio
async def test_abulk_csv():
    vss = VSSClient()
    await vss.adelete_all()

    # import for add
    ids = (await vss.aimport_file("tests/data/sample.csv", content_key="body"))["ids"]

    r1 = await vss.aget(ids[0])
    assert r1["documents"][0]["page_content"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = await vss.aget(ids[1])
    assert r2["documents"][0]["page_content"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = await vss.aget(ids[2])
    assert r3["documents"][0]["page_content"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."


def test_curd():
    vss = VSSClient()
    vss.delete_all()

    # add
    id1 = vss.add("The difference between eel and conger eel is that eel is more expensive.")
    id2 = vss.add("Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    id3 = vss.add("There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")

    r1 = vss.get(id1)
    assert r1["documents"][0]["page_content"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = vss.get(id2)
    assert r2["documents"][0]["page_content"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = vss.get(id3)
    assert r3["documents"][0]["page_content"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # update
    vss.update(id1, "up:The difference between eel and conger eel is that eel is more expensive.")
    vss.update(id2, "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    vss.update(id3, "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")

    r4 = vss.get(id1)
    assert r4["documents"][0]["page_content"] == "up:The difference between eel and conger eel is that eel is more expensive."
    r5 = vss.get(id2)
    assert r5["documents"][0]["page_content"] == "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r6 = vss.get(id3)
    assert r6["documents"][0]["page_content"] == "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # search
    s1 = vss.search("fish")
    assert s1[0]["page_content"] == r4["documents"][0]["page_content"]
    s2 = vss.search("animal")
    assert s2[0]["page_content"] == r5["documents"][0]["page_content"]
    s3 = vss.search("food")
    assert s3[0]["page_content"] == r6["documents"][0]["page_content"]

    # delete
    vss.delete(id1)
    assert vss.get(id1) == {"documents": [], "ids": []}
    assert vss.get(id2) == r5
    assert vss.get(id3) == r6

    # delete_all
    vss.delete_all()
    assert vss.get(id1) == {"documents": [], "ids": []}
    assert vss.get(id2) == {"documents": [], "ids": []}
    assert vss.get(id3) == {"documents": [], "ids": []}


def test_bulk_json():
    vss = VSSClient()
    vss.delete_all()

    # import for add
    ids = vss.import_file("tests/data/sample.json", content_key="body")["ids"]

    r1 = vss.get(ids[0])
    assert r1["documents"][0]["page_content"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = vss.get(ids[1])
    assert r2["documents"][0]["page_content"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = vss.get(ids[2])
    assert r3["documents"][0]["page_content"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."


def test_bulk_csv():
    vss = VSSClient()
    vss.delete_all()

    # import for add
    ids = vss.import_file("tests/data/sample.csv", content_key="body")["ids"]

    r1 = vss.get(ids[0])
    assert r1["documents"][0]["page_content"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = vss.get(ids[1])
    assert r2["documents"][0]["page_content"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = vss.get(ids[2])
    assert r3["documents"][0]["page_content"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."
