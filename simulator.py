import streamlit as st
from berekeningen import *
#import matplotlib.pyplot as plt
#from matplotlib.patches import Circle
import pandas as pd
import altair as alt     

st.set_page_config(layout="wide")

st.title("One-time transmission LoRa Sim")


#constanten
d0 = 1 # Characterization of LoRa Point-to-Point Path-Loss:Measurement Campaigns and Modeling Considering Censored Data (Gilles Callebaut & Liesbet Van der Perre)


links, rechts = st.columns([1, 2])

with links:
    st.header("LoRa instellingen")
    sf = st.slider(
        "Spreading Factor",     # tijdsduur van een symbool
        min_value=7,
        max_value=12,
        value=7,
    )

    # bb = st.slider(              #afhankelijk van de gekozen LoRa-chip (alle mogelijke keuze)
    #     "Bandbreedte [kHz]",
    #     min_value=7.8,
    #     max_value=500.0,
    #     value=7.8,
    # )
    bb = st.select_slider(
    "Bandbreedte [kHz]",
    options=[7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125, 250, 500], #vaste instelbare keuzes
    value=125,
)

    st.write("De berekende symbooltijd is:", round (symbooltijd(sf, bb)* 1000, 3), "ms")

    n_preamble = st.slider(              #lengte van de preamble is afhankelijk van de gekozen LoRa-chip
        "Preamble lengte",
        min_value=0,            
        max_value=20,
        value=8,
    )

    st.write("De berekende preambletijd is:", round(preambleduur(n_preamble, symbooltijd(sf, bb)) * 1000, 3), "ms")

    st.header("Pakket")

    pl = st.slider(
        "payload lengte in bytes",     
        min_value=0,
        max_value=255,
        value=0,
    )

    header_keuze = st.radio(
        "Wil je een header gebruiken?",
        ["enable header", "disable header"],
        index=0,
    )

    H = 0 if header_keuze == "enable header" else 1 # H = 0: header aan, H = 1: geen header

    CRC_keuze = st.radio(
        "Wil je een CRC gebruiken?",
        ["enable CRC", "disable CRC"],
        index=0,
    )

    CRC = 0 if CRC_keuze == "disable CRC" else 1 #

    CR_keuze = st.selectbox(
        "Code rate keuze",
        ("4/5", "4/6", "4/7","4/8"),
    )
    CR = (1  if CR_keuze == "4/5"                  #of gebruik maken van een dictionary
    else 2 if  CR_keuze == "4/6" 
    else 3 if  CR_keuze == "4/7" 
    else 4)                                     
    st.write("Je kiest voor:", CR, "extra redundantiebits")


    DE_keuze = st.radio(
        "Wil je een DE (low data rate optimization) gebruiken?",
        ["enable DE", "disable DE"],
        index=0,
    )
    DE = 0 if DE_keuze == "disable DE" else 1 # 

    st.write("De aantal payload symbolen (alles behalve de preamble) zijn:", payload_sym(pl, sf, CRC, H, CR, DE) , "symbolen")


    st.write("De duur van de payload wordt dan", round(payloadduur(payload_sym(pl, sf, CRC, H, CR, DE), symbooltijd(sf, bb))*1000,3) , "ms")

    t_preamble = preambleduur(n_preamble, symbooltijd(sf, bb))
    t_payload = payloadduur(payload_sym(pl, sf, CRC, H, CR, DE), symbooltijd(sf, bb))

    pakketduur_ = (pakketduur(t_preamble, t_payload))
    st.write("De time on air, of pakket duratie is:", round(pakketduur_*1000,3), "ms")
    
    st.header("Energie")

    spanning = st.slider(              #chip afhankelijk
        "Spanning [V]",
        min_value=0.0,            
        max_value=5.0,
        value=0.0,
    )
    stroom = st.slider(              #chip afhankelijk (wat ivm sleep stroom)
        "Stroom tijdens transmissie [mA]",
        min_value=0,            
        max_value=500,
        value=0,
    )

    st.write("Het gebruikt vermogen voor een transmissie is:", round(vermogen_transmissie(spanning, stroom)/1000, 3), "W") #moet dit het maximaal vermogen en minimaal vermogen zijn?

    vermogentransmissie = vermogen_transmissie(spanning, stroom/1000)


    st.write("Het gebruikt energie voor een transmissie is:", round(energie_transmissie(vermogentransmissie, pakketduur_)*1000, 3), "mJ") 



    energiebudget = st.slider(              #chip afhankelijk
        "Energiebudget [mJ]",  
        min_value=0,            
        max_value=500,
        value=0,
    )

    efficientie = st.slider(              #chip afhankelijk
        "efficientie [%]",
        min_value=0,            
        max_value=100,
        value=0,
    )

    st.write("Het beschikbaar energie voor een transmissie is:", round(beschikbare_energie(energiebudget, efficientie)/100, 3), "mJ")
    e_tx = round(energie_transmissie(vermogentransmissie, pakketduur_)*1000, 3)
    e_beschikbaar = round(beschikbare_energie(energiebudget, efficientie)/100, 3)

    if e_tx <= e_beschikbaar:                               #eventueel een tabel voor overzicht. Eventueel een marge, en de twee energie's tonen naast elkaar
        st.markdown(":green[Past binnen het budget]")
    else:
        st.markdown(":red[Past niet binnen het budget]")



    st.header("Pathloss")


    p_tx = st.slider("Zendvermogen [dBm]",  #afhankelijk van de chip
                      min_value=-4,
                       max_value=20,
                         value=14)        #zendvermogen

    omgeving = st.radio(
        "Omgeving (@1,5m, 868MHz, 125KHz bandbreedte, ...)",
        list(OMGEVING.keys()),
        index=0,
    )

    pl_d0 = OMGEVING[omgeving]["pl_d0"]
    n     = OMGEVING[omgeving]["n"]
    sigma = OMGEVING[omgeving]["sigma"]


    d = st.slider(
        "Afstand tussen zender en ontvanger [m]",  #dit weglaten voor de grafiek te kunnen maken 
        min_value=1,
        max_value=2000,
        value=1)        

    chi = shadowing(sigma)                  
    pl = pathloss(pl_d0, n, d)                         
    st.write("Het pathloss is:", round(pl,3), "dB") 

    rssi = p_ontvangen(p_tx, pl) #P_rx berekenen (P_tx en PL)
    st.write("De RSSI received signal strength indicator (ontvangen vermogen) is:", round(rssi, 3), "dBm")



    temperatuur = st.slider(           #omgevingstemperatuur (later eventueel de temperatuur van de chip toevoegen)
        "Omgevingstemperatuur [K]",
        min_value=233,            
        max_value=320,
        value=290,
    )

    st.write("de ruisvloer (noise) is:", round(ruisvloer(bb, temperatuur ),3), "dBm")








with rechts:

#     #WAARDES VOOR GRAFIEK aan te maken
#     afstanden = np.arange(1, 2001) 
#     pl_lijst = pathloss(pl_d0, n, afstanden) #wel nog opletten want telkens hier een waarde veranderd zal de  normaal verdeling wijzigen denk ik... als chi =0.0 dan wint de standaardnormale zal deze de waarde vervangen
#     #pl_lijst = pathloss(pl_d0, n, afstanden, chi) #lag?
#     rssi_lijst = p_ontvangen(p_tx, pl_lijst)
#     st.header("Grafieken")
#     st.write("RSSI (dBm) ifv afstand (m)")
    
#     st.line_chart({"RSSI [dBm]": rssi_lijst}, x_label="Afstand [m]", y_label="RSSI [dBm]")


#     snr_lijst = rssi_lijst - ruisvloer(bb, temperatuur)
#     st.write("SNR (dB) ifv afstand (m)")
#     st.line_chart({"SNR [dB]": snr_lijst}, x_label="Afstand [m]", y_label="SNR [dB]")


#     pl_th = pl_drempel(p_tx, sf)
#     per_lijst = per(pl_lijst, pl_th, sigma)
    
#     #debug
#     # pl_gem = pathloss(pl_d0, n, d)
#     # pl_th_d = pl_drempel(p_tx, sf)
#     # per_d = per(pl_gem, pl_th_d, sigma)
#     # st.write(f"Gemiddeld path loss: {pl_d0} + 10·{n}·log10({d}) = {pl_gem:.2f} dB")
#     # st.write(f"Drempel: {p_tx} − ({RSS_MIN[sf]}) = {pl_th_d} dB")
#     # st.write(f"PER = 1 − Φ(({pl_th_d} − {pl_gem:.2f}) / {sigma}) ≈ {per_d:.1f} % (dus PRR ≈ {100 - per_d:.1f} %)")

#     st.write(" PRR (%) versus afstand (m) ")
#     st.line_chart({"PER [%]": per_lijst}, x_label="Afstand [m]", y_label="PER [%]")




    # # CIRKELGRAFIEK (Streamlit-native)
    # st.header("Bereik rond de zender")

    # stap = st.slider("Afstand tussen de cirkels [m]", min_value=100, max_value=500, value=250, step=50)
    # max_straal = 2000
    # stralen = np.arange(stap, max_straal + 1, stap)

    # # waardes per straal (zelfde functies als bij de lijngrafieken, chi = 0)
    # pl_r = pathloss(pl_d0, n, stralen)
    # rssi_r = p_ontvangen(p_tx, pl_r)
    # snr_r = rssi_r - ruisvloer(bb, temperatuur)
    # per_r = per(pl_r, pl_drempel(p_tx, sf), sigma)

    # # elke cirkel = veel punten op gelijke afstand van de zender
    # hoeken = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    # rijen = []
    # for r, per_v in zip(stralen, per_r):
    #     rijen.append(pd.DataFrame({
    #         "x [m]": r * np.cos(hoeken),
    #         "y [m]": r * np.sin(hoeken),
    #         "PER [%]": round(float(per_v), 1),
    #     }))
    # rijen.append(pd.DataFrame({"x [m]": [0.0], "y [m]": [0.0], "PER [%]": [0.0]}))   # zender in het midden
    # df_cirkels = pd.concat(rijen, ignore_index=True)

    # st.scatter_chart(df_cirkels, x="x [m]", y="y [m]", color="PER [%]",
    #                  size=20, width=650, height=650)

    # # waardes per ring in een tabel
    # df_tabel = pd.DataFrame({
    #     "Afstand [m]": stralen,
    #     "RSSI [dBm]": np.round(rssi_r, 1),
    #     "SNR [dB]": np.round(snr_r, 1),
    #     "PER [%]": np.round(per_r, 1),
    # })
    # st.dataframe(df_tabel, hide_index=True)

    # st.markdown(
    #     "- **RSSI (dBm):** het ontvangen vermogen. Hoe negatiever, hoe zwakker het signaal.\n"
    #     "- **SNR (dB):** hoeveel het signaal boven (positief) of onder (negatief) de ruisvloer ligt. LoRa kan nog ontvangen bij een negatieve SNR.\n"
    #     "- **PER (%):** de kans dat een pakket niet aankomt. De kleur van de cirkel toont dit: hoe hoger, hoe minder pakketten aankomen.\n"
    #     "- **Cirkels:** zelfde afstand tot de zender (het punt in het midden). Het model heeft geen richting, dus de waardes gelden in alle richtingen."
    # )



    # CIRKELGRAFIEK
    st.header("Bereik rond de zender")

    stap = st.slider("Afstand tussen de cirkels [m]", min_value=10, max_value=500, value=250, step=10)
    max_straal = st.slider("Maximale afstand [m]", min_value=100, max_value=2000, value=250, step=50)
    stralen = np.arange(stap, max_straal + 1, stap)

    # waardes per straal (zelfde functies als bij de lijngrafieken, chi = 0)
    pl_r = pathloss(pl_d0, n, stralen)
    rssi_r = p_ontvangen(p_tx, pl_r)
    snr_r = rssi_r - ruisvloer(bb, temperatuur)
    per_r = per(pl_r, pl_drempel(p_tx, sf), sigma)

    # elke cirkel = een gesloten lijn door veel punten op gelijke afstand van de zender
    hoeken = np.linspace(0, 2 * np.pi, 181)
    rijen = []
    for r, rssi_v, snr_v, per_v in zip(stralen, rssi_r, snr_r, per_r):
        rijen.append(pd.DataFrame({
            "x": r * np.cos(hoeken),
            "y": r * np.sin(hoeken),
            "hoek": hoeken,
            "afstand": int(r),
            "rssi": round(float(rssi_v), 1),
            "snr": round(float(snr_v), 1),
            "per": round(float(per_v), 1),
        }))
    df_cirkels = pd.concat(rijen, ignore_index=True)

    assen = alt.Scale(domain=[-max_straal, max_straal])

    ringen = alt.Chart(df_cirkels).mark_line(strokeWidth=3).encode(
        x=alt.X("x:Q", title="x [m]", scale=assen),
        y=alt.Y("y:Q", title="y [m]", scale=assen),
        order="hoek:Q",
        detail="afstand:N",
        color=alt.Color("per:Q", title="PER [%]",
                        scale=alt.Scale(scheme="redyellowgreen", reverse=True, domain=[0, 100])),
        tooltip=[
            alt.Tooltip("afstand:Q", title="Afstand [m]"),
            alt.Tooltip("rssi:Q", title="RSSI [dBm]"),
            alt.Tooltip("snr:Q", title="SNR [dB]"),
            alt.Tooltip("per:Q", title="PER [%]"),
        ],
    )

    zender = alt.Chart(pd.DataFrame({"x": [0], "y": [0]})).mark_point(
        filled=True, color="white", size=80
    ).encode(x="x:Q", y="y:Q")

    st.altair_chart((ringen + zender).properties(width=600, height=600),
                    use_container_width=False)

    # waardes per ring in een tabel
    df_tabel = pd.DataFrame({
        "Afstand [m]": stralen,
        "RSSI [dBm]": np.round(rssi_r, 1),
        "SNR [dB]": np.round(snr_r, 1),
        "PER [%]": np.round(per_r, 1),
    })
    st.dataframe(df_tabel, hide_index=True)

    st.markdown(
        "- **RSSI (dBm):** het ontvangen vermogen. Hoe negatiever, hoe zwakker het signaal.\n"
        "- **SNR (dB):** hoeveel het signaal boven (positief) of onder (negatief) de ruisvloer ligt. LoRa kan nog ontvangen bij een negatieve SNR.\n"
        "- **PER (%):** de kans dat een pakket niet aankomt. De kleur van de cirkel toont dit: hoe hoger, hoe minder pakketten aankomen.\n"
        "- **Cirkels:** zelfde afstand tot de zender (het punt in het midden). Het model heeft geen richting, dus de waardes gelden in alle richtingen."
    )
