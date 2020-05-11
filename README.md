# Covid-19-project
Analysis
Dataset was downloaded from Kaggle and it has multiple files. Each of them was treated as an SQL table and analysis queries were created. Here are the queries and their output being discussed:
COVID Cases Country Summary 27th April

select "Country/Region", max("Confirmed") "Confirmed", max("Deaths") "Deaths", max("Recovered") "Recovered"
from covid_19_data
where "ObservationDate" = '04/27/2020'
group by "Country/Region"
order by "Confirmed" desc;

This query shows “latest” state of COVID-19 spread across all the countries. Usage of max() and group by is explained by duplicates in the dataset. The result shows the following:
 
This result can tell us one of the two: either these top countries have the best way to gather data or they were indeed hit by COVID-19 in the most massive manner. It is heartening to know that Recovered to Death ratio is quite positive in majority of countries.
Age distribution
There were three queries added that base analysis off age distribution:
\q
'
when age < 30 then '20 - 30'
when age < 40 then '30 - 40'
when age < 50 then '40 - 50'
when age < 60 then '50 - 60'
when age < 70 then '60 - 70'
else '> 70'
end as "Age bracket",
case
when death = '0' then 0
else 1
end "death",
case
when recovered = '0' then 0
else 1
end "recovered"
/") by_age
group by by_age."Age bracket"
order by "Confirmed" desc;

 
The result shows that indeed most of the confirmed cases are elder people. It also shows that younger people have significintly higher recovery chances.
Now let us see how adding gender impacts the output:
select "Age bracket", gender "Gender", count(*) "Confirmed", sum(death) "Died", sum(recovered) "Recovered" from
(select 
case
when age < 20 then '< 20'
when age < 30 then '20 - 30'
when age < 40 then '30 - 40'
when age < 50 then '40 - 50'
when age < 60 then '50 - 60'
when age < 70 then '60 - 70'
else '> 70'
end as "Age bracket",
case
when death = '0' then 0
else 1
end "death",
case
when recovered = '0' then 0
else 1
end "recovered",
gender
from "COVID19_line_list_data") by_age
group by by_age."Age bracket", gender
order by "Confirmed" desc;

 
The above query shows that males in general seem to be slightly more susceptible to COVID-19.
Now let us add country to see if anything gets strange there.
select "Age bracket", gender "Gender", country "Country", count(*) "Confirmed cases", sum(death) "Died", sum(recovered) "Recovered" from
(select 
case
when age < 20 then '< 20'
when age < 30 then '20 - 30'
when age < 40 then '30 - 40'
when age < 50 then '40 - 50'
when age < 60 then '50 - 60'
when age < 70 then '60 - 70'
else '> 70'
end as "Age bracket",
case
when death = '0' then 0
else 1
end "death",
case
when recovered = '0' then 0
else 1
end "recovered",
gender,
country
from "COVID19_line_list_data") by_age
group by by_age."Age bracket", gender, country
order by "Confirmed cases" desc;

 
From this table you cannot say anything specific about countries. But we can deduct from this view that age data is consistent across majority of the countries – top positions have exclusively elder age bracket cases.
Time series
For time series analysis it was viable to draw charts. Lets look more closely into it.
First there is confirmed cases chart. Countries are ordered by highest number of cases for the latest date. Plotting algorithm picks up all columns, selects date columns, sorts them and plots. Column containing country name is picked up from query config (has to be put manually in the queries file).
select * from time_series_covid_19_confirmed order by "4/27/20" desc;

 
From this we can see how late/early COVID-19 arrived to what country and how did it escalate.
Next 2 queries contain death and recovery statistics:
Death outcome:
select * from time_series_covid_19_deaths order by "4/27/20" desc;

 

And now recovery:
select * from time_series_covid_19_recovered order by "4/27/20" desc;

 
From the above 3 plots we can see that United States have received the most of COVID-19 cases and their Death-Recovery ratio is quite bad compared to other countries. Next 5 countries after US are Spain, Italy, France, Germany and UK. Spain, Germany and Italy also appear in top recoveries.
Out of countries most hit by COVID-19 the most Germany seemed to succeed the most – minimal death outcomes and quite high recoveries.
And of course all this does depend on amount of data gathered. Other countries don’t appear on the top not just because they are successful – quite likely they just don’t gather data and cannot report it. Hence mid country analysis is probably not the most demonstrative. But symptom data isn’t really comprehensive enough to switch analysis on that ground. So let us finish time series plot analysis by a closer look on US data:
Confirmed cases per state:
select * from "time_series_covid_19_confirmed_US" order by "4/27/20" desc;

 
select * from "time_series_covid_19_deaths_US" order by "4/27/20" desc;
 
It would make sense to attach state population information and see these statistics by % . Because we all know how populated New York must be.
The plots confirm that COVID-19 arrived in all the states approximately at the same time. It confirms that its spread is more or less consistent and there are no big anomalies like one state being COVID-19 free or one state having too many confirmed cases. The situation is more or less even.
Now with the final query let us see how many confirmed cases there are connected to Wuhan:
select "Visiting Wuhan", "From Wuhan", count(id) "Cases" from
(select 
 case
  when "visiting Wuhan"::varchar = '1' then 'Yes'
  else 'No'
 end "Visiting Wuhan",
 case
  when "from Wuhan"::varchar = '1' then 'Yes'
  else 'No'
 end "From Wuhan",
 id
from "COVID19_line_list_data") by_wuhan
group by "Visiting Wuhan", "From Wuhan"
order by "Cases" desc;

 
The statistics show that majority of cases are not even directly connected to the people who visited Wuhan. 
Dependancies
The program runs on Python 3.X using PyQt5. As database engine PostgreSQL was chosen. To have it running, one has to install PostgreSQL database engine and create a database there. Database name should be inputted to both executable files.

The following Python libs (included in venv/ directory) were used:
•	PyQt5 – UIX https://pypi.org/project/PyQt5/
•	psycopg – PostgreSQL Python driver https://pypi.org/project/psycopg2/
•	dataset – easy database access https://dataset.readthedocs.io/en/latest/
•	matplotlib – graph plotting https://matplotlib.org/
•	pandas – dataset manipulating https://pandas.pydata.org/

Usage
Project structure includes 2 launchable scripts:
•	make_db.py creates a database from contents of dataset/ directory.
◦	The script picks up any *.csv files in the dataset/ directory and attempts to load them into database with filename as a file.
◦	Failure to load mostly depends on the datatype. At the start of the make_db.py file there are file→column→type bindings that prevent failures.
◦	Current state of all files is set up to work without failures. It is also possible to choose database name at the start of make_db.py file.
•	app.py is the application itself. It has GUI and starts from login window.
◦	It picks up user data from .profile/users that contains username and password separated by \t symbol. It is possible to change password, but system is unlikely to treat well username change or new user creation.
◦	It loads any saved queries from .profile/queries file. Admin can add new queries and they will be automatically saved in the file upon exit from the application
•	login.ui and main.ui files can be opened and modified by QtDesigner. Converting them to Python was performed with this command: venv/bin/pyuic5 -o main_ui.py main.ui
