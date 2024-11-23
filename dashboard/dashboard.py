import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib import colors as mcolors

sns.set(style='dark')

day_df = pd.read_csv("dashboard/day_df.csv")
hour_df = pd.read_csv("dashboard/hour_df.csv")

def create_daily_users_df(df):
    daily_users_df = df.resample(rule='D', on='date').agg({
        "casual_users": "sum",
        "registered_users": "sum",
    })
    daily_users_df["user_counts"] = daily_users_df["casual_users"] + daily_users_df["registered_users"]
    daily_users_df = daily_users_df.reset_index()
    
    daily_users_df.rename(columns={
        "casual_users": "total_casual_users",
        "registered_users": "total_registered_users",
        "user_counts": "count_users"
    }, inplace=True)
    
    return daily_users_df

# Konversi kolom datetime
day_df["date"] = pd.to_datetime(day_df["date"])
hour_df["date"] = pd.to_datetime(hour_df["date"])

min_date = day_df["date"].min()
max_date = day_df["date"].max()

with st.sidebar:
    st.image("dashboard/image.jpg")
    start_date, end_date = st.date_input(
        label='Date', min_value=min_date, max_value=max_date, value=[min_date, max_date]
    )

day_filtered = day_df[(day_df["date"] >= str(start_date)) & (day_df["date"] <= str(end_date))]
hour_filtered = hour_df[(hour_df['date'] >= str(start_date)) & (hour_df['date'] <= str(end_date))]
daily_users_df = create_daily_users_df(day_filtered)

day_filtered['season'] = day_filtered['season'].astype('category')
day_filtered['weathersit'] = day_filtered['weathersit'].astype('category')

# Header Dashboard
st.header('Bike Sharing Dashboard :bicyclist:')
st.subheader('Daily Rent')

# Menampilkan metrik
total_casual_users = daily_users_df["total_casual_users"].sum()
total_registered_users = daily_users_df["total_registered_users"].sum()
total_users = daily_users_df["count_users"].sum()


# LINE VISUALIZATION KE 1
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Casual Rent", value=f"{total_casual_users:,}")

with col2:
    st.metric("Total Registered Rent", value=f"{total_registered_users:,}")

with col3:
    st.metric("Total Rent", value=f"{total_users:,}")

# Plot jumlah pengguna harian
fig, ax = plt.subplots(figsize=(16, 8))

# Plot the lines untuk registered dan casual users
ax.plot(daily_users_df["date"], daily_users_df["total_registered_users"], marker='o', linewidth=2, color="navy", label="Registered Users")
ax.plot(daily_users_df["date"], daily_users_df["total_casual_users"], marker='o', linewidth=2, color="violet", label="Casual Users")


# LINE VISUALIZATION KE 2
# Kostumisasi plot
ax.set_title("Daily Rent Trends", fontsize=20)
ax.set_xlabel("Date", fontsize=15)
ax.set_ylabel("Number of Rent", fontsize=15)
ax.legend()
plt.xticks(rotation=45)  

# Display the plot in Streamlit
st.pyplot(fig)


# LINE VISUALIZATION KE 3
col1, col2 = st.columns(2)
 
with col1:
    st.markdown("<h4 style='font-size: 20px; text-align: center;'>Casual and Registered User Rent Percentage</h4>", unsafe_allow_html=True)
    total_casual_users = daily_users_df["total_casual_users"].sum()
    total_registered_users = daily_users_df["total_registered_users"].sum()

    # Create a DataFrame for the pie chart
    pie_data = pd.DataFrame({
        "user_type": ["Casual User Rent", "Registered User Rent"],
        "user_count": [total_casual_users, total_registered_users]
    })

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(9, 9))
    colors = ['violet', 'navy']
    # Create the pie chart on the axis
    patches, texts, autotexts = ax.pie(pie_data["user_count"], labels=pie_data["user_type"], autopct="%1.1f%%", startangle=90, colors=colors)
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    for text in texts:
        text.set_color('black')
        text.set_fontsize(20)
    for text in autotexts:
        text.set_color('white')
        text.set_fontsize(20)
        
    # Display the plot in Streamlit
    st.pyplot(fig)
 
with col2:
    st.markdown("<h4 style='font-size: 20px; text-align: center;'>Total Rent Distribution by Season and Weather</h4>", unsafe_allow_html=True)

    # Calculate rental counts based on filtered data
    rental_counts = day_filtered.groupby(['season', 'weathersit']).agg({
        'user_counts': 'sum'
    })
    rental_counts['season'] = rental_counts['season'].astype('category')
    rental_counts['weathersit'] = rental_counts['weathersit'].astype('category')
    max_value = rental_counts['user_counts'].max()

    # Tentukan batas atas sumbu y dengan memberikan ruang tambahan
    y_max = max_value * 1.2  # Sesuaikan faktor pengali sesuai kebutuhan

    # Buat grafik batang
    plt.figure(figsize=(20, 18))
    sns.barplot(x='season', y='user_counts', hue='weathersit', data=rental_counts, palette=['black', 'navy', 'violet'])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=3, fontsize=40)
    plt.xlabel('Musim', fontsize=40)
    plt.ylabel('Jumlah Penyewaan', fontsize=40)
    plt.xticks(fontsize=40)

    # Atur skala sumbu y menjadi logaritmik
    plt.yscale('log')
    plt.ylim(bottom=1)  # Pastikan sumbu y dimulai dari 1 pada skala log

    plt.yticks(fontsize=40)
    st.pyplot(plt)


# LINE VISUALIZATION KE 4

st.subheader("Rent Peak Hours")

    # Heatmap untuk casual users
st.markdown("<h4 style='font-size: 20px; text-align: center;'>Casual Users</h4>", unsafe_allow_html=True)

hourly_counts_casual = hour_filtered.groupby(['weekday', 'hour'])['casual_users'].sum().unstack()

colors = ['violet', 'navy']
cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors)
plt.figure(figsize=(13, 6))
sns.heatmap(hourly_counts_casual, cmap=cmap)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel('Jam', fontsize=15)
plt.ylabel('Hari dalam Seminggu',fontsize=15)
st.pyplot(plt)


    # Heatmap untuk registered users
st.markdown("<h4 style='font-size: 20px; text-align: center;'>Registered Users</h4>", unsafe_allow_html=True)
hourly_counts_registered = hour_filtered.groupby(['weekday', 'hour'])['registered_users'].sum().unstack()

colors = ['violet', 'navy']
cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors)

plt.figure(figsize=(13, 6))
sns.heatmap(hourly_counts_registered, cmap=cmap)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel('Jam', fontsize=15)
plt.ylabel('Hari dalam Seminggu', fontsize=15)
st.pyplot(plt)

st.caption('Copyright © Salsabila Syahirah 2024 www.linkedin.com/in/salsabilasyahirah')
