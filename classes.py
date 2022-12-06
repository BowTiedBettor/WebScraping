import asyncio
import websockets
import json
import pandas as pd
import time
from datetime import datetime
import smtplib
import requests

"""
Example of how to build a proper scraper for a horse racing website
"""

async def getidsdata(uri, sportid=36):
    ws = await websockets.connect(uri)
    try:
        await ws.send(
            json.dumps(
                {"jsonrpc": "2.0", "params": {"ids": [f"{sportid}"]}, "method": "GetLeaguesBySportId", "meta": {
                    "blockId": "html-container-Center_LeagueListResponsiveBlock_16322"}, "id": "383b30bc-ed3e-423f-b172-1e8abf2737fb"}
            )
        )
        result = await ws.recv()
        close_ws = await ws.close()
        result_dict = json.loads(result)
        return result_dict

    except:
        raise Exception("bla bla bla")


async def getoddsdata(uri, id_):
    ws = await websockets.connect(uri)
    try:
        await ws.send(
            json.dumps(
                {"jsonrpc": "2.0", "params": {"eventState": "Mixed", "eventTypes": ["Outright"], "pagination": {"top": 100, "skip": 0}, "ids": [f"{id_}"]}, "method": "GetEventsByLeagueId", "meta": {
                    "blockId": "outRights-html-container-Center_LeagueViewResponsiveBlock_15984Center_LeagueViewResponsiveBlock_15984"}, "id": "734712ee-314b-4351-ba6f-3026aa1e24f2"}
            )
        )
        result = await ws.recv()
        close_ws = await ws.close()
        result_dict = json.loads(result)
        return result_dict

    except:
        raise Exception("bla bla bla")
       
class Bookie:
    def __init__(self):
        """
        """
        self.generate_uri()

    def generate_uri(self):
        headers = {}

        response = requests.post("https://...", headers=headers).json()
        jwt = response['jwt']
        uri = f"wss://...?jwt={jwt}..."
        self.uri = uri

    def getids(self, bana: str, från_lopp: int, till_lopp: int) -> list:
        """
        """
        try:
            data = asyncio.run(getidsdata(self.uri, 36))

            id_list = []
            if isinstance(från_lopp, int):
                for i in range(från_lopp, till_lopp + 1):
                    for spelobjekt in data['result']['leagues']:
                        if bana in spelobjekt['name'] and str(i) in spelobjekt['name']:
                            id_list.append(spelobjekt['id'])
                            break
            else:
                for spelobjekt in data['result']['leagues']:
                    if bana in spelobjekt['name']:
                        id_list.append(spelobjekt['id'])
                        break

            if id_list:
                return id_list

            else:
                raise Exception("bla bla bla")

        except Exception as e:
            print("Information:", repr(e))
            return e

    def scrape_vp(self, bana: str, lopp: list = None, outrightmarknad: bool = False):
        """
        Scrapes win and top 3 markets
        """
        pd_lista = []

        if not outrightmarknad:
            id_list = self.getids(
                bana=bana, från_lopp=lopp[0], till_lopp=lopp[1])
        else:
            id_list = self.getids(bana=bana, från_lopp="", till_lopp="")

        for objid in id_list:
            lopp_df = pd.DataFrame(
                columns=["Startnr", "Häst", "VOdds", "POdds"])

            try:
                data = asyncio.run(getoddsdata(self.uri, int(objid)))

                for market in data['result']['markets']:
                    if "Vinnare" in market['name']:
                        v_selections = market['selections']

                    if "Topp 3" in market['name']:
                        p_selections = market['selections']

                for v_data in v_selections:
                    try:
                        startnummer = int(v_data['name'].split(" ")[0])
                    except:
                        startnummer = 0
                    hästnamn = v_data['name']
                    vodds = round(v_data['trueOdds'], 2)
                    for p_data in p_selections:
                        if hästnamn == p_data['name'][3:]:
                            podds = round(p_data['trueOdds'], 2)
                            break

                    dummy_df = lopp_df
                    ny_rad = pd.DataFrame(
                        [[startnummer, hästnamn, vodds, podds]], columns=lopp_df.columns)
                    lopp_df = pd.concat(
                        [dummy_df, ny_rad], ignore_index=True)

            except Exception as e:
                print("bla bla bla") 
                print("Information:", repr(e))

            sorted_df = lopp_df.sort_values(by="Startnr")
            pd_lista.append(sorted_df)

        return pd_lista

    def scrape_h2h(self, bana: str, lopp: list = None, outrightmarknad: bool = False):
        """
        Scrapes the H2H-markets
        """
        pd_lista = []

        if not outrightmarknad:
            id_list = self.getids(
                bana=bana, från_lopp=lopp[0], till_lopp=lopp[1])
        else:
            id_list = self.getids(bana=bana, från_lopp="", till_lopp="")

        for objid in id_list:
            try:
                data = asyncio.run(getoddsdata(self.uri, int(objid)))

                for market in data['result']['markets']:
                    if "H2H" in market['name']:
                        h2h_selections = market['selections']

                        h2h_df = pd.DataFrame(
                            columns=["Startnr", "Häst", "H2H-odds"])

                        for h2h_data in h2h_selections:
                            try:
                                startnr = int(h2h_data['name'].split(" ")[0])
                            except:
                                startnr = 0
                            hästnamn = h2h_data['name']
                            h2hodds = round(h2h_data['trueOdds'], 2)

                            dummy_df = h2h_df
                            ny_rad = pd.DataFrame(
                                [[startnr, hästnamn, h2hodds]], columns=h2h_df.columns)
                            h2h_df = pd.concat(
                                [dummy_df, ny_rad], ignore_index=True)

                        sorted_df = h2h_df.sort_values(by="Startnr")
                        pd_lista.append(sorted_df)

            except Exception as e:
                print("bla bla bla") 
                print("Information:", repr(e))

        return pd_lista

    def awaitnewodds(self, bana: str, lopp: list, delta: int):
        """
        Awaits new odds, could be done by awaiting the information from the WebSocket [the whole purpose of the protocolf lol]
        but doesn't matter in practice
        """
        while True:
            try:
                ids = self.getids(
                    bana=bana, från_lopp=lopp[0], till_lopp=lopp[1])
                if isinstance(ids, websockets.exceptions.InvalidStatusCode):
                    print(datetime.now())
                    print("Update URI and try again")
                    print("")
                    self.generate_uri()
                    time.sleep(delta)
                    continue
                if isinstance(ids, list) and len(ids) > 0:
                    print("New odds just dropped")
                    return True
                else:
                    raise Exception
            except:
                print(datetime.now())
                print("...")
                print("")
                time.sleep(delta)
                continue

    def send_mail(self, recipients: list, bana: str, market: str, lopp: list = None, outrightmarknad: bool = False):
        """
        """
        if market == "h2h":
            try:
                result = self.scrape_h2h(
                    bana=bana, lopp=lopp, outrightmarknad=outrightmarknad)
            except:
                print("")
                print("bla bla bla")
                result = None
        elif market == "vp":
            try:
                result = self.scrape_vp(
                    bana=bana, lopp=lopp, outrightmarknad=outrightmarknad)
            except:
                print("")
                print("bla bla bla")
                result = None

        if result:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(EMAIL_ADDRESS, EMAIL_PASS)

                subject = ""
                body = ""
                for res in result:
                    body += str(res) + "\n" + "\n"

                msg = f"Subject: {subject}\n\n{body}".encode('utf-8')

                for recipient in recipients:
                    smtp.sendmail(EMAIL_ADDRESS, recipient, msg)

    def to_excel(self, path: str):
        pass
