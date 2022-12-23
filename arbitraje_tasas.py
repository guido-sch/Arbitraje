"""
    1- Librerias, definicion de variables y funciones
    2- Inicializacion del entorno
    3- Deficinion del handler que va a recibir la informacion por websocket
    4- Inicializacion del Websocket Connection
    5- Subscripcion para recibir la informacion de mercado
    6- (comentado) Testeo si se recibe informacion de ordenes
v1 - 21 12 2022 - Guido Schifani - primer draft    
v2 - 22 12 2022 - Guido Schifani - se agrego 
                        1) unittest
                        2) envio de ordenes
"""


# 1- librerias
import pyRofex
from datetime import datetime, timedelta
import time
import unittest
global instruments2
import yfinance as yf
import pandas as pd
import numpy as np


#relacion entre ticker de futuros (remarket) y de sus underlying (yfinance)
instruments2 = {"YPFD/FEB23":"YPFD.BA",
                "GGAL/FEB23":"GGAL.BA",
                "PAMP/FEB23":"PAMP.BA",
                "DLR/FEB23":"ARS=X"
                }
#futuros
instruments = list(instruments2.keys())


#tabla donde se van a guardar las tasas implicitas
df1 = pd.DataFrame(index=instruments,
                   columns=["BID","OFFER"])

#tabla donde se van a guardar los spread de tasas implicitas
df2 = pd.DataFrame(index=instruments,
                   columns=instruments)
df2.columns.name = 'Fondeo\Coloco'

#tabla donde se van a guardar las oportunidades de arbitraje
df3 = pd.DataFrame(index=instruments,
                   columns=instruments)
df3.columns.name = 'Fondeo\Coloco'


# Funcion para tomas los valores spot en yfinance
def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

#calculo de TNA
def tasa_implicita(futuro,spot,fecha_hoy,fecha_vto):
    """
    Determinación de la tasa implícita al día del vencimiento
    del futuro, considerando el precio del spot
    inputs:
        Cotización del Futuro
        Precio del Spot
        Fecha del día (datetime)
        Fecha del Vto (datetime)
    """
    if spot is None or futuro == float('nan'):
        tasa_implicita = float('nan')
    elif futuro is None or  futuro == float('nan'):
        tasa_implicita = float('nan')
    else:
        tasa_implicita = (futuro - spot)/spot *365/(fecha_vto - fecha_hoy).days       
    return round(tasa_implicita*100,2)


class Unittest(unittest.TestCase):

    def test(self):
        ImpRate = tasa_implicita(2,1,datetime.today(),datetime.today()+timedelta(days=2))
        self.assertEqual(ImpRate, 18250)


unittest.main()

# 2-Inicializacion del entorno
pyRofex.initialize(user="guidoschifani7690",
                   password="rbazfW9@",#Alma@1234
                   account="REM7690",
                   environment=pyRofex.Environment.REMARKET)


# 3- Deficinion del handler que va a recibir la informacion por websocket
def market_data_handler(message):

    instr = message["instrumentId"]["symbol"] #instrumento
    bi = message["marketData"]["BI"][0]['price'] #bid del instrumento
    of = message["marketData"]["OF"][0]['price'] #offer del instrumento   
    la = get_current_price(instruments2[instr]) #spot en yfinance

    hoy=datetime.today()
    mat=datetime.strptime(pyRofex.get_instrument_details(ticker = instr)["instrument"]["maturityDate"], "%Y%m%d") + timedelta(hours=23,minutes=59,seconds=59)
    TNA_BI = tasa_implicita(bi,la,hoy,mat)
    TNA_OF = tasa_implicita(of,la,hoy,mat)
    
    df1.loc[instr]['BID']=TNA_BI
    df1.loc[instr]['OFFER']=TNA_OF
    
    print(instr)
    if bi and of and la:
        print("Tasa BID:   ", str(TNA_BI) , "% - ", bi)
        # print(("Tasa tomadora: " + '\t' + str(TNA_BI) +  '%').expandtabs(5))
        print("Tasa OFFER: ", str(TNA_OF), "% - ", of)
        print("Spot:           ", la)
        # print(("Tasa colocadora: " + '\t' + str(TNA_OF) +  '%').expandtabs(5))
        if bi>of:
            print(" ")
        else:
            print(" ")
        print("___________")
    else:
        "Missing BID OF or LA value"  
    
    
    #si tenemos todas las tases, se calcula la oportunidad de arbitraje
    check_nan = df1.isnull().values.any()
    if check_nan:
        print("Construyendo tabla")
    else:
        print("############################################################")     
        print("Tabla con tasas implicitas")
        print(df1)
    
        for i in instruments:
            for j in instruments:
                df2.loc[j][i]=df1.loc[i]['BID']-df1.loc[j]['OFFER']
                if df2.loc[j][i]>0:
                    df3.loc[j][i]="Arbitraje"
                else:
                    df3.loc[j][i]="NO Arbitraje"
    
        print("############################################################")
        print("Tablas de spreads")
        print(df2)    
        print("############################################################")
        print("Tabla con evaluacion de arbitraje")
        print(df3)   
        print("############################################################") 
        gs=df2.stack().index[np.argmax(df2.values)]
        print("La mejor estrategia es fondar en "+gs[0]+" y colocar en "+gs[1])
    
    

def error_handler(message):
    print("Error Message Received.")#+str(message["instrumentId"]["symbol"]))
    # print("Error Message Received: {0}".format(message))

def exception_handler(e):
    print("Exception Occurred.")#+str(e["instrumentId"]["symbol"]))
    # print("Exception Occurred: {0}".format(e.msg))

# 4- Inicializacion del Websocket Connection
pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                  error_handler=error_handler,
                                  exception_handler=exception_handler)


# 5- Subscripcion para recibir la informacion de mercado
# Entries que se van a tener en cuenta (BIDS, OFFERS, LAST)
entries = [pyRofex.MarketDataEntry.BIDS,
           pyRofex.MarketDataEntry.OFFERS,
           pyRofex.MarketDataEntry.LAST]

# subscripcion a los intrumentos definidos arriba
print("############################################################")
print("Subscripcion a los siguientes productos"+str(instruments))
print("############################################################")
pyRofex.market_data_subscription(tickers=instruments,
                                 entries=entries)

    
# # 6- Testeo si se recibe informacion de ordenes
# time.sleep(3)
# print("############################################################")
# print("Se espera 3 segundos y se lanza una orden de compra de "+str(instruments[0]))
# print("############################################################")
# time.sleep(5)


# pri=pyRofex.get_market_data(instruments[0])['marketData']['OF'][0]['price']
# gs=pyRofex.send_order(instruments[0],price=pri-1, size=100, order_type=pyRofex.OrderType.LIMIT, side=pyRofex.Side.SELL)
# order_status=pyRofex.get_order_status(gs['order']['clientId'])['order']['status']
# print("Order ",order_status)


time.sleep(1000)

# Se cierra la conexion 
pyRofex.close_websocket_connection()
