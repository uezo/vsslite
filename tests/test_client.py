import os
import pytest
from vsslite import VSSLiteClient

API_KEY = os.environ.get("OPENAI_APIKEY")

@pytest.mark.asyncio
async def test_acurd():
    vss = VSSLiteClient()
    await vss.adelete_all()

    # add
    id1 = await vss.aadd("The difference between eel and conger eel is that eel is more expensive.")
    assert id1 == 1
    id2 = await vss.aadd("Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    assert id2 == 2
    id3 = await vss.aadd("There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")
    assert id3 == 3

    r1 = await vss.aget(id1)
    assert r1["body"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = await vss.aget(id2)
    assert r2["body"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = await vss.aget(id3)
    assert r3["body"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # update
    id4 = await vss.aupdate(id1, "up:The difference between eel and conger eel is that eel is more expensive.")
    assert id4 == 4
    id5 = await vss.aupdate(id2, "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    assert id5 == 5
    id6 = await vss.aupdate(id3, "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")
    assert id6 == 6

    r4 = await vss.aget(id4)
    assert r4["body"] == "up:The difference between eel and conger eel is that eel is more expensive."
    r5 = await vss.aget(id5)
    assert r5["body"] == "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r6 = await vss.aget(id6)
    assert r6["body"] == "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # search
    s1 = await vss.asearch("fish")
    assert s1[0]["body"] == r4["body"]
    s2 = await vss.asearch("animal")
    assert s2[0]["body"] == r5["body"]
    s3 = await vss.asearch("food")
    assert s3[0]["body"] == r6["body"]

    # delete
    await vss.adelete(id4)
    assert await vss.aget(id4) is None
    assert await vss.aget(id5) == r5
    assert await vss.aget(id6) == r6

    # delete_all
    await vss.adelete_all()
    assert await vss.aget(id4) is None
    assert await vss.aget(id5) is None
    assert await vss.aget(id6) is None


def test_curd():
    vss = VSSLiteClient()
    vss.delete_all()

    # add
    id1 = vss.add("The difference between eel and conger eel is that eel is more expensive.")
    assert id1 == 1
    id2 = vss.add("Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    assert id2 == 2
    id3 = vss.add("There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")
    assert id3 == 3

    r1 = vss.get(id1)
    assert r1["body"] == "The difference between eel and conger eel is that eel is more expensive."
    r2 = vss.get(id2)
    assert r2["body"] == "Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r3 = vss.get(id3)
    assert r3["body"] == "There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # update
    id4 = vss.update(id1, "up:The difference between eel and conger eel is that eel is more expensive.")
    assert id4 == 4
    id5 = vss.update(id2, "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them.")
    assert id5 == 5
    id6 = vss.update(id3, "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season.")
    assert id6 == 6

    r4 = vss.get(id4)
    assert r4["body"] == "up:The difference between eel and conger eel is that eel is more expensive."
    r5 = vss.get(id5)
    assert r5["body"] == "up:Red pandas are smaller than pandas, but when it comes to cuteness, there is no \"lesser\" about them."
    r6 = vss.get(id6)
    assert r6["body"] == "up:There is no difference between \"Ohagi\" and \"Botamochi\" themselves; they are used interchangeably depending on the season."

    # search
    s1 = vss.search("fish")
    assert s1[0]["body"] == r4["body"]
    s2 = vss.search("animal")
    assert s2[0]["body"] == r5["body"]
    s3 = vss.search("food")
    assert s3[0]["body"] == r6["body"]

    # delete
    vss.delete(id4)
    assert vss.get(id4) is None
    assert vss.get(id5) == r5
    assert vss.get(id6) == r6

    # delete_all
    vss.delete_all()
    assert vss.get(id4) is None
    assert vss.get(id5) is None
    assert vss.get(id6) is None
