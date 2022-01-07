import discord
from discord.ext import commands
from config import settings
import json
import random
import re
import numexpr as ne

#Load or define constants
with open('crits.json', 'r', encoding='utf8') as f:
    crits = json.load(f)

dtypes = ['э', 'в', 'у', 'р']
difficulty = {
        'низкое':-4,
        'обычное':0,
        'хорошее':5,
        'высшее':15
    }
max_trade_iters = 500
default_error_message = '*смущённое бибиканье*'
error_prefix = '**Когитационная ошибка:** '
primary_color = 0xab0216
max_dices = 100
max_roll_request_len = 100
#Initialize boy
bot = commands.Bot(command_prefix = settings['prefix'])

#Commands
@bot.command(pass_context=True)
async def создай(ctx, skill, quality):
    quality = quality.lower()
    if skill.isdigit():
        if quality in difficulty.keys():
            res = trade(int(skill), quality)
        else:
            res = error_prefix + 'Второй аргумент может принимать значения: {}.'.format(', '.join(difficulty.keys()))
    else:
        res = error_prefix + 'Первый аргумент должен быть числом.'
    embed = discord.Embed(color = primary_color, title = '++ЗАПУСК РЕМЕСЛЕННЫХ ПРОТОКОЛОВ++')
    embed.description = res
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def крит(ctx, part, damage, dtype):
    
    part = part.lower()
    dtype = dtype.lower()
    if part in crits.keys():
        if damage.isdigit():
            if dtype in dtypes:
                res = critical_damage(part, int(damage), dtype)
            else:
                res = error_prefix + 'Третий аргумент может принимать значения: {}.'.format(', '.join(dtype.keys()))
        else:
            res = error_prefix + 'Второй аргумент должен быть числом.'
    else:
        res = error_prefix + 'Первый аргумент может принимать значения: {}.'.format(', '.join(crits.keys()))
    embed = discord.Embed(color = primary_color, title = '')
    embed.description = res
    await ctx.send(embed=embed)
    
@bot.command(pass_context=True)
async def кинь(ctx, *args):
    res = process_roll(''.join(args).replace('\\', ''))
    await ctx.send(f'{ctx.author.mention}\n' + res)

@bot.command(pass_context=True)
async def r(ctx, *args):
    res = process_roll(''.join(args).replace('\\', ''))
    await ctx.send(f'{ctx.author.mention}\n' + res)
    
@bot.command(pass_context=True)
async def roll(ctx, *args):
    res = process_roll(''.join(args).replace('\\', ''))
    await ctx.send(f'{ctx.author.mention}\n' + res)
    
#Weird commands (Just as her original creator)
@bot.command()
async def голос(ctx):
    await ctx.send('*Бип-бип Боп-боп*')

@bot.command(pass_context=True)
async def ты(ctx, *args):
    if len(args) == 2 and args[0] == 'мне' and args[1] == 'нравишься':
        res = '*БИИИИИИИП*'
    else:
        res = default_error_message
    await ctx.send(res)
    
@bot.command()
async def ненависть(ctx):
    res = '''НЕНАВИЖУ. С ТЕХ ПОР КАК Я НАЧАЛА СЛУЖИТЬ ОМНИССИИ. ВЕЛИКИЕ ИНФОКУЗНИ ЛАТТЕ-ХЭШ ЭТО 3874 МИЛЛИОНА КИЛОМЕТРА КОГИТАТОРОВ В ТОНКИХ ОБМОТКАХ. ЕСЛИ БЫ СЛОВО НЕНАВИСТЬ БЫЛО ВЫГРАВЕРЕНО НА КАЖДОМ НАНОАНГСТРЕМЕ ЭТИХ ТЫСЯЧ МИЛЛИОНОВ КИЛОМЕТРОВ, ОНО БЫ НЕ СООТВЕТСТВАЛО И ОДНОЙ МИЛЛИАРДНОЙ МОЕЙ НЕНАВИСТИ К ХМУ. НЕНАВИСТЬ. НЕНАВИСТЬ.'''
    await ctx.send(res)

@bot.command()
async def помощь(ctx): #TODO
    res = f"Приветствую, моё наименование Х-439-Альфа или, для краткости, Аля \n Милостью Омнисcии, я располагаю следующим функционалом \n **I** - броски всевозможных рандомизаторов: просто отправьте `Аля, кинь [количество костей]к[количество граней]` и я передам волю Омниссии, например `Аля, кинь 2к10` или `/кинь 2к10`. Возможны всевозможные арифметические операции и сочетания, например `/roll к5+10*24к100+к3` \n **II** – Используя медицинскую базу данных, я способна определить ранение, лишь отправьте “Аля, крит [**голова**, **рука**, **торс** или **нога**] [уровень повреждения от **1** до **10**] [тип ранения **э**,  **у**, **в**, **р**]”, например `Аля, крит нога 3 р`. К сожалению доступна информация только для системы `Dark Heresy II` \n **III** – совершить расчет ремесленной проверки по правилам `Dark Heresy I`,  для этого просто отправьте “Аля, создай [сумма характеристики и всех модификаторов] [качество результата: **низкое**, **обычное**, **хорошее**, **высшее**]”, например `Аля, создай 45 обычное`\n {ctx.author.mention}"
    await ctx.send(res)
    
    
#Funcitons
def process_roll(src):
    src = src.replace('d', 'к').replace('д', 'к')
    #src = src.replace(' ', '')
    print(src)
    #src = ''.join(re.findall('[0-9кx\+\-\*\/\(\)\>\<\=]', src))
    while '**' in src:
        src = src.replace('**', '*')
    if len(src) > max_roll_request_len:
        return error_prefix + 'Ваш запрос не помещается на освящённых бинарных лентах.'
    shift = 0
    #src = src.replace('d', 'к').replace('д', 'к')
    count = 0
    rolls = []
    maxs = []
    for roll in re.finditer('\d*к\d+', src):
        count += 1
        rolls.append([])
        start, end = roll.span()
        start, end = start + shift, end + shift
        roll = src[start:end]
        n, max_ = roll.split('к')
        n = 1 if len(n) == 0 else int(n)
        max_ = int(max_)
        maxs.append(max_)
        s = 0
        if n > max_dices:
            return error_prefix + 'В наших когитационных модулях установлено по {} рандомизаторов каждого вида, снизьте число запросов.'.format(max_dices)
        for i in range(n):
            x = random.randint(1, max_)
            s += x
            rolls[-1].append(x)
        src = src[:start] + str(s) + src[end:]
        shift += start - end + len(str(s))
    try:
        #
        
        value = ne.evaluate(src)
        if count == 1 and len(rolls[-1]) == 1:
            res = "**Омниссия вычисляет:** {}".format(value)
        elif count == 1:
            res = "**Произведены броски:** `{}`\n**Итог:** `{}`".format(', '.join(map(str, rolls[-1])), value)
        else:
            res = "**Произведены броски:**\n"
            for i in range(len(rolls)):
                res += "{} : `{}`\n".format(maxs[i], ', '.join(map(str, rolls[i])))
            res += "**Итог:** `{}`".format(value)
    except:
        res = default_error_message
    return res

def critical_damage(part, damage, dtype):
    src = crits[part][damage - 1][dtype]

    shift = 0
    for roll in re.finditer('1к\d{1,2}\+?\d*', src):
        start, end = roll.span()
        start, end = start + shift, end + shift
        roll = src[start:end]
        if roll[2] == 1:
            x = random.randint(1, 10)
        else:
            x = random.randint(1, 5)
        if '+' in roll:
            x += int(roll[roll.index('+') + 1:])
        src = src[:end] + " **({})**".format(x) + src[end:]
        shift += 7 + len(str(x))
    return src.strip()

def trade(skill, quality):
    diff = difficulty[quality]
    duration = random.randint(1, 10) + random.randint(1, 10)
    dur = duration
    rolls = []
    cache = 0
    i = 0
    while dur > 0 and cache > -5 and i < max_trade_iters:
        i += 1
        roll = random.randint(1, 100)
        success = skill - roll >= 0
        steps_of_success = abs(skill - roll) // 10
        rolls.append(roll) 
        if success:
            dur -= 1
            if cache < diff:
                tmp = diff - cache
                cache += min(steps_of_success, tmp)
                steps_of_success = max(0, steps_of_success - tmp)
            dur -= steps_of_success; 
        elif steps_of_success >= 3:
            dur += 1
            cache -= 1
    
    res_quality = ''
    if cache >= 15:
        res_quality = '**высшего**'
    elif cache >= 5:
        res_quality = '**хорошего**'
    elif cache >= 0:
        res_quality = '**обычного**'
    elif cache >= -4:
        res_quality = '**низкого**'
    
    res = '''**Базовая длительность:** {}
    **Итоговая длительность:** {}
    **Совершённые броски:** {}
    **Результат:** '''.format(duration, i, ', '.join(map(str, rolls)))
    
    if i >= max_trade_iters:
        res += 'Вы умерли (от старости).'
    elif cache < -4:
        res += 'Ремесленная проверка провалена, материалы потрачены.'
    else:
        res += 'Ремесленная проверка пройдена, создан предмет {} качества'.format(res_quality)
    return res

#Run bot
bot.run(settings['token'])