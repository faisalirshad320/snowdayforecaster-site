# -*- coding: utf-8 -*-
"""Data for /cities/<slug>/ metro pages. Each metro reuses its state's thresholds
(tier) from states_data; only the local board, districts, outlets and blurb differ.
Board ZIPs are validated against the zip/ shards at build time (missing ones are skipped).
Snowfall figures are rounded NOAA 1991-2020 normals for the nearest reporting station."""

CITIES = {
 "nyc": dict(
   name="New York City", state="NY", kw="snow day nyc",
   board=[("New York City","10007",29),("Brooklyn","11201",28),("Queens","11432",29),
          ("Bronx","10451",30),("Yonkers","10701",30),("White Plains","10601",32)],
   districts=["New York City Public Schools (NYCPS)","Yonkers Public Schools"],
   announce=["schools.nyc.gov and the NYC Schools app","News 12","NY1 and local TV closings lists"],
   blurb=("New York City rarely takes a traditional snow day: since 2020 NYCPS — the largest school "
          "district in the US at about 900,000 students — usually declares a remote-learning day instead. "
          "Its call effectively sets the tone for the whole metro, while suburban Westchester and Long "
          "Island districts still close the old-fashioned way."),
   neighbors=["buffalo","rochester","boston"]),

 "buffalo": dict(
   name="Buffalo", state="NY", kw="snow day buffalo",
   board=[("Buffalo","14202",95),("Cheektowaga","14225",95),("Amherst","14226",100),
          ("Tonawanda","14150",95),("West Seneca","14224",95),("Lancaster","14086",95)],
   districts=["Buffalo Public Schools","Williamsville Central Schools","Amherst Central Schools"],
   announce=["WIVB 4 and WGRZ 2","WKBW 7","district robocalls and text alerts"],
   blurb=("Buffalo is lake-effect country and routinely runs through snowfalls that would close schools "
          "anywhere else, so the bar here is high. When Erie County issues a driving ban, that — not snow "
          "depth alone — is often what finally closes the districts."),
   neighbors=["rochester","syracuse","nyc","cleveland"]),

 "rochester": dict(
   name="Rochester", state="NY", kw="snow day rochester ny",
   board=[("Rochester","14604",100),("Greece","14616",100),("Irondequoit","14617",100),
          ("Henrietta","14467",95),("Webster","14580",100),("Brighton","14618",100)],
   districts=["Rochester City School District","Greece Central Schools","Webster Central Schools"],
   announce=["13WHAM","WHEC 10 and WROC 8","district websites and alerts"],
   blurb=("Rochester sits under lake-effect bands off Lake Ontario, and totals swing sharply from one "
          "suburb to the next. It is common for the city district and its ring of suburban districts to "
          "make different calls on the very same morning."),
   neighbors=["buffalo","syracuse","nyc"]),

 "syracuse": dict(
   name="Syracuse", state="NY", kw="snow day syracuse",
   board=[("Syracuse","13202",125),("Cicero","13039",120),("Camillus","13031",120),
          ("Liverpool","13088",123),("Baldwinsville","13027",120),("East Syracuse","13057",123)],
   districts=["Syracuse City School District","North Syracuse Central Schools","West Genesee Central Schools"],
   announce=["WSYR 9","CNYcentral (WSTM / WTVH)","Spectrum News"],
   blurb=("Syracuse is one of the snowiest big cities in America, averaging around 125 inches a winter, so "
          "it tolerates heavy snow before closing. An ice storm or extreme wind chill is more likely to "
          "trigger a day off here than ordinary snowfall."),
   neighbors=["rochester","buffalo","nyc"]),

 "denver": dict(
   name="Denver", state="CO", kw="snow day denver",
   board=[("Denver","80202",57),("Aurora","80010",55),("Boulder","80302",85),
          ("Lakewood","80215",60),("Littleton","80120",55),("Arvada","80002",58)],
   districts=["Denver Public Schools","Jeffco Public Schools","Cherry Creek Schools","Aurora Public Schools"],
   announce=["9NEWS, Denver7 and FOX31 closings lists","district websites and apps"],
   blurb=("Denver's snow melts fast under the high-altitude sun, so timing matters more than the total — a "
          "foot overnight that clears by mid-morning may bring only a delay. Cold and icy side streets drive "
          "many Front Range closures as much as the snow itself."),
   neighbors=[]),

 "chicago": dict(
   name="Chicago", state="IL", kw="snow day chicago",
   board=[("Chicago","60601",38),("Naperville","60540",37),("Evanston","60201",38),
          ("Schaumburg","60173",37),("Oak Lawn","60453",38),("Joliet","60432",33)],
   districts=["Chicago Public Schools","Indian Prairie District 204","Elgin Area District U-46"],
   announce=["Emergency Closing Center (emergencyclosings.com)","ABC 7 and NBC 5","district text alerts"],
   blurb=("Chicago Public Schools famously almost never closes — it treats a snow day as a last resort and "
          "leans on e-learning days instead. As a result the collar suburbs around the city close far more "
          "often than Chicago itself does."),
   neighbors=[]),

 "detroit": dict(
   name="Detroit", state="MI", kw="snow day detroit",
   board=[("Detroit","48226",33),("Warren","48089",34),("Dearborn","48124",33),
          ("Livonia","48150",36),("Sterling Heights","48310",35),("Troy","48083",36)],
   districts=["Detroit Public Schools Community District","Warren Consolidated Schools",
              "Dearborn Public Schools","Utica Community Schools"],
   announce=["WXYZ 7 and WDIV 4","WJBK FOX 2","district robocalls"],
   blurb=("Metro Detroit districts weigh cold as heavily as snow: Michigan lets schools close for extreme "
          "wind chill, and a hard freeze with icy roads shuts Wayne, Oakland and Macomb county schools "
          "several times most winters, often with no fresh snow at all."),
   neighbors=["grand-rapids","cleveland"]),

 "grand-rapids": dict(
   name="Grand Rapids", state="MI", kw="snow day grand rapids",
   board=[("Grand Rapids","49503",75),("Wyoming","49509",72),("Kentwood","49508",72),
          ("Walker","49534",74),("Grandville","49418",72),("East Grand Rapids","49506",75)],
   districts=["Grand Rapids Public Schools","Kentwood Public Schools","Forest Hills Public Schools"],
   announce=["WOOD TV8 and WZZM 13","FOX 17","district alerts"],
   blurb=("West Michigan gets heavy lake-effect snow off Lake Michigan, so Grand Rapids-area districts — GRPS "
          "especially — close or run two-hour delays regularly through January and February, more often than "
          "the state's east side."),
   neighbors=["detroit"]),

 "cleveland": dict(
   name="Cleveland", state="OH", kw="snow day cleveland",
   board=[("Cleveland","44114",64),("Parma","44129",60),("Lakewood","44107",62),
          ("Euclid","44117",60),("Cleveland Heights","44118",62),("Strongsville","44136",60)],
   districts=["Cleveland Metropolitan School District","Parma City Schools","Lakewood City Schools"],
   announce=["WKYC 3 and FOX 8 (WJW)","News 5 Cleveland (WEWS)","district websites"],
   blurb=("Cleveland's east-side snowbelt suburbs get far more lake-effect snow than the city or the west "
          "side, so eastern districts such as Cleveland Heights and Chardon routinely close while western "
          "ones stay open on the same day."),
   neighbors=["detroit","buffalo"]),

 "boston": dict(
   name="Boston", state="MA", kw="snow day boston",
   board=[("Boston","02108",49),("Cambridge","02139",50),("Quincy","02169",45),
          ("Newton","02458",50),("Somerville","02143",49),("Brookline","02445",49)],
   districts=["Boston Public Schools","Cambridge Public Schools","Newton Public Schools"],
   announce=["WCVB 5 and WBZ 4","NBC10 Boston","Boston.com closings page"],
   blurb=("Boston closings often hinge on coastal nor'easters and wind rather than inland snow totals. The "
          "city and its inner suburbs tend to move together, while coastal districts also watch for blizzard "
          "warnings and storm surge."),
   neighbors=["nyc"]),

 "dallas": dict(
   name="Dallas", state="TX", kw="snow day dallas",
   board=[("Dallas","75201",2),("Fort Worth","76102",2),("Plano","75074",2),
          ("Irving","75060",2),("Arlington","76010",2),("Garland","75040",2)],
   districts=["Dallas ISD","Fort Worth ISD","Plano ISD"],
   announce=["WFAA 8 and NBC 5 (KXAS)","FOX 4","district alerts"],
   blurb=("In Dallas-Fort Worth it is ice, not snow, that closes schools. A glaze on overpasses and bridges "
          "can shut every district in the Metroplex with no accumulation at all, which is why DFW closings "
          "often begin as delays that convert to full closures once roads refreeze."),
   neighbors=[]),

 "minneapolis": dict(
   name="Minneapolis", state="MN", kw="snow day minneapolis",
   board=[("Minneapolis","55401",52),("St. Paul","55102",52),("Bloomington","55420",50),
          ("Plymouth","55447",54),("Eden Prairie","55344",52),("Maple Grove","55369",54)],
   districts=["Minneapolis Public Schools","Saint Paul Public Schools","Anoka-Hennepin School District","Osseo Area Schools"],
   announce=["KARE 11 (NBC)","WCCO 4 (CBS)","KSTP 5 (ABC)","district websites and alerts"],
   blurb=("The Twin Cities are built for winter, so schools here tolerate snow that would close districts further south "
          "and rarely take a day for snowfall alone. What closes Minneapolis and Saint Paul schools is extreme cold: "
          "Minnesota lets districts call off for dangerous wind chill, and a hard Arctic outbreak shuts the metro several "
          "times most winters with little or no fresh snow."),
   neighbors=["milwaukee","chicago"]),

 "columbus": dict(
   name="Columbus", state="OH", kw="snow day columbus",
   board=[("Columbus","43215",28),("Dublin","43017",28),("Westerville","43081",28),
          ("Hilliard","43026",28),("Grove City","43123",27),("Gahanna","43230",28)],
   districts=["Columbus City Schools","South-Western City School District","Dublin City Schools","Olentangy Local School District"],
   announce=["WBNS 10 (CBS)","WCMH 4 (NBC)","WSYX 6 (ABC)","district websites and alerts"],
   blurb=("Central Ohio gets moderate snow, around 28 inches a winter, and ice is as likely to close Columbus schools as "
          "snow is. Columbus City Schools, one of the largest districts in Ohio, and the big suburban districts around it "
          "weigh road conditions and wind chill heavily, so a forecast of freezing rain or a hard overnight freeze can "
          "close schools on a day with very little snow on the ground."),
   neighbors=["cleveland","detroit"]),

 "milwaukee": dict(
   name="Milwaukee", state="WI", kw="snow day milwaukee",
   board=[("Milwaukee","53202",47),("Wauwatosa","53226",47),("West Allis","53214",47),
          ("Waukesha","53186",46),("Brookfield","53045",46),("Greenfield","53220",47)],
   districts=["Milwaukee Public Schools","Wauwatosa School District","West Allis-West Milwaukee School District","Waukesha School District"],
   announce=["TMJ4 (WTMJ, NBC)","WISN 12 (ABC)","WITI 6 (FOX)","district websites and alerts"],
   blurb=("Milwaukee sits on Lake Michigan, which both moderates the cold and feeds lake-enhanced snow, so the metro "
          "tolerates a good deal of snow before closing. Milwaukee Public Schools, the largest district in Wisconsin, "
          "tends to set the tone for the area, and ice and dangerous wind chill close schools here as often as heavy "
          "snowfall does."),
   neighbors=["chicago","minneapolis"]),

 "albany": dict(
   name="Albany", state="NY", kw="snow day albany",
   board=[("Albany","12203",60),("Schenectady","12305",60),("Troy","12180",62),
          ("Clifton Park","12065",62),("Delmar","12054",60),("Guilderland","12084",61)],
   districts=["Albany City School District","Shenendehowa Central School District","Bethlehem Central School District","Schenectady City School District"],
   announce=["WNYT NewsChannel 13 (NBC)","News10 WTEN (ABC)","WRGB CBS 6 (CBS)","district websites and alerts"],
   blurb=("The Capital Region averages around 60 inches a winter and its districts are used to it, so it takes a real "
          "storm, an ice event or deep cold to close schools here. Nor'easters climbing the coast and cold air draining "
          "down from the Adirondacks are the usual triggers, and the city, Schenectady and the suburban districts around "
          "them do not always make the same call on the same morning."),
   neighbors=["nyc","syracuse","boston"]),
}
