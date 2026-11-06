import streamlit as st
from berekeningen import *
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import pandas as pd
import altair as alt     

import plotly.graph_objects as go #voor de zone

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





    # HEATMAP (interactief, transparante achtergrond)
    st.header("Bereik rond de zender")

    max_straal = st.slider("Maximale afstand tot de zender [m]", min_value=100, max_value=2000, value=500, step=50)


    # raster over het vierkant [-max_straal, max_straal]²
    N = 200
    as_waarden = np.linspace(-max_straal, max_straal, N)
    X, Y = np.meshgrid(as_waarden, as_waarden)

    # afstand tot de zender (minimaal d0, anders log10(0))
    r = np.maximum(np.sqrt(X**2 + Y**2), d0)

    # zelfde functies als eerder, nu voor het hele raster (chi = 0)
    pl_h = pathloss(pl_d0, n, r)
    rssi_h = p_ontvangen(p_tx, pl_h)
    snr_h = rssi_h - ruisvloer(bb, temperatuur)
    per_h = per(pl_h, pl_drempel(p_tx, sf), sigma)

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        x=as_waarden,
        y=as_waarden,
        z=per_h,
        zmin=0, zmax=100,
        colorscale="RdYlGn_r",
        zsmooth="best",                       # vloeiend vlak, geen cellen
        colorbar=dict(title="PER [%]"),
        customdata=np.dstack([r, rssi_h, snr_h]),
        hovertemplate=(
            "Afstand: %{customdata[0]:.0f} m<br>"
            "RSSI: %{customdata[1]:.1f} dBm<br>"
            "SNR: %{customdata[2]:.1f} dB<br>"
            "PER: %{z:.1f} %<extra></extra>"
        ),
    ))

    
    for niveau in (10, 50, 90):
            fig.add_trace(go.Contour(
                x=as_waarden, y=as_waarden, z=per_h,
                contours=dict(start=niveau, end=niveau, size=1,
                              coloring="lines", showlabels=True,
                              labelformat=".0f", labelfont=dict(size=11)),
                line=dict(color="rgba(0,0,0,0.6)", width=1.5),
                showscale=False,
                hoverinfo="skip",
            ))

    # zender in het midden
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers", name="Zender",
        marker=dict(size=10, color="white", line=dict(color="black", width=2)),
        hovertemplate="Zender<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        width=700, height=650,
        paper_bgcolor="rgba(0,0,0,0)",        # transparante achtergrond
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="x [m]", range=[-max_straal, max_straal], constrain="domain"),
        yaxis=dict(title="y [m]", range=[-max_straal, max_straal],
                   scaleanchor="x", scaleratio=1),   # vierkant
    )

    st.plotly_chart(fig, use_container_width=False)

    st.markdown(
        "- **RSSI (dBm):** het ontvangen vermogen. Hoe negatiever, hoe zwakker het signaal.\n"
        "- **SNR (dB):** hoeveel het signaal boven (positief) of onder (negatief) de ruisvloer ligt. LoRa kan nog ontvangen bij een negatieve SNR.\n"
        "- **PER (%):** de kans dat een pakket niet aankomt. Hoe roder, hoe minder pakketten aankomen.\n"
        "- **Zone:** het model heeft geen richting, dus de waardes gelden in alle richtingen rond de zender (het witte punt)."
    )
