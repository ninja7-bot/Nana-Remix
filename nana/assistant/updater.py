import random
from git import Repo
from git.exc import GitCommandError, NoSuchPathError, InvalidGitRepositoryError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from nana import (
    setbot,
    Owner,
    USERBOT_VERSION,
    ASSISTANT_VERSION,
    log,
    OFFICIAL_BRANCH,
    REPOSITORY,
    RANDOM_STICKERS,
    REMINDER_UPDATE,
    TEST_DEVELOP,
)
from nana.__main__ import restart_all, loop
from nana.assistant.__main__ import dynamic_data_filter
from nana.tr_engine.strings import tld


async def gen_chlog(repo, diff):
    changelog = ""
    d_form = "%H:%M - %d/%m/%y"
    try:
        for cl in repo.iter_commits(diff):
            changelog += f"• [{cl.committed_datetime.strftime(d_form)}]: {cl.summary} <{cl.author}>\n"
    except GitCommandError:
        changelog = None
    return changelog


async def update_changelog(changelog):
    await setbot.send_sticker(Owner, random.choice(RANDOM_STICKERS))
    text = tld("update_successful")
    text += tld("update_welcome").format(
        USERBOT_VERSION,
        ASSISTANT_VERSION
    )
    text += tld("updated_changelog")
    text += changelog
    await setbot.send_message(Owner, text)


async def update_checker():
    try:
        repo = Repo()
    except NoSuchPathError as error:
        log.warning(f"Check update failed!\nDirectory {error} is not found!")
        return
    except InvalidGitRepositoryError as error:
        log.warning(
            f"Check update failed!\nDirectory {error} does not seems to be a git repository"
        )
        return
    except GitCommandError as error:
        log.warning(f"Check update failed!\n{error}")
        return

    brname = repo.active_branch.name
    if brname not in OFFICIAL_BRANCH:
        return

    try:
        repo.create_remote("upstream", REPOSITORY)
    except BaseException:
        pass

    upstream = repo.remote("upstream")
    upstream.fetch(brname)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{brname}")

    if not changelog:
        log.info(f"Nana is up-to-date with branch {brname}")
        return

    log.warning(f"New UPDATE available for [{brname}]!")

    text = tld("updater_available_text").format(brname)
    text += f"**CHANGELOG:**\n`{changelog}`"
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton(tld("update_now_btn"), callback_data="update_now")]]
    )
    await setbot.send_message(Owner, text, reply_markup=button, parse_mode="markdown")


@setbot.on_callback_query(dynamic_data_filter("update_now"))
async def update_button(client, _):
    await client.send_message(Owner, "Updating, please wait...")
    try:
        repo = Repo()
    except NoSuchPathError as error:
        log.warning(f"Check update failed!\nDirectory {error} is not found!")
        return
    except InvalidGitRepositoryError as error:
        log.warning(
            f"Check update failed!\nDirectory {error} does not seems to be a git repository"
        )
        return
    except GitCommandError as error:
        log.warning(f"Check update failed!\n{error}")
        return

    brname = repo.active_branch.name
    if brname not in OFFICIAL_BRANCH:
        return

    try:
        repo.create_remote("upstream", REPOSITORY)
    except BaseException:
        pass

    upstream = repo.remote("upstream")
    upstream.fetch(brname)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{brname}")
    try:
        upstream.pull(brname)
        await client.send_message(Owner, tld("update_successful"))
    except GitCommandError:
        repo.git.reset("--hard")
        repo.git.clean("-fd", "nana/modules/")
        repo.git.clean("-fd", "nana/assistant/")
        repo.git.clean("-fd", "nana/helpers/")
        await client.send_message(
            Owner, tld("update_successful_force")
        )
    await update_changelog(changelog)
    await restart_all()


if REMINDER_UPDATE and not TEST_DEVELOP:
    loop.create_task(update_checker())
