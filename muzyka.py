"""Логіка музики для бота: черга, YouTube, Spotify, shuffle, loop.
Команди (/грати, /цикл тощо) знаходяться в main.py.

Spotify не віддає аудіо, тому зі Spotify-посилання беремо лише список
"виконавець - назва", а звук для кожного треку шукаємо на YouTube.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import aiohttp
import discord
import yt_dlp

FFMPEG_OPTIONS = "-vn"
# Треки спочатку завантажує yt-dlp у тимчасову папку, і лише потім ffmpeg грає локальний файл.
# Так YouTube не віддає 403, який виникав, коли ffmpeg сам відкривав потік.
CACHE_DIR = os.path.join(tempfile.gettempdir(), "alphabot_music")
shutil.rmtree(CACHE_DIR, ignore_errors=True)   # прибираємо залишки від минулого запуску
os.makedirs(CACHE_DIR, exist_ok=True)

IDLE_TIMEOUT = 300        # скільки секунд бот сидить у каналі без музики
MAX_TRACKS_PER_ADD = 200  # ліміт треків за один /грати

YTDL_BASE = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "source_address": "0.0.0.0",
}

SPOTIFY_RE = re.compile(
    r"open\.spotify\.com/(?:intl-[a-z]+/)?(track|album|playlist)/([A-Za-z0-9]+)")
LOOP_LABELS = {"off": "вимкнено", "track": "поточний трек :repeat_one:",
               "queue": "вся черга :repeat:"}

players: dict[int, "Player"] = {}   # guild.id -> Player
_session: Optional[aiohttp.ClientSession] = None


class MusicError(Exception):
    """Помилка, текст якої можна показати користувачу."""


# ---------------------------------------------------------------- допоміжне --

def pomylka(text: str) -> discord.Embed:
    return discord.Embed(description=text, color=discord.Color.red())


def fmt_duration(sec) -> str:
    if not sec:
        return "?"
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


def is_playlist_url(url: str) -> bool:
    return urlparse(url).path.rstrip("/") == "/playlist"


def extract_youtube(query: str) -> list:
    """Блокуюча функція: повертає [(назва, url, тривалість)]. Запускати через to_thread."""
    opts = {
        **YTDL_BASE,
        "extract_flat": "in_playlist",
        "noplaylist": not is_playlist_url(query),
        "playlistend": MAX_TRACKS_PER_ADD,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=False)
    entries = info.get("entries")
    if entries is None:
        entries = [info]
    result = []
    for e in entries:
        if not e:
            continue
        url = e.get("webpage_url") or e.get("url")
        if url and not url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={e.get('id', url)}"
        if not url:
            continue
        result.append((e.get("title") or "Без назви", url, e.get("duration")))
    return result


def download_audio(query: str):
    """Блокуюча функція: завантажує аудіо у тимчасовий файл. Повертає (шлях, info)."""
    # унікальне ім'я на кожне завантаження, щоб видалення старого файлу не зачепило новий
    opts = {**YTDL_BASE, "noplaylist": True,
            "outtmpl": os.path.join(CACHE_DIR, f"%(id)s-{uuid.uuid4().hex[:8]}.%(ext)s")}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)
    if "entries" in info:
        entries = [e for e in info["entries"] if e]
        if not entries:
            raise MusicError("Нічого не знайдено")
        info = entries[0]
    downloads = info.get("requested_downloads") or [{}]
    path = downloads[0].get("filepath")
    if not path or not os.path.exists(path):
        raise MusicError("Не вдалося завантажити аудіо")
    return path, info


def remove_file(path):
    try:
        os.remove(path)
    except OSError:
        pass  # на Windows файл може ще бути зайнятий; він видалиться при наступному запуску


async def fetch_spotify(kind: str, sid: str):
    """Читає трек/альбом/плейлист зі Spotify без API-ключів (через embed-сторінку).

    Це неофіційний спосіб: якщо Spotify змінить розмітку, тут перестане працювати.
    """
    url = f"https://open.spotify.com/embed/{kind}/{sid}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
    try:
        async with get_session().get(url, headers=headers,
                                     timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status != 200:
                raise MusicError("Spotify не віддав цю сторінку (можливо, плейлист приватний).")
            html = await r.text()
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
        if not m:
            raise MusicError("Не вдалося прочитати сторінку Spotify.")
        entity = json.loads(m.group(1))["props"]["pageProps"]["state"]["data"]["entity"]
    except (KeyError, TypeError, json.JSONDecodeError, aiohttp.ClientError, asyncio.TimeoutError):
        raise MusicError("Не вдалося прочитати це Spotify-посилання.")

    name = entity.get("name") or entity.get("title") or "Spotify"
    tracks = []
    for t in entity.get("trackList") or []:
        title = (t.get("title") or "").strip()
        artist = (t.get("subtitle") or "").replace("\xa0", " ").strip()
        if title:
            tracks.append(f"{artist} - {title}" if artist else title)
    if not tracks:  # одиночний трек
        artists = ", ".join(a["name"] for a in entity.get("artists", []) if a.get("name"))
        title = entity.get("name") or entity.get("title")
        if title:
            tracks.append(f"{artists} - {title}" if artists else title)
    if not tracks:
        raise MusicError("У цьому Spotify-посиланні не знайшлось треків.")
    return name, tracks[:MAX_TRACKS_PER_ADD]


# -------------------------------------------------------------------- трек ---

@dataclass
class Track:
    title: str
    query: str                      # YouTube-посилання або "ytsearch1:..."
    requester: discord.abc.User
    duration: Optional[int] = None
    web_url: Optional[str] = None

    filepath: Optional[str] = None  # завантажений файл (тимчасовий)

    async def make_source(self) -> discord.AudioSource:
        if not (self.filepath and os.path.exists(self.filepath)):
            self.filepath, info = await asyncio.to_thread(download_audio, self.query)
            self.web_url = info.get("webpage_url") or self.web_url
            self.duration = info.get("duration") or self.duration
        return discord.FFmpegPCMAudio(self.filepath,
                                      executable=os.getenv("FFMPEG_PATH") or "ffmpeg",
                                      options=FFMPEG_OPTIONS)

    def release_file(self, delay: float = 2.0):
        """Видаляє тимчасовий файл (з невеликою затримкою, поки ffmpeg його відпустить)."""
        path, self.filepath = self.filepath, None
        if path:
            asyncio.get_running_loop().call_later(delay, remove_file, path)


async def build_tracks(query: str, user):
    """Перетворює запит користувача на список Track. Повертає (треки, назва)."""
    if "spotify.com" in query:
        m = SPOTIFY_RE.search(query)
        if not m:
            raise MusicError("З Spotify я розумію лише посилання на трек, альбом або плейлист.")
        name, items = await fetch_spotify(*m.groups())
        tracks = [Track(title=i, query=f"ytsearch1:{i} audio", requester=user) for i in items]
        return tracks, name

    q = query if query.startswith(("http://", "https://")) else f"ytsearch1:{query}"
    try:
        entries = await asyncio.to_thread(extract_youtube, q)
    except Exception as e:
        print(f"[muzyka] yt-dlp: {e}")
        raise MusicError("Не вдалося отримати це з YouTube. Перевір посилання або спробуй пізніше.")
    if not entries:
        raise MusicError("Нічого не знайдено.")
    tracks = [Track(title=t, query=u, requester=user, duration=d, web_url=u) for t, u, d in entries]
    name = tracks[0].title if len(tracks) == 1 else "плейлиста"
    return tracks, name


# ------------------------------------------------------------------ плеєр -----

class Player:
    """Стан музики одного сервера: черга, поточний трек, режим loop."""

    def __init__(self, guild: discord.Guild, channel):
        self.guild = guild
        self.channel = channel
        self.queue: list = []
        self.current: Optional[Track] = None
        self.loop = "off"            # off | track | queue
        self.skipped = False
        self._replay = False         # трек повторюється через loop (не спамимо "Зараз грає")
        self.wakeup = asyncio.Event()
        self.finished = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        self.task = asyncio.create_task(self.run())

    def _after(self, error):
        if error:
            print(f"[muzyka] помилка відтворення: {error}")
        self._loop.call_soon_threadsafe(self.finished.set)

    async def say(self, **kwargs):
        try:
            await self.channel.send(**kwargs)
        except discord.HTTPException:
            pass

    def now_playing_embed(self) -> discord.Embed:
        t = self.current
        title = f"[{t.title}]({t.web_url})" if t.web_url else t.title
        embed = discord.Embed(title=":musical_note: Зараз грає :musical_note:",
                              description=title, color=discord.Color.blurple())
        embed.add_field(name="Тривалість", value=fmt_duration(t.duration))
        embed.add_field(name="Додав", value=t.requester.display_name)
        embed.set_footer(text=f"Цикл: {LOOP_LABELS[self.loop]} • у черзі: {len(self.queue)}")
        return embed

    async def run(self):
        while True:
            if not self.queue:
                self.current = None
                self.wakeup.clear()
                try:
                    await asyncio.wait_for(self.wakeup.wait(), IDLE_TIMEOUT)
                except asyncio.TimeoutError:
                    await self.say(embed=discord.Embed(
                        description="Нічого грати, виходжу з каналу :wave:",
                        color=discord.Color.blurple()))
                    await self.shutdown()
                    return
                continue

            track = self.queue.pop(0)
            self.current = track
            replay, self._replay = self._replay, False

            try:
                source = await track.make_source()
            except Exception as e:  # yt-dlp кидає різні помилки
                print(f"[muzyka] не вдалося завантажити {track.query}: {e}")
                await self.say(embed=pomylka(
                    f"Не вдалося завантажити **{track.title}**, пропускаю."))
                continue

            if self.skipped:         # /далі або /стоп спрацювали, поки трек завантажувався
                self.skipped = False
                track.release_file(0)
                continue

            vc = self.guild.voice_client
            if vc is None or not vc.is_connected():
                await self.shutdown()
                return

            self.finished.clear()
            vc.play(source, after=self._after)
            if not replay:
                await self.say(embed=self.now_playing_embed())
            await self.finished.wait()

            skipped, self.skipped = self.skipped, False
            if self.loop == "track" and not skipped:
                self.queue.insert(0, track)   # файл лишається, повтор почнеться без завантаження
                self._replay = True
            else:
                track.release_file()
                if self.loop == "queue":
                    self.queue.append(track)

    async def shutdown(self):
        players.pop(self.guild.id, None)
        self.queue.clear()
        if self.task is not asyncio.current_task():
            self.task.cancel()
        vc = self.guild.voice_client
        if vc:
            await vc.disconnect(force=True)


# ----------------------------------------------- перевірки для команд --------

async def perevirka(Interaction: discord.Interaction) -> Optional[Player]:
    """Для команд керування: плеєр існує і користувач в одному каналі з ботом."""
    player = players.get(Interaction.guild_id)
    vc = Interaction.guild.voice_client
    if not player or not vc:
        await Interaction.response.send_message(
            embed=pomylka("Зараз нічого не грає."), ephemeral=True)
        return None
    if getattr(Interaction.user.voice, "channel", None) != vc.channel:
        await Interaction.response.send_message(
            embed=pomylka("Зайди в один голосовий канал з ботом."), ephemeral=True)
        return None
    return player


async def voice_update(bot_user, member, before, after):
    """Викликається з on_voice_state_update у main.py."""
    guild = member.guild
    if member.id == bot_user.id:
        if after.channel is None:  # бота кікнули/відключили
            player = players.pop(guild.id, None)
            if player:
                player.queue.clear()
                player.task.cancel()
        return
    vc = guild.voice_client
    if vc and vc.channel and before.channel == vc.channel:
        if all(m.bot for m in vc.channel.members):  # усі пішли
            player = players.get(guild.id)
            if player:
                await player.shutdown()