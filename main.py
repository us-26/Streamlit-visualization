import pandas as pd
import streamlit as st

# Change time format of both files to Pandas datetime:

electricity_consumption = pd.read_csv("Electricity_20-09-2024.csv",
                                      delimiter=";")

electricity_consumption["Time"] = pd.to_datetime(
    electricity_consumption["Time"], format=' %d.%m.%Y %H:%M')

electricity_price = pd.read_csv("sahkon-hinta-010121-240924.csv")
electricity_price["Time"] = pd.to_datetime(electricity_price["Time"],
                                           format='%d-%m-%Y %H:%M:%S')

# Join the two data frames according to time:

electricity_price_consumption = electricity_consumption.merge(electricity_price, on="Time", how="inner")

# Required total time data:

electricity_price_consumption["Energy (kWh)"] = electricity_price_consumption["Energy (kWh)"].str.replace(',', '.').astype(float)
electricity_price_consumption["Temperature"] = electricity_price_consumption["Temperature"].str.replace(',', '.').astype(float)
electricity_price_consumption["Hourly bill (cent)"] = electricity_price_consumption["Energy (kWh)"] * electricity_price_consumption["Price (cent/kWh)"]
electricity_price_consumption["Electricity bill (Euros)"] = round((electricity_price_consumption["Hourly bill (cent)"] / 100), 2)
electricity_price_consumption = electricity_price_consumption.drop(['Energy night(kWh)', 'Energy day (kWh)', 'Hourly bill (cent)'], axis=1)
electricity_price_consumption.rename(columns={'Energy (kWh)': 'Electricity consumption (KWh)', 'Price (cent/kWh)': 'Electricity price (cent/kWh)'}, inplace=True)

# Calculated grouped values of daily, weekly or monthly consumption, bill, average price and average temperature:

electricity_daily_consumption = (electricity_price_consumption.groupby( by=pd.Grouper(key="Time", freq='D'))[["Electricity consumption (KWh)", "Electricity bill (Euros)"]].sum()).round(2).reset_index()
electricity_daily_temperature = (electricity_price_consumption.groupby( by=pd.Grouper(key="Time", freq='D'))[["Temperature", "Electricity price (cent/kWh)"]].mean()).round(2).reset_index()
daily_data = pd.merge(electricity_daily_consumption, electricity_daily_temperature, on='Time', how='inner')
daily_data["Time"] = daily_data["Time"].dt.date

electricity_monthly_consumption = (electricity_price_consumption.groupby( by=pd.Grouper(key="Time", freq='ME'))[["Electricity consumption (KWh)", "Electricity bill (Euros)"]].sum()).round(2).reset_index()
electricity_monthly_temperature = (electricity_price_consumption.groupby( by=pd.Grouper(key="Time", freq='ME'))[["Temperature", "Electricity price (cent/kWh)"]].mean()).round(2).reset_index()
monthly_data = pd.merge(electricity_monthly_consumption, electricity_monthly_temperature, on='Time', how='inner')
monthly_data["Time"] = monthly_data["Time"].dt.date

electricity_weekly_consumption = (electricity_price_consumption.groupby( by=pd.Grouper(key="Time", freq='W'))[["Electricity consumption (KWh)", "Electricity bill (Euros)"]].sum()).round(2).reset_index()
electricity_weekly_temperature = (electricity_price_consumption.groupby( by=pd.Grouper(key="Time", freq='W'))[["Temperature", "Electricity price (cent/kWh)"]].mean()).round(2).reset_index()
weekly_data = pd.merge(electricity_weekly_consumption, electricity_weekly_temperature, on='Time', how='inner')
weekly_data["Time"] = weekly_data["Time"].dt.date

# Time interval selector:

st.header("START TIME: ", )
start_date_selection = st.selectbox(label="Choose a start date", options=daily_data["Time"])
st.header("END TIME: ", )
end_date_selection = st.selectbox(label="Choose an end date", options=daily_data[daily_data["Time"] > start_date_selection])

# Data over selected period:

st.header("Data over the selected range: ", )
st.write("Selected Range: ", start_date_selection, " - ", end_date_selection)
consumption_range = daily_data[(daily_data.Time > start_date_selection) & (daily_data.Time <= end_date_selection)]
electricity_range = consumption_range["Electricity price (cent/kWh)"].sum().round(2)
st.write("Electricity consumption over the period: ", electricity_range, " KWh ")
st.write("Total bill over the period: ", consumption_range["Electricity bill (Euros)"].sum().round(2), " Euros ")
st.write("Average hourly price over the period: ", consumption_range["Electricity price (cent/kWh)"].mean().round(2), " Cents ")

# Selector for grouping interval:

st.header("Averaging period: ", )
view_selector = st.selectbox(label="Choose visualization period", options=("Daily",  "Weekly", "Monthly"))

# Line charts of data:

if view_selector == "Daily":
    st.line_chart(consumption_range, x='Time', y="Electricity consumption (KWh)", y_label='Electricity consumption (KWh)',
                  x_label='Year')
    st.line_chart(consumption_range, x='Time', y="Electricity bill (Euros)", y_label='Electricity bill (Euros))',
                  x_label='Year')
    st.line_chart(consumption_range, x='Time', y="Electricity price (cent/kWh)", y_label='Electricity price (cent/kWh)',
                  x_label='Year')
    st.line_chart(consumption_range, x='Time', y="Temperature", y_label='Temperature', x_label='Year')

elif view_selector == "Weekly":
    weekly_data_range = weekly_data[(weekly_data.Time > start_date_selection) & (weekly_data.Time <= end_date_selection)]

    st.line_chart(weekly_data_range, x='Time', y="Electricity consumption (KWh)",y_label='Electricity consumption (KWh)',x_label='Year')
    st.line_chart(weekly_data_range, x='Time', y="Electricity bill (Euros)", y_label='Electricity bill (Euros))',x_label='Year')
    st.line_chart(weekly_data_range, x='Time', y="Electricity price (cent/kWh)", y_label='Electricity price (cent/kWh)',x_label='Year')
    st.line_chart(weekly_data_range, x='Time', y="Temperature", y_label='Temperature', x_label='Year')

elif view_selector == "Monthly":
    monthly_data_range = monthly_data[(weekly_data.Time > start_date_selection) & (weekly_data.Time <= end_date_selection)]

    st.line_chart(monthly_data_range, x='Time', y="Electricity consumption (KWh)",y_label='Electricity consumption (KWh)',x_label='Year')
    st.line_chart(monthly_data_range, x='Time', y="Electricity bill (Euros)", y_label='Electricity bill (Euros))',x_label='Year')
    st.line_chart(monthly_data_range, x='Time', y="Electricity price (cent/kWh)", y_label='Electricity price (cent/kWh)',x_label='Year')
    st.line_chart(monthly_data_range, x='Time', y="Temperature", y_label='Temperature', x_label='Year')
