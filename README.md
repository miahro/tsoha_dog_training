# Koirankoulutussovellus #

## Tausta ja käyttötarkoitus ##

Koiran koulutuksessa eri taidot opetaan koiralle lukuisten toistojen kautta. Koirat ovat myös paikkaspesifejä sekä häiriöherkkiä, joten pelkät toistot eivät riitä, vaan harjoituksia pitää toistaa myös eri paikoissa (esim. koti, kauppakeskus, jne.) ja eri häiriöiden (esim. äänet, toiset koirat, jne) läsnäollessa. Yleinen näkemys esimerkiksi luoksetulon harjoittelusta on, että asian oppimiseksi pitäisi koiran kanssa tehdä 20 toistoa, kahdessakymmenessä eri paikassa, ja kahdenkymmenen eri häiriötekijän läsnäollessa. Tämä tarkoittaisi siis 20 x 20 x 20=8000 toistoa tälle yhdelle perustaidolle. Koska toistojen määrä on suuri, ja erilaisia harjoiteltavia taitoja on useita, on koulutuksen seuranta hankalaa muistinvaraisesti tai esimerkiksi paperilla. Sovelluksen tarkoitus on koulutusohjelman seuranta ylläpitämällä tietoa tehdyistä harjoituksista. 

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


## Heroku linkki ##
https://tsoha-dog-training.herokuapp.com/ 

## Alustava tietokanta-skeema ##
Alustavana suunnitelmana tietokanta sisältää 7 taulua:
  * Users; käyttäjätiedot
  * Dogs; koirat
  * Skills; harjoiteltavat taidot
  * Places; paikat (joissa harjoitellaan)
  * Disturbances; häiriöt (joiden alla harjoitellaan)
  * Plan; koulutussuunnitelma (koira, taidot, paikat, häiriöt, toistojen tavoite, visible eli mukana aktiivisessa suunnitelmassa vai ei)
  * Progress; koulutuksen eteneminen (koira, taidot, paikat, häiriöt, toteutuneet toistot)
  
## Modulit
Sovellus on jaettu seuraaviin moduleihin:
  * Python koodi: 
    * app.py: flaskin pääohjelma
    * routes.py: näkymät
    * users.py: käyttäjätietojen hallinta
    * dog.py: koiraan liittyvätn toimintojen (luonti, raportointi) 
    * plan.py: koulutussuunnitelmiin liittyvät toiminnot (oletussuunnitelmien luonti, raporttidatan luku tietokannasta, suoritettujen koulutusten päivitys tietokantaan)
    * db.py: tietokannan polun ja tietokannan määrittely
    * defaults.py: oletussuunnitelman oletustiedot (taidot, paikat, häiriöt). Vain yksinkertaisia tekstimuotoisia listoja + lukutietoa. Eri tiedostossa, jotta muokkaus on helpompaa ja varsinaiset Python-kooditiedostot eivät pitene tarpeettomasti
  * html-pohjat
    * laytout.html: sivun tyylitiedosto
    * index.html: etusivu
    * register.html: uuden käyttäjätunnuksen luonti
    * login.html: sisäänkirjautumissivu
    * error.html: yleinen virhesivu, eri virheet ohjataan tänne virhespesifillä viestillä
    * add_dog.html: uuden koiran lisäys
    * dogs.html: käyttäjän koirien listaus
    * dogchoice.htlm: aktiivisen koiran valinta
    * markprogress.html: koiran koulutuksen raportointi- ja kuittausnäkymä 
  * CSS-pohja
    * main.css
  * SQL-skeema:
    * schema.sql tietokantataulujen määrittely
  


## Käyttöohje
	Sovelluksen käyttöohje
  * Luo ensin käyttäjätunnus 
    * Käyttäjätunnus 1-20 merkkiä
    * Salasana 1-20 merkkiä
    * 1 merkin käyttäjätunnus ja salasana ei ole järkevää, mutta helpomman testauksen vuoksi jätetty näin
  * Kirjaudu sisään
  * Lisää koira
    * käyttäjä voi lisätä useampia koiria
    * koiran lisäyksen yhteydessä luodaan koiralle oletuskoulutussuunnitelma
	* Listaa koirat
    * listaa käyttjän koirat
    * koiran nimeä klikkaamalla avautuu raporttinäkymä kyseiselle koiralla
      * raportointinäkymä on kesken
	* Raportointinäkymästä on linkki suoritettujen koulutusten kuittaamiseen
    * KESKEN
	
	
## Releasee note 0.3
	Git-commit XX sisältää ensimmäiset versiot moduleista. Tässä vaiheessa on keskitytty koodin toiminnallisuuteen ja tietokannan toiminnallisuuteen. Päätoimintojen pitäisi toimia. Jotakuinkin toimivia osia ovat: 
  * käyttäjätunnusten luonti
  * login / logout
  * uuden koiran  luonti / lisäys
    * oletussuunnitelman lisäys uudelle koiralle
  * Heroku release (välipalautus 2 versio)
	
  Totetus on kesken seuraaville:
  * koulutussuunnitelman raportointinäkymä; toiminto on olemassa, ja tietokantakysely toimii, mutta raportti näyttö on aika kökkö. Päivitetään myöhemmin järkeväksi näytöksi
  * Suoritettujen koulutusten kuittaus: toiminto toimii, mutta on vähän kökkö. Parannetaan vielä. 
  * Html sivut:
    * aiktataulusyistä keskitetty ensin backendin toiminnallisuuteen
    * html-sivut on jätetty tässä vaiheessa aivan sotkuksi ja kasari-tyylisiksi
    * nämä korjataan välipalautus 3:ssa
  * CSS tyylitiedosto: 
    * kuten html-pohjat, CSS-tyylitiedostolle ei ole yritetty tehdä mitään järkevää tässä vaiheessa
    * tiedosto on olemassa, jotta nähdään, että se yleensä on käytössä
    * CSS tiedosto korjataan järkeväksi välipalautus 3:ssa

Toteuttamatta on:
 
  * Koulutussuunnitelman muokkaus
    * saattaaa jäädäkin toteuttamatta, mennään ehkä oletussuunnitelmalla

	

