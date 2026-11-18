# Всяка хуйня, імпорти
import datetime
from virshi import virsh
import random
from anekdot import anekdoty
from discord import app_commands
from discord.ext import commands
from random import choice
import discord
from rozkladka import change_rozkladka
import muzyka
import asyncio

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)


# Запуск бота


@client.event
async def on_ready():
    print(f'Ви залогінились, як {client.user}')
    await client.tree.sync()


# команди пішли
@client.tree.command(name='пінг', description='Відповідає "понг!"')
async def пінг(Interaction: discord.Interaction):
    await Interaction.response.send_message(
        content=f'{Interaction.user.mention} Понг!')


@client.tree.command(name='анекдот',
                     description='Розповідає вам випадковий анекдот!')
@discord.app_commands.checks.cooldown(1,
                                      10,
                                      key=lambda i: (i.guild_id, i.user.id))
async def анекдот(Interaction: discord.Interaction):
    embed = discord.Embed(title=':rofl: Анекдот :rofl:',
                          description='',
                          color=discord.Color.yellow())
    anekdot = random.choice(anekdoty)
    embed.add_field(name=" ", value=anekdot)
    print(anekdot)
    await Interaction.response.send_message(embed=embed)


@client.tree.command(name='хелп', description='Навігація по командам.')
async def хелп(Interaction: discord.Interaction):
    embed = discord.Embed(
        title="Меню навігації по командам",
        description="Тут ви можете знайти потрібні вам команди",
        colour=discord.Colour.dark_purple())
    embed.add_field(name='/хелп',
                    value="Виводить повідомлення, яке ви зараз бачите.",
                    inline=False)
    embed.add_field(name='/анекдот',
                    value="Розповідає вам випадковий анекдот.",
                    inline=False)
    embed.add_field(name='/тіп @учасник',
                    value='Тіпає вказаного вами користувача серверу.',
                    inline=False)
    embed.add_field(name='/пінг', value='Відповідає вам "понг".', inline=False)
    embed.add_field(name='/рол [перше число], [друге число]',
                    value='Видає випадкове число в заданомоу діапазоні.',
                    inline=False)
    embed.add_field(name='/монет [Герб/Копійка]',
                    value='Підкидує монетку.',
                    inline=False)
    embed.add_field(name='/грати [посилання YouTube/Spotify або назва] [перемішати]',
                    value='Додає трек чи плейлист у чергу та грає у голосовому каналі.',
                    inline=False)
    embed.add_field(name='/перемішати',
                    value='Перемішує чергу.',
                    inline=False)
    embed.add_field(name='/цикл [Вимкнути/Поточний трек/Вся черга]',
                    value='Зациклює трек або всю чергу.',
                    inline=False)
    embed.add_field(name='/черга, /зараз, /далі, /пауза, /продовжити, /стоп, /вийти',
                    value='Керування музикою.',
                    inline=False)
    await Interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name='тіп', description='Тіпає вказаного користувача')
async def тіп(Interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title=':partying_face: Тіп :partying_face:',
        description=f'Користувач {member.mention} був тіпнутий користувачем {Interaction.user.mention}',
        color=discord.Color.teal())
    await Interaction.response.send_message(embed=embed)


@client.tree.command(
    name='рол', description='Видає будь-яке число в заданому вами діапазоні.')
async def рол(Interaction: discord.Interaction, число: int = None, друге_число: int = None):
    if друге_число == None and число == None:
        random_number = random.randint(1, 100)
        embed = discord.Embed(
            title=':game_die: Рол :game_die:',
            description=f'Ви отримали число **{random_number}** з діапазону **1 - 100**',
            color=discord.Color.red())
        await Interaction.response.send_message(embed=embed)
    elif друге_число != None:
        if число > друге_число:
            random_number = random.randint(число, друге_число)
            embed = discord.Embed(
                title=':game_die: Рол :game_die:',
                description=f'Ви отримали число **{random_number}** з діапазону **{число} - {друге_число}**',
                color=discord.Color.red())
            await Interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                description=f'Число {друге_число} менше за число {число}, скористайтесь командою ще раз, та введіть дані правильним чином!',
                color=discord.Color.red())
            await Interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        random_number = random.randint(1, число)
        embed = discord.Embed(
            title=':game_die: Рол :game_die:',
            description=f'Ви отримали число **{random_number}** з діапазону **1 - {число}**',
            color=discord.Color.red())
        await Interaction.response.send_message(embed=embed)


@client.tree.command(name='монета', description='Підкидує монету')
@app_commands.choices(вибір=[
    app_commands.Choice(name="Герб", value="герб"),
    app_commands.Choice(name='Копійка', value='копійка')
])
async def монета(Interaction: discord.Interaction, вибір: app_commands.Choice[str] = None):
    values = ["герб", "копійка"]
    computerchoice = random.choice(values)
    if вибір == None:
        embed = discord.Embed(
            title=':coin: Монета :coin:',
            color=discord.Color.orange(),
            description=f'На жаль, чи на нещастя :face_with_monocle:, це **{computerchoice}**!')
        await Interaction.response.send_message(embed=embed)
    elif computerchoice == вибір.value:
        embed = discord.Embed(
            title=':coin: Монета :coin:',
            color=discord.Color.orange(),
            description=f'Ви вгадали :partying_face:! Це дійсно **{computerchoice}**!'
        )
        await Interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=':coin: Монета :coin:',
            color=discord.Color.orange(),
            description=f'Ви не вгадали :frowning2:. Нажаль це **{computerchoice}**('
        )
        await Interaction.response.send_message(embed=embed)


@client.tree.command(name='вірші',
                     description='Розповідає мої придумані/перероблені вірші')
@app_commands.choices(вибір=[
    app_commands.Choice(name="Рандом", value="рандом"),
    app_commands.Choice(name='Любов Хардіка', value="0"),
    app_commands.Choice(name="Про Хардіка", value="1"),
    app_commands.Choice(name='Про Владоса', value="2"),
    app_commands.Choice(name='Про Лілу Катін і Хардіка', value="3"),
    app_commands.Choice(name='Ліла Катін (ориг. - Натаха С. Жадан)', value="4"),
    app_commands.Choice(name='Хардік Помер (ориг. - Марат С. Жадан)', value="5"),
    app_commands.Choice(name='300 Владосів (ориг. - 300 китайців Жадан і Собаки)', value="6")
])
async def вірші(Interaction: discord.Interaction,
                вибір: app_commands.Choice[str]):
    values = [
        ":mending_heart: Любов Хардіка :mending_heart:",
        ":star_struck: Про Хардіка :star_struck:",
        "<:General_Vlados:1085193355216035840> Про Владоса <:General_Vlados:1085193355216035840>",
        ':kiss: Про Лілу Катін і Хардіка :kiss:',
        ':cold_face: Ліла Катін :cold_face: (ориг. - Натаха С. Жадан)',
        ':sob: Хардік Помер :sob: (ориг. - Марат С. Жадан)',
        ":three::zero::zero: 300 Владосів (ориг. - 300 китайців ЖіС) :three::zero::zero:"
    ]
    if вибір.value == "рандом":
        computerchoice = random.choice(virsh)
        zagolovok = values[virsh.index(computerchoice)]
    else:
        print(вибір.value)
        int_value = int(вибір.value)
        print(int_value)
        zagolovok = values[int_value]
        computerchoice = virsh[int_value]
    embed = discord.Embed(
        title=f':page_with_curl: Вірші :page_with_curl:\n{zagolovok}',
        color=discord.Color.green(),
        description=computerchoice)
    await Interaction.response.send_message(embed=embed)


@client.tree.command(name='sigame',
                     description='Всі потрібні дані для гри в SIgame')
async def sigame(Interaction: discord.Interaction):
    embed = discord.Embed(title="SIGame",
                          description="Всі потрібні дані для гри SIgame",
                          colour=discord.Colour.dark_purple())
    embed.add_field(name='Посилання на онлайн версію гри',
                    value="https://vladimirkhil.com/si/online/",
                    inline=False)
    embed.add_field(name='Назва кімнати', value="alpha", inline=False)
    embed.add_field(name='Пароль від кімнати', value='bebe', inline=False)
    embed.add_field(name='Бібліотека паків',
                    value='https://sigame.xyz/',
                    inline=False)
    await Interaction.response.send_message(embed=embed)


@client.tree.command(
    name='шипирити',
    description='Шипирить вказаного учасника з учасником, який найбільш йому підходить')
@discord.app_commands.checks.cooldown(1,
                                      120,
                                      key=lambda i: (i.guild_id, i.user.id))
async def шипирити(Interaction: discord.Interaction, користувач: discord.Member = None):
    member = користувач
    if member is None:
        while (True):
            member = choice(Interaction.guild.members)
            if (member.id != 958711560786812958
                    and member.id != 1080576224293822587
                    and member.id != 310848622642069504
                    and member.id != 1075068110714970112
                    and member.id != 472911936951156740
                    and member.id != 228537642583588864
                    and member.id != 684773505157431347
                    and member.id != 829466856746123305):
                break
    if (member.id == 958711560786812958 and member.id == 1080576224293822587
            and member.id == 310848622642069504 and member.id == 1075068110714970112
            and member.id == 472911936951156740 and member.id == 228537642583588864
            and member.id == 684773505157431347 and member.id == 829466856746123305):
        await Interaction.response.send_message(
            text='Друже, треба обрати людину, а не бота)', ephemeral=True)
    while (True):
        shyp_member = choice(Interaction.guild.members)
        if (shyp_member.id != 958711560786812958
                and shyp_member.id != 1080576224293822587
                and shyp_member.id != 310848622642069504
                and shyp_member.id != 1075068110714970112
                and shyp_member.id != 472911936951156740
                and shyp_member.id != 228537642583588864
                and shyp_member.id != 684773505157431347
                and shyp_member.id != 829466856746123305 and shyp_member != member):
            break
    embed = discord.Embed(
        title=':revolving_hearts: Шипирство :revolving_hearts:',
        description=f'{member.mention} любить {shyp_member.mention}',
        color=discord.Color.red())
    await Interaction.response.send_message(embed=embed)


# @client.event
# async def on_member_remove(member):
#     if member.id == 470992060976070657:
#         channel = client.get_channel(1080562042957733908)
#         await channel.send("Владосік, ти куди? :thinking:")


@client.tree.command(name='розклад',
                     description='Підскажить шо там по розкладу')
@app_commands.choices(день=[
    app_commands.Choice(name="Понеділок", value="0"),
    app_commands.Choice(name="Вівторок", value="1"),
    app_commands.Choice(name="Середа", value="2"),
    app_commands.Choice(name="Четвер", value="3"),
    (app_commands.Choice(name="П'ятниця", value="4"))
])
async def розклад(Interaction: discord.Interaction,
                  день: app_commands.Choice[str] = None):
    embed = discord.Embed(
        title="Розклад уроків 9-В",
        description="Покаже розклад на день, визначить який урок зараз, наступний та чи ще є уроки сьогодні",
        colour=discord.Colour.green())
    weekday_array = [monday, tuesday, wednesday, thursday, friday]
    delta = datetime.timedelta(hours=3, minutes=0)
    data_time_today = datetime.datetime.now(datetime.timezone.utc) + delta
    weekday_today = data_time_today.isoweekday() - 1
    if день is None:
        time_now = data_time_today.time()
        if weekday_today <= 4:
            WeekDay = weekday_array[weekday_today]
            if time_now < WeekDay.time[0]:
                embed.add_field(
                    name=" ",
                    value=f"Першим уроком буде {WeekDay.names[0]} {WeekDay.time[0]}-{WeekDay.time_end[0]} \nПосилання: {WeekDay.url[0]}"
                )
            else:
                for i in range(len(WeekDay.time)):
                    if time_now > WeekDay.time_end[len(WeekDay.time) - 1]:
                        embed.add_field(
                            name=" ", value="На сьогодні уроки закінчились!!!")
                        break
                    elif time_now >= WeekDay.time[i] and time_now < WeekDay.time_end[i]:
                        if i != len(WeekDay.time) - 1:
                            embed.add_field(
                                name=" ",
                                value=f"Зараз йде: {WeekDay.names[i]} {WeekDay.time[i]}-{WeekDay.time_end[i]} \nПосилання: {WeekDay.url[i]} \nНаступний урок буде:{WeekDay.names[i + 1]} {WeekDay.time[i + 1]}-{WeekDay.time_end[i + 1]} \nПосилання: {WeekDay.url[i + 1]}"
                            )
                        else:
                            embed.add_field(
                                name=" ",
                                value=f"Зараз йде: {WeekDay.names[i]} {WeekDay.time[i]}-{WeekDay.time_end[i]} \nПосилання: {WeekDay.url[i]} \nЦе останній урок"
                            )
                        break
                    elif time_now >= WeekDay.time_end[i] and time_now < WeekDay.time[i + 1]:
                        embed.add_field(
                            name=" ",
                            value=f"Зараз перерва, наступний урок: {WeekDay.names[i + 1]} {WeekDay.time[i + 1]}-{WeekDay.time_end[i + 1]} \nПосилання: {WeekDay.url[i + 1]}"
                        )
                        break
                await Interaction.response.send_message(embed=embed)
        else:
            embed.add_field(name=" ", value="Вихідний!!! (Dzidzio референс)")
            await Interaction.response.send_message(embed=embed)
    else:
        weekday_today = int(день.value)
        WeekDay = weekday_array[weekday_today]
        if weekday_today <= 2:
            nomer = 0
        elif weekday_today >= 3:
            nomer = 1

        for i in range(len(WeekDay.time)):
            embed.add_field(name=" ",
                            value=f"{nomer} . {WeekDay.names[i]} ({WeekDay.time[i]}-{WeekDay.time_end[i]})\nПосилання:{WeekDay.url[i]}\n",
                            inline=False)
            nomer += 1
        await Interaction.response.send_message(embed=embed)


@client.tree.command(name='розкладочка',
                     description='Змінює розкладочку ))')
async def розкладочка(Interaction: discord.Interaction, строка: str):
    embed = discord.Embed(title="Змінити розкладку",
                          description="Змінює розкладку))",
                          colour=discord.Colour.dark_purple())
    гстрока = change_rozkladka(строка)
    embed.add_field(name=f"{гстрока}", value=' ')
    await Interaction.response.send_message(embed=embed)


# @client.tree.command(
#     name='голосувати', description='проголосувати за кандидати на пост Презідента сервера')
# # @discord.app_commands.checks.cooldown(1, 50000, key=lambda i: (i.guild_id, i.user.id))
# @app_commands.choices(вибір=[
#     app_commands.Choice(name="#1 Даніїл Карасенко", value="Даніїл Карасенко"),
#     app_commands.Choice(name="#2 wantage", value="wantage"),
# ])
# async def голосувати(Interaction: discord.Interaction, вибір: app_commands.Choice[str]):
#     if (Interaction.user.id == 621697764841226251 and вибір.value == "Даніїл Карасенко") or (Interaction.user.id == 660072518803128345 and вибір.value == "wantage"):
#         embed = discord.Embed(
#             title="Голосування", description=f"Дурак сам за себе не голосують!!!", colour=discord.Colour.blue())
#         await Interaction.response.send_message(embed=embed, ephemeral=True)
#     else:
#         perevirka = False
#         file = open('voting.txt', 'r', encoding='utf-8')
#         for lane in file:
#             word=lane.split()
#             print(word)
#             if word[0] == Interaction.user.name:
#                 perevirka=True
#                 break
#         file.close
#         if perevirka==True:
#             embed = discord.Embed(title="Голосування", description=f"Ви вже проголосували за {word[3]}!!!", colour=discord.Colour.blue())
#         else:
#             file = open('voting.txt', 'a', encoding='utf-8')
#             file.write(f"{Interaction.user} проголосував за {вибір.value} \n")
#             file.close()
#             embed = discord.Embed(title="Голосування", description=f"Ви проголосували за {вибір.value}", colour=discord.Colour.blue())
#         await Interaction.response.send_message(embed=embed, ephemeral=True)


# ---------- Музика (вся логіка в muzyka.py) ----------
@client.event
async def on_voice_state_update(member, before, after):
    await muzyka.voice_update(client.user, member, before, after)


@client.tree.command(name='грати',
                     description='Додає в чергу трек чи плейлист з YouTube/Spotify або за назвою')
@app_commands.describe(запит='Посилання на YouTube/Spotify або назва пісні',
                       перемішати='Перемішати додані треки (для плейлистів)')
@app_commands.guild_only()
async def грати(Interaction: discord.Interaction, запит: str, перемішати: bool = False):
    voice = getattr(Interaction.user, 'voice', None)
    if not voice or not voice.channel:
        await Interaction.response.send_message(
            embed=muzyka.pomylka('Спочатку зайди в голосовий канал!'), ephemeral=True)
        return
    await Interaction.response.defer()

    try:
        tracks, name = await muzyka.build_tracks(запит.strip(), Interaction.user)
    except muzyka.MusicError as e:
        await Interaction.followup.send(embed=muzyka.pomylka(str(e)))
        return

    vc = Interaction.guild.voice_client
    try:
        if vc is None:
            vc = await voice.channel.connect()
        elif vc.channel != voice.channel:
            if vc.is_playing() or vc.is_paused():
                await Interaction.followup.send(
                    embed=muzyka.pomylka(f'Бот уже грає в {vc.channel.mention}.'))
                return
            await vc.move_to(voice.channel)
    except (discord.ClientException, asyncio.TimeoutError, discord.Forbidden):
        await Interaction.followup.send(
            embed=muzyka.pomylka('Не вдалося підключитися до голосового каналу.'))
        return

    player = muzyka.players.get(Interaction.guild_id)
    if player is None:
        player = muzyka.Player(Interaction.guild, Interaction.channel)
        muzyka.players[Interaction.guild_id] = player
    player.channel = Interaction.channel

    if перемішати:
        random.shuffle(tracks)
    player.queue.extend(tracks)
    player.wakeup.set()

    if len(tracks) == 1:
        text = f'Додано в чергу: **{tracks[0].title}**'
    else:
        text = f'Додано **{len(tracks)}** треків з **{name}**'
        if перемішати:
            text += ' (перемішано :twisted_rightwards_arrows:)'
    embed = discord.Embed(title=':musical_note: Музика :musical_note:',
                          description=text,
                          color=discord.Color.blurple())
    await Interaction.followup.send(embed=embed)


@client.tree.command(name='перемішати', description='Перемішує поточну чергу')
@app_commands.guild_only()
async def перемішати(Interaction: discord.Interaction):
    player = await muzyka.perevirka(Interaction)
    if not player:
        return
    if len(player.queue) < 2:
        await Interaction.response.send_message(
            embed=muzyka.pomylka('У черзі замало треків для перемішування.'), ephemeral=True)
        return
    random.shuffle(player.queue)
    embed = discord.Embed(
        title=':twisted_rightwards_arrows: Перемішування :twisted_rightwards_arrows:',
        description=f'Чергу з **{len(player.queue)}** треків перемішано!',
        color=discord.Color.blurple())
    await Interaction.response.send_message(embed=embed)


@client.tree.command(name='цикл', description='Зациклює поточний трек або всю чергу')
@app_commands.describe(режим='Що зациклювати')
@app_commands.choices(режим=[
    app_commands.Choice(name="Вимкнути", value="off"),
    app_commands.Choice(name="Поточний трек", value="track"),
    app_commands.Choice(name="Вся черга", value="queue")
])
@app_commands.guild_only()
async def цикл(Interaction: discord.Interaction, режим: app_commands.Choice[str]):
    player = await muzyka.perevirka(Interaction)
    if not player:
        return
    player.loop = режим.value
    embed = discord.Embed(
        title=':repeat: Цикл :repeat:',
        description=f'Цикл: **{muzyka.LOOP_LABELS[player.loop]}**',
        color=discord.Color.blurple())
    await Interaction.response.send_message(embed=embed)


@client.tree.command(name='далі', description='Пропускає поточний трек')
@app_commands.guild_only()
async def далі(Interaction: discord.Interaction):
    player = await muzyka.perevirka(Interaction)
    if not player:
        return
    if player.current is None:
        await Interaction.response.send_message(
            embed=muzyka.pomylka('Зараз нічого не грає.'), ephemeral=True)
        return
    player.skipped = True
    vc = Interaction.guild.voice_client
    if vc.is_playing() or vc.is_paused():
        vc.stop()
    embed = discord.Embed(title=':next_track: Пропуск :next_track:',
                          description='Трек пропущено.',
                          color=discord.Color.blurple())
    await Interaction.response.send_message(embed=embed)


@client.tree.command(name='пауза', description='Ставить музику на паузу')
@app_commands.guild_only()
async def пауза(Interaction: discord.Interaction):
    player = await muzyka.perevirka(Interaction)
    if not player:
        return
    vc = Interaction.guild.voice_client
    if vc.is_playing():
        vc.pause()
        embed = discord.Embed(title=':pause_button: Пауза :pause_button:',
                              description='Музику поставлено на паузу.',
                              color=discord.Color.blurple())
        await Interaction.response.send_message(embed=embed)
    else:
        await Interaction.response.send_message(
            embed=muzyka.pomylka('Нічого ставити на паузу.'), ephemeral=True)


@client.tree.command(name='продовжити', description='Знімає музику з паузи')
@app_commands.guild_only()
async def продовжити(Interaction: discord.Interaction):
    player = await muzyka.perevirka(Interaction)
    if not player:
        return
    vc = Interaction.guild.voice_client
    if vc.is_paused():
        vc.resume()
        embed = discord.Embed(title=':arrow_forward: Продовжуємо :arrow_forward:',
                              description='Музика знову грає.',
                              color=discord.Color.blurple())
        await Interaction.response.send_message(embed=embed)
    else:
        await Interaction.response.send_message(
            embed=muzyka.pomylka('Музика не на паузі.'), ephemeral=True)


@client.tree.command(name='стоп', description='Зупиняє музику та очищає чергу')
@app_commands.guild_only()
async def стоп(Interaction: discord.Interaction):
    player = await muzyka.perevirka(Interaction)
    if not player:
        return
    player.queue.clear()
    player.loop = "off"
    vc = Interaction.guild.voice_client
    if player.current is not None:
        player.skipped = True
        if vc.is_playing() or vc.is_paused():
            vc.stop()
    embed = discord.Embed(title=':stop_button: Стоп :stop_button:',
                          description='Музику зупинено, чергу очищено.',
                          color=discord.Color.blurple())
    await Interaction.response.send_message(embed=embed)


@client.tree.command(name='вийти', description='Бот виходить з голосового каналу')
@app_commands.guild_only()
async def вийти(Interaction: discord.Interaction):
    player = await muzyka.perevirka(Interaction)
    if not player:
        return
    embed = discord.Embed(title=':wave: Бувайте :wave:',
                          description='Виходжу з голосового каналу.',
                          color=discord.Color.blurple())
    await Interaction.response.send_message(embed=embed)
    await player.shutdown()


@client.tree.command(name='зараз', description='Показує, що зараз грає')
@app_commands.guild_only()
async def зараз(Interaction: discord.Interaction):
    player = muzyka.players.get(Interaction.guild_id)
    if not player or player.current is None:
        await Interaction.response.send_message(
            embed=muzyka.pomylka('Зараз нічого не грає.'), ephemeral=True)
        return
    await Interaction.response.send_message(embed=player.now_playing_embed())


@client.tree.command(name='черга', description='Показує чергу треків')
@app_commands.guild_only()
async def черга(Interaction: discord.Interaction):
    player = muzyka.players.get(Interaction.guild_id)
    if not player or (player.current is None and not player.queue):
        await Interaction.response.send_message(
            embed=muzyka.pomylka('Черга порожня.'), ephemeral=True)
        return
    embed = discord.Embed(title=':scroll: Черга :scroll:', color=discord.Color.blurple())
    if player.current:
        embed.add_field(name='Зараз грає', value=player.current.title, inline=False)
    if player.queue:
        lines = [f'`{i}.` {t.title}' for i, t in enumerate(player.queue[:10], 1)]
        if len(player.queue) > 10:
            lines.append(f'…і ще {len(player.queue) - 10}')
        embed.add_field(name='Далі', value='\n'.join(lines)[:1024], inline=False)
    embed.set_footer(text=f'Цикл: {muzyka.LOOP_LABELS[player.loop]}')
    await Interaction.response.send_message(embed=embed)


# Помилки
@анекдот.error
async def on_error(interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        msg = '**Зачекайте** та спробуйте ще раз через **{:.0f}** секунд!'.format(
            error.retry_after)
        await interaction.response.send_message(msg, ephemeral=True)


@шипирити.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        msg = '**Зачекайте** та спробуйте ще раз через **{:.0f}** секунд!'.format(
            error.retry_after)
        await interaction.response.send_message(msg, ephemeral=True)


# токен
import logging
client.run(TOKEN, log_level=logging.WARNING)