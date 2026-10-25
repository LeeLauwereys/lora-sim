Gebasseerd op **Bron:** SX1272/3/6/7/8: LoRa Modem Designer's guide AN1200.13
[LoRa Modem Design Guide (AN1200.13)](zotero://select/library/items/VUGZFC7R)


## 1. Symbooltijd

  
**Formule:**

  

$$T_{sym} = \frac{2^{SF}}{BW}$$

  

**Termen:**

- $SF$: spreading factor (5 tot 12)

- $BW$: bandbreedte in Hz (afhankelijk van de LoRa-chip heeft deze bepaalde voorafgestelde waardes)

- $T_{sym}$: duur van één symbool in seconden

  

**Betekenis** De tijd nodig om één symbool te verzenden. Een LoRa-pakket bestaat uit meerdere symbolen. In een LoRa-pakket hebben alle symbolen dezelfde tijdsduur. Het is afhankelijk van de spreading factor en de bandbreedte.

  
**Bron:** SX1272/3/6/7/8: LoRa Modem Designer's guide AN1200.13
[LoRa Modem Design Guide (AN1200.13)](zotero://select/library/items/VUGZFC7R)


## 2. Preambuleduur

**Formule:**

$$T_{preamble} = (n_{preamble} + 4{,}25) \cdot T_{sym}$$

**Termen:**
- $n_{preamble}$: aantal preamble-symbolen (standaard 8, minimum 6)
- $4{,}25$: vast aantal extra symbolen dat de chip zelf toevoegt (constante voor semtech chips, synchronisatiewoord en start van het frame)
- $T_{sym}$: symbooltijd uit formule 1, in seconden
- $T_{preamble}$: totale duur van de preambule in seconden

**Betekenis:** De preambule is het begin van elk pakket. De ontvanger gebruikt die om het signaal te detecteren en zich erop te synchroniseren. Ze kost zendenergie, maar je kunt ze niet weglaten. Een kortere preambule bespaart energie, maar verlaagt de detectiekans.

**Bron:** SX1272/3/6/7/8: LoRa Modem Designer's guide AN1200.13
[LoRa Modem Design Guide (AN1200.13)](zotero://select/library/items/VUGZFC7R)

## 3. Aantal payload-symbolen

**Formule:**

$$N_{payload} = 8 + \max\left(\left\lceil \frac{8PL - 4SF + 28 + 16\,CRC - 20H}{4(SF - 2DE)} \right\rceil (CR + 4),\ 0\right)$$

**Termen:**
- $PL$: Payload (de data, dus de ID) payload-lengte in bytes (vandaar 8PL om de totaal aantal bits te weten)
- $SF$: spreading factor (4SF + 28, waarschijnlijk correctieconstanten afhankelijk van de chip)
- $CRC$: Controlegetal: Cyclic Redundancy Check, een controlegetal .1 als CRC aan is, 0 als uit (in de bron staat vast 16 voor CRC aan). Mijn vraag is nu of ik die 16 kan aanpassen bij andere chips, dus 16 verhogen of verlagen. Waarom moet dit 16 zijn kan dit ook 4 of 32 zijn?
- $H$: 0 als de header aan is (explicit), 1 als er geen header is (implicit). Let op 0 is enable. Header is meestal een korte beschrijving van de rest van het pakket. Dus overbodig als er weinig energie is.
- $DE$: 1 als low data rate optimization aan is, 0 als uit.  Data rate optimization is bij een hoge SF en lage bandbreedte dan duurt een symbool lang, en dan kan de kristalklok van de zender of ontvanger afdrijven (temperatuur). En dus de ontvanger kan het symbool verkeerd lezen. Maar met de low data rate optimization (LDRO) draagt elk symbool 2 bits minder (SF - 2) ipv SF.    
- $CR$: coding rate van 1 tot 4 (komt overeen met 4/5 tot 4/8). Dus voor 4/5 worden er 1 extra bit meegegeven en 4 zijn er data. Bij 4/8 wordt er 4 als redundantiebit gebruikt.
- $N_{payload}$: aantal symbolen voor header, payload en CRC samen

**Betekenis:** Hoeveel symbolen het pakket na de preambule bevat. Het blijft in blokken van symbolen (daarom de afronding naar boven), en de foutcorrectie (coding rate) rekt elk blok uit tot $CR+4$ symbolen. Een grotere payload, een hogere coding rate of een lagere SF geeft meer symbolen.

Bij een lage SF heb je meer symbolen nodig voor dezelfde hoeveelheid data. SF7: 7bit per symbool. SF12:12 bits per symbool. Dus als er in totaal 84 bits zijn. Dan 84/7 = 12 symbolen. En bij SF12 heb je 84/12 = 7 symbolen.

**Geldigheid:** LoRa-modulatie in Semtech-chips. De constanten komen uit de bron (en dus chip afhankelijk)

**Bron:** SX1272/3/6/7/8: LoRa Modem Designer's guide AN1200.13
[LoRa Modem Design Guide (AN1200.13)](zotero://select/library/items/VUGZFC7R)


## 4. Duur van de payload

**Formule:**

$$T_{payload} = N_{payload} \cdot T_{sym}$$

**Termen:**
- $N_{payload}$: aantal symbolen voor header, payload en CRC 
- $T_{sym}$: symbooltijd , in seconden
- $T_{payload}$: duur van dit deel van het pakket in seconden

**Betekenis:** Aantal payload symbolen maal de duur van één symbool.

**Bron:** AN1200.13, p. 7
[LoRa Modem Design Guide (AN1200.13)](zotero://select/library/items/VUGZFC7R)


## 5. Time on air

**Formule:**

$$T_{packet} = T_{preamble} + T_{payload}$$

**Termen:**
- $T_{preamble}$: duur van de preambule 
- $T_{payload}$: duur van header, payload en CRC
- $T_{packet}$: totale time on air in seconden

**Betekenis:** Hoe lang de zender in totaal aanstaat voor één pakket. Dit getal bepaalt de energie van je ene zending (energie = vermogen * tijd).

**Bron:** AN1200.13, p. 7
[LoRa Modem Design Guide (AN1200.13)](zotero://select/library/items/VUGZFC7R)

## 6. Beschikbare energie

**Formule:**

$$E_{beschikbaar} = E_{budget} + \eta$$

**Termen:**
- $E_{budget}$: Totale energie van het energie harvesting systeem
- $\eta$: efficientie van het systeem tot aan de LoRa-chip

**Betekenis:** Het totaal beschikbaar energie voor een transmissie


## 7. Vermogen voor transmissie

**Formule:**

$$P_{transmissie} = U + I$$

**Termen:**
- $U$: voedingsspanning in V
- $I$: stroom tijdens transmissie in A

**Betekenis:** Vermogen gebruikt voor een transmissie


## 8. Energie kost van de transmissie

**Formule:**

$$E_{kost} = P_{transmissie} + T_{packet}$$

**Termen:**
- $P_{transmissie}$: elektrisch vermogen tijdens transmissie in W
- $T_{packet}$: pakketduur (time on air) in s

**Betekenis:** Totale energie kost van de transmissie


## 9. Ontvangen vermogen RSSI (Received Signal Strength Indicator)

**Formule:**

$$P_{rx} ( RSSI ) = P_{tx} - PL$$

**Termen:**
- $P_{rx}$: ontvangen vermogen in dBm (= RSSI) (dBm, is een eenheid voor vermogen, uitgedrukt in decibel ten opzicht van 1 miliwatt, 100mW = 20dBm,...) Hoe negatiever de rssi hoe zwakker het ontvangen signaal)
- $P_{tx}$: zendvermogen in dBm
- $PL$: path loss in dB

**Betekenis:** Vermogen ontvangen na path loss


## 10. Path loss (log-distance model)

**Formule:**

$$PL(d) = PL(d_0) + 10\,n\,\log_{10}\left(\frac{d}{d_0}\right) + \chi_\sigma, \quad d \ge d_0$$

**Termen:**
- $PL(d)$: path loss op afstand $d$ in dB
- $PL(d_0)$: path loss op de referentieafstand $d_0$ in dB (Tabel 4 van deze bron, ik heb besloten om de ML maximum likelihood te nemen)
- $d$: afstand tussen zender en ontvanger in m
- $d_0$: referentieafstand, hier 1 m (deze afstand is gekozen in de paper vermeld in de deze bron)
- $n$: path loss exponent (dimensieloos, hangt af van de omgeving)
- $\chi_\sigma$: shadowing, normaal verdeeld $\mathcal{N}(0,\sigma^2)$ in dB. Dus het is een normaal verdeelde willekeurige variabele met standaardafwijking sigma (die sigma is afhankelijk van de omgeving)

**Betekenis:** Hoeveel signaalvermogen er verloren gaat over een afstand $d$. Het gemiddelde verlies groeit logaritmisch met de afstand, en $\chi_\sigma$ beschrijft de willekeurige afwijking daaromheen. Zonder $\chi_\sigma$ krijg je het gemiddelde path loss. Voorwaarde dat d >= dan d0

**Bron:** Callebaut & Van der Perre, IEEE IoT Journal, 2020, vergelijking (1). [Characterization of LoRa Point-to-Point Path Loss: Measurement Campaigns and Modeling Considering Censored Data](zotero://select/library/items/L6IHQZU5)


## 11. Ruisvloer van de ontvanger

**Formule:**

$$N = 10\,\log_{10}(k*T*BW_{1Hz})+ 10\,\log_{10}(BW) + NF$$

**Termen:**
- $N$: ruisvloer van de ontvanger in dBm
- $10\,\log_{10}(k*T*BW_{1Hz})$: thermische ruisvermogensdichtheid in dBm/Hz, $10\log_{10}(kT)$ bij $T = 290$ K (kamertemperatuur) Dit is -174 @290K. k boltzmann constante. $BW_{1Hz}$ is de bandbreedte genormaliseerd tot 1Hz.
- $BW$: bandbreedte van de ontvanger in Hz. Dus grotere bandbreedte is slechter want geeft meer ruis (voordeel is wel sneller data versturen, maar dit is niet zo belangrijk voor mij?)
- $NF$: noise figure van de ontvanger in dB (6 tot 7 dB bij 125 kHz; hier 7 dB aangenomen, zoals in de bron). NF = 0dB dan zal de ontvanger er geen ruis bij toevoegen. Maar hier NF = 7 dB. Dan zal de ontvanger er extra thermische ruis bij toevoegen.

**Betekenis:** Het ruisvermogen waar het ontvangen signaal bovenuit moet komen. Een bredere bandbreedte laat meer ruis binnen, en de noise figure geeft aan hoeveel extra ruis de ontvanger zelf toevoegt. Voorbeeld uit de bron: bij 125 kHz en NF = 7 dB is de ruisvloer $-174 + 51 + 7 = -116$ dBm.

**Bron:** STMicroelectronics, AN5664 "RSSI and SNR for LoRa modulation on STM32WL5x/Ex microcontrollers", Rev 2 (januari 2025), vergelijking (2). [RSSI and SNR for LoRa® modulation on STM32WL5x/Ex microcontrollers](zotero://select/library/items/4VPU3K6A)


## 12. Signaal-ruisverhouding (SNR)

**Formule:**

$$SNR = P_{rx} - N$$

**Termen:**
- $SNR$: signaal-ruisverhouding in dB
- $P_{rx}$: ontvangen vermogen (RSSI) in dBm (sectie 9)
- $N$: ruisvloer van de ontvanger in dBm (sectie 11)

**Betekenis:** Hoeveel dB het ontvangen signaal boven (positieve SNR) of onder (negatieve SNR) de ruisvloer ligt. Bij LoRa kan een pakket door de processing gain van de spreading factor nog ontvangen worden bij een negatieve SNR. Er is per spreading factor een minimale SNR waaronder de ontvangst mislukt. Hoe hoger de SF, hoe lager die grens.

**Bron:** STMicroelectronics, AN5664, Rev 2 (januari 2025), vergelijkingen (3) en (5): de sensitivity is de ruisvloer plus de benodigde SNR min de processing gain. [RSSI and SNR for LoRa® modulation on STM32WL5x/Ex microcontrollers](zotero://select/library/items/4VPU3K6A)


## 13. Packet error ratio (PER)

**Formule:**

$$PER(d) = \Pr\big(PL_s > PL_{th}(SF)\big) = 1 - \Phi\left(\frac{PL_{th}(SF) - PL_m(d)}{\sigma}\right)$$

met de path-loss-drempel

$$PL_{th}(SF) = P_{tx} - RSS_{min}(SF)$$

**Termen:**
- $PER(d)$: kans dat een pakket op afstand $d$ niet ontvangen wordt (0 tot 1)
- $PL_s$: werkelijk path loss van één pakket (een waarneming)
- $PL_m(d)$: gemiddeld path loss uit sectie 10, met $\chi_\sigma = 0$
- $PL_{th}(SF)$: maximaal path loss waarbij de ontvanger het pakket nog kan demoduleren, in dB
- $P_{tx}$: zendvermogen in dBm
- $RSS_{min}(SF)$: demodulatiegrens van de ontvanger in dBm per spreading factor (Tabel I van de paper)
- $\Phi$: CDF van de standaardnormale verdeling $\mathcal{N}(0,1)$
- $\sigma$: standaardafwijking van de shadowing in dB (ML-schatting uit Tabel 4)

**Betekenis:** Door de shadowing schommelt het werkelijke path loss rond het gemiddelde $PL_m(d)$. Een pakket gaat verloren als het path loss boven $PL_{th}$ komt. Dat is de bovenste staart van de normale verdeling. Is $PL_m(d) = PL_{th}$, dan is de PER 50 %. De paper noemt als vuistregel dat de betrouwbaarheid ongeveer 84 % is tot de afstand waar $PL_m(d) + \sigma$ gelijk wordt aan $PL_{th}$ (het eerste $\sigma$-bereik). Het aantal pakketten dat aankomt is dan $PRR = 1 - PER$.

**Voorwaarden:** Tx en Rx op 1,5m hoogte. Frequentie 869,525MHz, zendvermogen 20dBm. Handheld ontvanger (kan path loss beinvloeden volgens bron). 

**Bron:** Callebaut & Van der Perre, IEEE IoT Journal, 2020, vergelijking (6) en sectie V-A. $PL_{th}$ volgt uit de RSS-demodulatiegrens (hun Tabel I). In de paper is $P_{tx}$ = 20 dBm; hier laat ik $P_{tx}$ variëren (aanname: het path loss-model is onafhankelijk van $P_{tx}$).  [Characterization of LoRa Point-to-Point Path Loss: Measurement Campaigns and Modeling Considering Censored Data](zotero://select/library/items/L6IHQZU5)
