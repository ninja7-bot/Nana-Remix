import os
from glob import glob
from mega import Mega
from pyrogram import filters

from nana import app, Command, AdminSettings, edrep

__MODULE__ = "Mega"
__HELP__ = """
Download any file from URL or from telegram
──「 **Download mega file from URL** 」──
-> `mega (url)`
Give url as args to download it.
(this is a sync module. you cannot use your userbot while mega is downloading a file)
──「 **List Downloaded** 」──
-> `megafile`
List of file that have downloaded with mega.
"""


async def megadl(url):
    mega = Mega()
    mega.download_url(url, "nana/downloads/mega")


@app.on_message(filters.user(AdminSettings) & filters.command(["mega"], Command))
async def mega_download(_, message):
    args = message.text.split(None, 1)
    if len(args) == 1:
        await edrep(message, text="usage: mega (url)")
        return
    await edrep(message, text="__Processing...__")
    if not os.path.exists("nana/downloads/mega"):
        os.makedirs("nana/downloads/mega")
    await megadl(args[1])
    files_list = glob('nana/downloads/mega/*')
    for doc in files_list:
        await message.reply_document(doc)
        os.remove(doc)
    await message.delete()


@app.on_message(filters.me & filters.command(["megafile"], Command))
async def mega_downloaded_file(_, message):
    filelist = os.listdir("nana/downloads/mega")
    print(len(filelist))
    if len(filelist) == 0:
        await edrep(
            message,
            text="You haven't download any files with mega! try to download something",
        )
        return
    listoffile = "List of file downloaded with mega: \n`"
    for i in range(len(filelist)):
        listoffile += filelist[i] + "\n"
    listoffile += "`"
    await edrep(message, text=listoffile)
