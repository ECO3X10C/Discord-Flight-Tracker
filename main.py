
# CONFIGS

guild_id = 0  # REPLACE WITH GUILD ID 
token_text = " " # REPALCE WITH BOT TOKEN


# IMPORTANT INFO

"""

INFO:
-Check your intents
-flights might have two different codes(ex: WJA and WS), if one does not work, try using the other

IMPORTS:
discord
FlightRadarAPI
datetime
pytz
typing

CREDITS:
ADITYA KODURI
"""

# IMPORTS

from typing import Optional
from discord import app_commands
from FlightRadar24.api import FlightRadar24API
from datetime import date, datetime
import discord
from discord import member
from discord import file
from discord.ext import commands
import datetime
from datetime import datetime
import pytz


# API INNIT

fr_api = FlightRadar24API()
airports = fr_api.get_airports()
airlines = fr_api.get_airlines()
flights = fr_api.get_flights()
zones = fr_api.get_zones()

# DISCORD IMPORTS

MY_GUILD = discord.Object(id=guild_id) 
token = token_text 

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)

# CLIENT INNIT
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


# TRACK COMMAND
@client.tree.command()
async def track(interaction: discord.Interaction, airline: str, code: str):
    callsign = airline
    plane = code
    # TRY EXCEPT LOOP FOR ERRORS
    try:
        airlines = fr_api.get_airlines()
        plane = callsign + plane
        flights = False
        i = 0
        # SORT BY AIRLINE
        for flight in fr_api.get_flights(callsign.upper()):
            # SORT BY FLIGHT NUMBER
            if flight.check_info(callsign=plane.upper()):    

                # GET FLIGHT DATA
                flights = True
                details = fr_api.get_flight_details(flight.id)
                flight.set_flight_details(details)

                # GET ESTIMATED TAKEOFF AND LANDING TIMES
                scheduled = (flight.time_details.get("scheduled"))
                takeoff_time = scheduled.get("departure")
                ttz = pytz.timezone(flight.origin_airport_timezone_name)
                ltz = pytz.timezone(flight.destination_airport_timezone_name)
                takeoff_time = datetime.fromtimestamp(takeoff_time)
                landing_time = scheduled.get("arrival")
                landing_time = datetime.fromtimestamp(landing_time)
                takeoff_time = str(takeoff_time.astimezone(ttz))
                landing_time = str(landing_time.astimezone(ltz))
                takeoff_time = takeoff_time[:-6]
                landing_time = landing_time[:-6]

                #r GET REAL TAKEOFF AND LANDING TIMES
                scheduled_real = (flight.time_details.get("real"))
                takeoff_time_real = scheduled_real.get("departure")
                ttz_real = pytz.timezone(flight.origin_airport_timezone_name)
                ltz_real = pytz.timezone(flight.destination_airport_timezone_name)
                landing_time_real = scheduled_real.get("arrival")
                
                # CRAFT EMBED FOR FLIGHT 

                embed=discord.Embed(title = "Here is the current location of the aircraft",url =f"https://www.google.com/maps/search/{flight.latitude},+{flight.longitude}?shorturl=1" ,description=f"Here is the flight information for {plane.upper()}.",color=0xffffff)
                embed.add_field(name="Callsign", value=flight.callsign, inline=False)
                embed.add_field(name="Airline", value=flight.airline_name, inline=False)
                embed.add_field(name="Altitude", value=flight.altitude, inline=True)
                embed.add_field(name="Heading", value=flight.heading, inline=True)
                embed.add_field(name="Ground Speed", value=flight.ground_speed, inline=True)
                embed.add_field(name="Origin", value=f"{flight.origin_airport_name}({flight.origin_airport_iata})", inline=True)
                embed.add_field(name="Destination", value=f"{flight.destination_airport_name}({flight.destination_airport_iata})", inline=True)
                embed.add_field(name = "Aircraft Type",value=flight.aircraft_model)
                embed.add_field(name = "Time of Departure(Scheduled)",value = f"{takeoff_time}({flight.origin_airport_timezone_abbr})")
                embed.add_field(name="Time of Arival(Scheduled)", value=f"{landing_time}({flight.destination_airport_timezone_abbr})", inline=True)
                embed.add_field(name = "‎",value = "‎",inline = True)

                # CHECKING FLIGHT ARRIVAL AND DEAPRTURE
                try:
                    takeoff_time_real = datetime.fromtimestamp(takeoff_time_real)
                    takeoff_time_real = str(takeoff_time_real.astimezone(ttz_real))
                    takeoff_time_real = takeoff_time_real[:-6]
                    embed.add_field(name = "Time of Departure(Real)",value = f"{takeoff_time_real}({flight.origin_airport_timezone_abbr})",inline = True)
                except:
                    embed.add_field(name = "Time of Departure(Real)",value = f"Not departed yet.",inline = True)  
                try:
                    landing_time_real = datetime.fromtimestamp(landing_time_real)
                    landing_time_real = str(landing_time_real.astimezone(ltz_real))            
                    landing_time_real = landing_time_real[:-6]
                    embed.add_field(name="Time of Arival(Real)", value=f"{landing_time_real}({flight.destination_airport_timezone_abbr})", inline=True)
                except:
                    
                    embed.add_field(name="Time of Arival(Real)", value=f"Not landed yet.", inline=True)
                embed.add_field(name = "‎",value = "‎",inline = True)

                # GET AIRCRAFT IMAGE

                values_view = flight.aircraft_images.values()
                value_iterator = iter(values_view)
                first_value = next(value_iterator)
                image_dict = first_value[0]
                aircraft_image = (image_dict.get("src"))
                copy_right = (image_dict.get("copyright"))
                embed.set_footer(text = f"Photo credit: {copy_right} \nFor more flight information please visit: https://www.flightradar24.com/{flight.callsign}/{flight.id}")
                embed.set_image(url = aircraft_image)

                # SEND EMBED

                await interaction.response.send_message(embed=embed)
                flights = True  

        # IF FLIGHT IS NOT FOUND
            
        if flights == False:
            await  interaction.response.send_message(content = "Sorry, I could not find your flight. \nPlease visit https://www.flightradar24.com/ to find the flight manually. ")

    except:
        for flight in fr_api.get_flights(callsign.upper()):
            if flight.check_info(callsign=plane.upper()):     
                await interaction.send_message(f"Sorry, an error occured and I could not provide details regarding the flight. Please visit https://www.flightradar24.com/{flight.callsign}/{flight.id} for flight information.")


# RUN BOT

client.run(token)