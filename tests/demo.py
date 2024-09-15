import asyncio
import minutia

async def main():
    await minutia.init()

    minutia.set_max_filesize(9999999999)
    await minutia.setup_explicit_unix_socket("/tmp/test.pipe")

    print(await minutia.http.get("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/320px-Image_created_with_a_mobile_phone.png"))

    print(await minutia.http.get("https://static2.bigstockphoto.com/5/9/1/large2/195897274.jpg"))


asyncio.run(main())
