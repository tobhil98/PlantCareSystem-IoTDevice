# Database

## Implementation

The databse is implemented in Google Sheets using both standard integrated commands and SQL queries (examples are given below).

#### Data input
The sheet `data` stores all sensor data originating from the client. 

The attributes stored and an example tuple are provided below: 

|Date|Time|temp|Humidity|Moisture|__PowerAppsId__|
|---|---|---|---|---|---|
|12/02/2020|18:51:00|25|36.3|0.0|588145fa080d4dbab930e24b11f17aec|

#### Data Processing
The majority of the data processing is done in the `TIME_DATA` sheet (green cells contain formulas). 
Readings from the sheet `data` are processed to then be easily displayed inside our app over different periods (Current day, Last 7 Days, Last 30 Days, Last 365 Days).

#### User settings

The database is also used to store user plantpot and app settings. 
It is regularly checked to ensure the flower pot and app are using and displaying the most current settings set by the user. 
It is also used by our Alexa skill to update and retrieve data.


#### Example Queries

```
=IF(A2<>"",FLOOR(TEXT(A2,"hh:mm"),"00:15"),"")
```
```
=IF(Q2<>"",TEXT(Q2,"ddd"),"")
```
```
=QUERY( data!A:E, "select A,B, SUM(C)/COUNT(C),SUM(D)/COUNT(D),SUM(E)/COUNT(E) where A <= date """&TEXT(TODAY(),"yyyy-mm-dd")&""" and A > date """&TEXT(TODAY()-7,"yyyy-mm-dd")&""" group by B, A order by A asc", 0)

```

## Access

The database can be accessed [here](https://docs.google.com/spreadsheets/d/1NZDNo2mW4UnCA0T85z3vnphhXVEbOLhD8V7sgtIKTIo/edit?usp=sharing).

