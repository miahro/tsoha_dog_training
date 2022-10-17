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
  * Optionaalisesti käyttäjä voi muokata suunnitelmaa omalle koiralleen:
    * muuttaa toistojen tavoitemäärää per harjoitus
    * poistaa harjoituksia ohjelmasta
    * lisätä uusia harjoituksia
  * Käyttäjä voi kuitata koiralleen toistoja (tietty harjoitus, tietty paikka, tietty häiriö) tehdyksi
  * Käyttäjälle on olemassa raportointinäkymä, jossa voi koirakohtaisesti seurata koulutussuunnitelman edistymistä / toteutumista


## Heroku linkki ##
https://tsoha-dog-training.herokuapp.com/ 

## Tietokanta-skeema ##
Tietokanta sisältää 7 taulua:
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
    * layout.html: sivun tyylitiedosto
    * index.html: etusivu
    * register.html: uuden käyttäjätunnuksen luonti
    * login.html: sisäänkirjautumissivu
    * add_dog.html: uuden koiran lisäys
    * dogs.html: käyttäjän koirien listaus
    * markprogress.html: koiran koulutuksen raportointi- ja kuittausnäkymä 
    * modify_plan.html: koulutussuunnitelman muokkausnäkymä
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

* Valitse koira
    * listaa käyttjän koirat
    * koiran nimeä klikkaamalla avautuu raporttinäkymä kyseiselle koiralla
    * valittu koira pysyy aktiivisena kunnes valitaan uusi (tai kirjaudutaan ulos)

* Raportointinäkymässä:
    * näkee koko koulutusuunnitelman edistymisen prosentteina
    * taitokohtaisen edistymisen prosenetteina
    * painamalla "näytä kaikki" näkee jokaisen yksittäisen harjoituksen (taito/paikka/häiriö/toistoja/tavoite)
    * tehtyjen koulutusen kuittaus: valitse alasvetovalikosta haluttu koulutus (taito/paikka/häiriö/nykyiset toistot/tavoite)
      * syöttämällä toistojen määrä ja kuittaa koulutus voi kuitata toistoja tehdyiksi
      * syöttämällä negatiivisen luvun voi perua väärin tehtyjä kuittauksia (nykyiset toistot on kuitenkin aina vähintään nolla)

* Muokkaa ohjelmaa näkymä:
  * koirakohtaisen suunnitelman tavoitemäärien muuttaminen: 
    * valitse alasvetovalikosta koulutus (id/taito/paikka/häiriö/tavoitemäärä) ja paina valitse koulutus
    * avatutuvassa näkymässä voit syöttää uuden tavoitteen
      * syöttämllä nolla, koulutus poistuu ohjelmasta
      * valitsemalla "ei muutosta / palaa" palataan edelliseen näkymään ilman muutoksia
  * Lisää uusi koulutus:
    * Päivitä koulutusvaihetoehdot päivittää valittavien koulutusten valikkoon käyttjän tai muiden käyttäjien lisäämät koulutusvaihtoehdot
    * Valitse uusi koulutus: alasvetovalikosta valitaan koulutus (id/taito/pakka/häiriö/toisto)
  * Uuden taito-, paikka tai häiriövaihtoehdon lisäys
    * Syötä haluttu uusi taito, paikka tai häiriö
    * Syötön jälkeen, päivitä koulutusvaihtoehdot päivittää valittaviin koulutuksiin näistä syntyvät yhdistelmät.

	
	
## Releasee note 1.1 

	Tässä vaiheessa sovellukseen on toteutettu kaikki suunniteltu toiminnallisuus. Palautteena saadut korjausehdotukset on myös toteutettu. 

