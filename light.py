import asyncio
from kasa import Discover

async def main():
    dev = await Discover.discover_single("192.168.137.240", username="2558852597@qq.com", password="Zx_20001102")
    await dev.turn_off()
    await dev.update()

if __name__ == "__main__":
    asyncio.run(main())


# from kasa import Discover
# import asyncio

# def main():
#     dev = asyncio.run(Discover.discover_single("192.168.137.240", username="2558852597@qq.com", password="Zx_20001102"))
#     asyncio.run(dev.turn_off())
#     asyncio.run(dev.update())

# if __name__ == "__main__":
#     main()
