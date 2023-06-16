import json
import os
import random
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord import File, Embed


class CrearRespuesta():
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.respuesta = discord.Embed(
            title=self.title,
            description=self.content,
            colour=int("3FFF3F", 16)
        )

    @property
    def enviar(self):
        return self.respuesta


class WelcomeEmbed():
    def __init__(self, member):
        self.member = member

    @property
    def enviar(self):
        return self.embed


def cargar_datos():
    if os.path.exists('config.json'):
        with open('config.json') as f:
            return json.load(f)
    else:
        template = {'prefix': '!', 'token': "", 'palabras baneadas': [], 'saldos': {}}
        with open('config.json', 'w') as f:
            json.dump(template, f)
        return template


def guardar_datos(datos):
    with open('config.json', 'w') as f:
        json.dump(datos, f)


def iniciar_saldo(user_id, datos):
    if str(user_id) not in datos['saldos']:
        datos['saldos'][str(user_id)] = 0
        guardar_datos(datos)


def obtener_saldo(user_id, datos):
    return datos['saldos'].get(str(user_id), 0)


def restar_dinero(user_id, cantidad, datos):
    datos['saldos'][str(user_id)] -= cantidad
    guardar_datos(datos)


def agregar_dinero(user_id, cantidad, datos):
    datos['saldos'][str(user_id)] += cantidad
    guardar_datos(datos)


def es_dueño_servidor(ctx):
    return ctx.bot.is_owner(ctx.author)

def main():
    if os.path.exists('config.json'):
        with open('config.json') as f:
            config_data = json.load(f)
    else:
        template = {'prefix': '!', 'token': "", 'palabras baneadas': [], 'saldos': {}}
        with open('config.json', 'w') as f:
            json.dump(template, f)
        config_data = template

    palabrasbaneadas = config_data["palabras baneadas"]
    prefix = config_data["prefix"]
    token = config_data["token"]
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=prefix, intents=intents, description="Bot IA")

    @bot.command(name="saludar", help="El bot saluda")
    async def saludar(ctx):
        await ctx.reply(f'Hola {ctx.author}, ¿cómo estás?')

    @bot.command(name="sumar", help="Suma de dos números")
    async def sumar(ctx, num1: int, num2: int):
        suma = num1 + num2
        respuesta = CrearRespuesta(f'El resultado de la suma es: {suma}', None)
        await ctx.reply(embed=respuesta.enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Banear una palabra del servidor')
    async def banword(ctx, palabra):
        if palabra.lower() in palabrasbaneadas:
            await ctx.send(embed=CrearRespuesta('Esa palabra ya fue baneada', None).enviar)
        else:
            palabrasbaneadas.append(palabra.lower())
            config_data['palabras baneadas'] = palabrasbaneadas
            guardar_datos(config_data)
            respuesta = CrearRespuesta('Palabra baneada correctamente del servidor', None)
            await ctx.send(embed=respuesta.enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Quitar ban a una palabra del servidor')
    async def unbanword(ctx, palabra):
        if palabra.lower() in palabrasbaneadas:
            palabrasbaneadas.remove(palabra.lower())
            config_data['palabras baneadas'] = palabrasbaneadas
            guardar_datos(config_data)
            respuesta = CrearRespuesta('Palabra eliminada exitosamente', None)
            await ctx.send(embed=respuesta.enviar)
        else:
            respuesta = CrearRespuesta('Error', 'Esa palabra no se encuentra baneada dentro de este servidor')
            await ctx.send(embed=respuesta.enviar)

    @bot.command(name="integrantes", help="Muestra la lista de integrantes del servidor")
    async def integrantes(ctx):
        members = ctx.guild.members
        member_list = '\n'.join([member.name for member in members])
        respuesta = CrearRespuesta('Lista de Integrantes', member_list)
        await ctx.send(embed=respuesta.enviar)

    @bot.command(name="reglas", help="Muestra las reglas del servidor")
    async def reglas(ctx):
        reglas = "1. No hacer spam.\n2. No compartir contenido inapropiado.\n3. Respetar a los demás miembros.\n4. No hacer bullying o acoso.\n5. Evitar el uso de lenguaje ofensivo.\n6. Que le vayas a las chivas.\n7. Que te guste Star Wars.\n8. Que seas Checo Lover\n\nEstas son las reglas del servidor."
        respuesta = CrearRespuesta('Reglas del Servidor', reglas)
        await ctx.send(embed=respuesta.enviar)

    @bot.command(name="kick", help="Expulsa a un miembro del servidor")
    @commands.has_permissions(kick_members=True)
    async def kick(ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        respuesta = CrearRespuesta('Miembro Expulsado', f'El miembro {member.mention} ha sido expulsado del servidor.')
        await ctx.send(embed=respuesta.enviar)

    @bot.command(name="ban", help="Banear a un miembro del servidor")
    @commands.has_permissions(ban_members=True)
    async def ban(ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="Usuario Baneado", description=f'{member} ha sido baneado de este servidor', colour="3FFF3F")
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error", description=str(e), colour="FF0000")
            await ctx.send(embed=embed)

    @bot.command(name="unban", help="Desbanear a un miembro del servidor")
    @commands.has_permissions(ban_members=True)
    async def unban(ctx, user_id: int, *, reason=None):
        try:
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(title="Unban", description=f'{user.name}({user_id}) ha sido desbaneado', colour="3FFF3F")
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error", description=str(e), colour="FF0000")
            await ctx.send(embed=embed)

    @bot.command(name="transferir", help="Transfiere dinero a otro usuario")
    async def transferir(ctx, amount: int, member: discord.Member):
        if amount <= 0:
            respuesta = CrearRespuesta('Error', 'La cantidad a transferir debe ser mayor a 0')
            await ctx.send(embed=respuesta.enviar)
            return

        datos = cargar_datos()

        if obtener_saldo(ctx.author.id, datos) < amount:
            respuesta = CrearRespuesta('Error', 'No tienes suficiente saldo para realizar la transferencia')
            await ctx.send(embed=respuesta.enviar)
            return

        if ctx.author.id == member.id:
            respuesta = CrearRespuesta('Error', 'No puedes transferir dinero a ti mismo')
            await ctx.send(embed=respuesta.enviar)
            return

        restar_dinero(ctx.author.id, amount, datos)
        agregar_dinero(member.id, amount, datos)

        respuesta = CrearRespuesta('Transferencia Exitosa', f'Se ha transferido {amount} al usuario {member.mention}')
        await ctx.send(embed=respuesta.enviar)

    @bot.command(name="saldo", help="Muestra el saldo del usuario")
    async def saldo(ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        datos = cargar_datos()
        iniciar_saldo(member.id, datos)
        saldo = obtener_saldo(member.id, datos)

        respuesta = CrearRespuesta('Saldo', f'El saldo de {member.mention} es: {saldo}')
        await ctx.send(embed=respuesta.enviar)

    @commands.check(es_dueño_servidor)
    @bot.command(name="agregarfondos", help="Agrega fondos a un usuario")
    async def agregar_fondos(ctx, cantidad: int, member: discord.Member):
        datos = cargar_datos()
        iniciar_saldo(member.id, datos)
        datos['saldos'][str(member.id)] += cantidad
        guardar_datos(datos)
        respuesta = CrearRespuesta('Fondos Agregados', f'Se han agregado {cantidad} fondos a {member.name}.')
        await ctx.send(embed=respuesta.enviar)

    @agregar_fondos.error
    async def agregar_fondos_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            respuesta = CrearRespuesta('Error', 'Solo el dueño del servidor puede agregar fondos.')
            await ctx.send(embed=respuesta.enviar)

    @bot.command(name="apostar", help="Apostar una cantidad de dinero")
    async def apostar(ctx, amount: int):
        if amount <= 0:
            respuesta = CrearRespuesta('Error', 'La cantidad a apostar debe ser mayor a 0')
            await ctx.send(embed=respuesta.enviar)
            return

        datos = cargar_datos()

        if obtener_saldo(ctx.author.id, datos) < amount:
            respuesta = CrearRespuesta('Error', 'No tienes suficiente saldo para realizar la apuesta')
            await ctx.send(embed=respuesta.enviar)
            return

        opciones = ["ganar", "perder"]
        resultado = random.choice(opciones)

        if resultado == "ganar":
            ganancia = amount * 2
            agregar_dinero(ctx.author.id, ganancia, datos)
            respuesta = CrearRespuesta('¡Ganaste!', f'Has ganado {ganancia} monedas.')
            await ctx.send(embed=respuesta.enviar)
        else:
            restar_dinero(ctx.author.id, amount, datos)
            respuesta = CrearRespuesta('¡Perdiste!', f'Has perdido {amount} monedas.')
            await ctx.send(embed=respuesta.enviar)

    @bot.event
    async def on_ready():
        print(f'Bot iniciado como {bot.user.name}')

    @bot.event
    async def on_member_join(member):
        channel = member.guild.system_channel
        welcome_embed = WelcomeEmbed(member)
        await channel.send(embed=welcome_embed.enviar)

    bot.run(token)

if __name__ == "__main__":
    main()