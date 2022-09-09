# Koirankoulutussovellus #

## Tausta ja käyttötarkoitus ##

Koiran koulutuksessa eri taidot opetaan koiralle lukuisten toistojen kautta. Koirat ovat myös paikkaspesifejä sekä häiriöherkkiä, joten pelkät toistot eivät riitä, vaan harjoituksia pitää toistaa myös eri paikoissa (esim. koti, kauppakeskus, jne.) ja eri häiriöiden (esim. äänet, toiset koirat, jne) läsnäollessa. Yleinen näkemys esimerkiksi luoksetulon harjoittelusta on, että asian oppimiseksi pitäisi koiran kanssa tehdä 20 toistoa, kahdessakymmenessä eri paikassa, ja kahdenkymmenen eri häiriötekijän läsnäollessa. Tämä tarkoittaisi siis 20*20*20=8000 toistoa tälle yhdelle perustaidolle. Koska toistojen määrä on suuri, ja erilaisia harjoiteltavia taitoja on useita, on koulutuksen seuranta hankalaa muistinvaraisesti tai esimerkiksi paperilla. Sovelluksen tarkoitus on koulutusohjelman seuranta ylläpitämällä tietoa tehdyistä harjoituksista. 

## Tärkeimmät ominaisuudet ##
Sovelluksella on seuraavat ominaisuudet:
  * Käyttäjä voi luoda käyttäjätilin (tunnus & salasana), kirjautua sisään ja ulos
  * Käyttäjä voi luoda itselleen koiran (nimi) tai useampia koiria
  * Käyttäjä voi tarkastella ainoastaan omien koiriensa tietoja, ei muiden käyttäjien
  * Uudelle koiralle luodaan (oletus)koulutussuunnitelma, sisältäen tietyt harjoitukset, paikat, häiriöt, ja toistojen määrät
	* Lähtökohtaisesti oletussuunnitelma on kiinteä vakiosuunnitelma
   * Optionaalisesti käyttäjä voi muokata suunnitelmaa omalle koiralleen (tämän ominaisuuden toteutus riippuu kuitenkin sovelluksen laajuudesta, jätetään tekemättä mikäli laajenee liikaa)
  * Käyttäjä voi kuitata koiralleen toistoja (tietty harjoitus, tietty paikka, tietty häiriö) tehdyksi
  * Käyttäjälle on olemassa raportointinäkymä, jossa voi koirakohtaisesti seurata koulutussuunnitelman edistymistä / toteutumista


## Alustava tietokanta-skeema ##
Alustavana suunnitelmana tietokanta sisältää 7 taulua:
  * Users; käyttäjätiedot
  * Dogs; koirat
  * Skills; harjoiteltavat taidot
  * Places; paikat (joissa harjoitellaan)
  * Disturbances; häiriöt (joiden alla harjoitellaan)
  * Plan; koulutussuunnitelma (koira, taidot, paikat, häiriöt, toistojen tavoite)
  * Progress; koulutuksen eteneminen (koira, taidot, paikat, häiriöt, toteutuneet toistot)