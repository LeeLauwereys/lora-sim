#Berekening voor de  simulator
from math import ceil
#import math
import numpy as np
from scipy.stats import norm

Boltzmann = 1.380649e-23   # J/K

def symbooltijd(sf, bb):
    symbool_tijd = (2**sf)/(bb*1000)
    return symbool_tijd

def preambleduur(n_preamble, symbool_tijd):
    preambletijd = (n_preamble + 4.25) * symbool_tijd
    return preambletijd

def payload_sym(pl, sf, CRC, H, CR, DE):
    payload_symbool = 8 + max(ceil((8*pl - 4*sf + 28 +16*CRC - 20*H)/(4*(sf - 2*DE)) )*(CR + 4),0)

    return payload_symbool

def payloadduur(payload_symbool, symbool_tijd):
    payloadtijd = payload_symbool * symbool_tijd
    return payloadtijd

def pakketduur(preambletijd, payloadtijd):
    pakkettijd = preambletijd + payloadtijd
    return pakkettijd

def beschikbare_energie(budget, efficientie):
    return budget * efficientie

def vermogen_transmissie(spanning, stroom):
    return spanning * stroom

def energie_transmissie(vermogen_transmissie, pakketduur):
    return vermogen_transmissie * pakketduur

def p_ontvangen(p_tx, PL):
    return p_tx - PL

OMGEVING = {    #data komt uit de (tabel 4) # Characterization of LoRa Point-to-Point Path-Loss:Measurement Campaigns and Modeling Considering Censored Data (Gilles Callebaut & Liesbet Van der Perre)
    "Stedelijk":    {"pl_d0": 74.85, "n": 2.75, "sigma": 11.25},        #ML schatting
    "Kust":  {"pl_d0": 43.96, "n": 3.62, "sigma": 27.51},
    "Bosrijk": {"pl_d0": 95.52, "n": 2.03, "sigma": 6.87},
}

def shadowing(sigma):
    return np.random.normal(0, sigma) # normaalverdeling


def pathloss(pl_d0, n, d, chi=0.0, d0 = 1.0 ): #G. Callebaut paper
    return pl_d0 + 10 * n * np.log10(d / d0) + chi

RSS_MIN = {7: -123, 8: -126, 9: -129, 10: -132, 11: -133, 12: -136} #G. Callebaut paper tabel 1


def pl_drempel(p_tx, sf):
    return p_tx - RSS_MIN[sf]          # maximaal path loss dat nog gedemoduleerd wordt

def per(pl_m, pl_th, sigma):
    return 100 * (1 - norm.cdf((pl_th - pl_m) / sigma))     # in %


SNR_MIN = {7: -7.5, 8: -10, 9: -12.5, 10: -15, 11: -17.5, 12: -20}   # (waardes voor @125kHz bandbreedte) data komt van Tabel 1 van Characterization of LoRa Point-to-Point Path-Loss:Measurement Campaigns and Modeling Considering Censored Data (Gilles Callebaut & Liesbet Van der Perre)

def ruisvloer(bb, T, nf=7.0):           #uit datasheet van stm RSSI and SNR for LoRa® modulation on STM32WL5x/Ex microcontrollers
    return 10 * np.log10(Boltzmann * T * 1000) + 10 * np.log10(bb*1000) + nf    #met DB_@1Hz = 1            #*1000 om naar miliwatt om te zetten (dBm)


