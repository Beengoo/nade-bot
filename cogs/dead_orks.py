import discord
from discord.ext import commands
import requests
from discord import app_commands
from discord import Embed


class DeadOrks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.stats = {
            "ok": "The data were fetched successfully.",
            "invalid_data": "The given data was invalid."
        },
        self.data = {}

    @app_commands.command(name="war-states")
    @app_commands.describe(
        date="Вкажіть дату в форматі (рік-число-місяць)"
    )
    async def on_state(self, interaction: discord.Interaction, date: str = None):
        await interaction.response.defer(ephemeral=False, thinking=True)
        await self.send_state(interaction=interaction, data=await self.get_data(date=date))

    async def get_data(self, date: str = None):
        if date is None:
            date = requests.get("https://russianwarship.rip/api/v2/war-info").json()
            date = date["data"]["current_date"]

        war_data = requests.get(f"https://russianwarship.rip/api/v2/statistics?offset=0&limit=50&date_from={date}&date_to={date}").json()

        return {
            "resource": war_data['data']['records'][0]['resource'],
            "date": war_data['data']['records'][0]['date'],
            "day": war_data['data']['records'][0]['day'],
            "stats": {
                "personnel_units": [war_data['data']['records'][0]['stats']['personnel_units'],
                                    war_data['data']['records'][0]['increase']['personnel_units']],

                "tanks": [war_data['data']['records'][0]['stats']['tanks'],
                          war_data['data']['records'][0]['increase']['tanks']],

                "armoured_fighting_vehicles": [war_data['data']['records'][0]['stats']['armoured_fighting_vehicles'],
                                               war_data['data']['records'][0]['increase']['armoured_fighting_vehicles']],

                "artillery_systems": [war_data['data']['records'][0]['stats']['artillery_systems'],
                                      war_data['data']['records'][0]['increase']['artillery_systems']],

                "mlrs": [war_data['data']['records'][0]['stats']['mlrs'],
                         war_data['data']['records'][0]['increase']['mlrs']],

                "aa_warfare_systems": [war_data['data']['records'][0]['stats']['aa_warfare_systems'],
                                       war_data['data']['records'][0]['increase']['aa_warfare_systems']],

                "planes": [war_data['data']['records'][0]['stats']['planes'],
                           war_data['data']['records'][0]['increase']['planes']],

                "helicopters": [war_data['data']['records'][0]['stats']['helicopters'],
                                war_data['data']['records'][0]['increase']['helicopters']],

                "vehicles_fuel_tanks": [war_data['data']['records'][0]['stats']['vehicles_fuel_tanks'],
                                        war_data['data']['records'][0]['increase']['vehicles_fuel_tanks']],

                "warships_cutters": [war_data['data']['records'][0]['stats']['warships_cutters'],
                                     war_data['data']['records'][0]['increase']['warships_cutters']],

                "cruise_missiles": [war_data['data']['records'][0]['stats']['cruise_missiles'],
                                    war_data['data']['records'][0]['increase']['cruise_missiles']],

                "uav_systems": [war_data['data']['records'][0]['stats']['uav_systems'],
                                war_data['data']['records'][0]['increase']['uav_systems']],

                "special_military_equip": [war_data['data']['records'][0]['stats']['special_military_equip'],
                                           war_data['data']['records'][0]['increase']['special_military_equip']],

                "atgm_srbm_systems": [war_data['data']['records'][0]['stats']['atgm_srbm_systems'],
                                      war_data['data']['records'][0]['increase']['atgm_srbm_systems']],
            }
        }

    async def send_state(self, interaction: discord.Interaction, data: dict):
        eb = Embed(title=f"[{data['date']}] Статистика втрат орків в Україні (день: {data['day']})",
                   description=f'[[Джерело]({data["resource"]})]')

        eb.add_field(name="Особовий склад",
                     value=f"{data['stats']['personnel_units'][0]} (+{data['stats']['personnel_units'][1]})", inline=False)

        eb.add_field(name="Танки",
                     value=f"{data['stats']['tanks'][0]} (+{data['stats']['tanks'][1]})", inline=False)

        eb.add_field(name="ББМ",
                     value=f"{data['stats']['armoured_fighting_vehicles'][0]} "
                           f"(+{data['stats']['armoured_fighting_vehicles'][1]})", inline=False)

        eb.add_field(name="Арт Системи",
                     value=f"{data['stats']['artillery_systems'][0]} (+{data['stats']['artillery_systems'][1]})", inline=False)

        eb.add_field(name="РСЗВ",
                     value=f"{data['stats']['mlrs'][0]} (+{data['stats']['mlrs'][1]})", inline=False)

        eb.add_field(name="Засоби ППО",
                     value=f"{data['stats']['aa_warfare_systems'][0]} (+{data['stats']['aa_warfare_systems'][1]})", inline=False)

        eb.add_field(name="Літаки",
                     value=f"{data['stats']['planes'][0]} (+{data['stats']['planes'][1]})", inline=False)

        eb.add_field(name="Гелікоптери",
                     value=f"{data['stats']['helicopters'][0]} (+{data['stats']['helicopters'][1]})", inline=False)

        eb.add_field(name="Автотехніки та автоцистерн",
                     value=f"{data['stats']['vehicles_fuel_tanks'][0]} (+{data['stats']['vehicles_fuel_tanks'][1]})", inline=False)

        eb.add_field(name="Кораблі та катери",
                     value=f"{data['stats']['warships_cutters'][0]} (+{data['stats']['warships_cutters'][1]})", inline=False)

        eb.add_field(name="БПЛА",
                     value=f"{data['stats']['uav_systems'][0]} (+{data['stats']['uav_systems'][1]})", inline=False)

        eb.add_field(name="Спец. техніка",
                     value=f"{data['stats']['special_military_equip'][0]} "
                           f"(+{data['stats']['special_military_equip'][1]})", inline=False)

        eb.add_field(name="Установок ОТРК/ТРК ",
                     value=f"{data['stats']['atgm_srbm_systems'][0]} (+{data['stats']['atgm_srbm_systems'][1]})", inline=False)

        eb.add_field(name="Крилатих ракет",
                     value=f"{data['stats']['cruise_missiles'][0]} (+{data['stats']['cruise_missiles'][1]})", inline=False)

        await interaction.edit_original_response(embed=eb)


async def setup(bot: commands.Bot):
    await bot.add_cog(DeadOrks(bot))
