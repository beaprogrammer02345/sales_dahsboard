import streamlit as st
import plotly.express as px
import pandas as pd
import os 
import warnings
from prophet import Prophet 
warnings.filterwarnings('ignore')
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go  # Import for line chart
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import numpy as np
from PIL import Image
import base64
import io
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime, timedelta
from io import BytesIO
import plotly.io as pio
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error



st.set_page_config(page_title="Sales Dashboard!!!", page_icon=":bar_chart:", layout="wide")
# HTML to include Font Awesome
st.empty()


st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)
# to hide the inbuilt structure
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        margin-top: 0px;  /* Remove margin at the top */
        padding-top: 0px;  /* Remove padding at the top */
    }
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Path to the local image
#image_path = 'background.png'  # Adjust the path according to where your image is located
#image_path = 'background.png'  # Adjust the path according to where your image is located
image_path = 'body-background.png'  # Adjust the path according to where your image is located
# Function to calculate growth rate
def calculate_growth_rate(current_sales, previous_sales):
    if previous_sales == 0:  # Handle division by zero
        return 100 if current_sales > 0 else 0
    return ((current_sales - previous_sales) / previous_sales) * 100

# Function to set a local image as background
def add_bg_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function to add the background
add_bg_from_local(image_path)

st.markdown(
    """
    <style>
    .header-container {
        display: flex;
        align-items: flex-start; /* Align items to the top */
        margin: 0; 
        padding: 0;
        height: auto; /* Adjust height as needed */
    }
    h1 {
        margin-top: 0px;  /* Adjust this to control top space */
        margin-bottom: 0px;  /* Adjust this to control bottom space */ 

    }
    </style>
    <div class="header-container">
        <h1>
            <i class="fa-sharp fa-solid fa-chart-line"></i>  Sales Insights
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

#CSS Design
st.markdown("""
<style>


[data-testid="block-container"] {
    padding-left: 0rem;
    padding-right: 0rem;
    padding-top: 0rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;/
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}


[data-testid="stMetric"] {
   
    background-color: #0B0D28; 
    text-align: center;
    padding: 4px 0;
    margin:0px;
    border-radius: 18px;
    animation: pulse 1.5s infinite; /* Subtle pulse animation */
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  margin:0px;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

/* Animation */
[data-testid="stMetric"] {
    animation: pulse 1.5s infinite; /* Subtle pulsing animation */
}

</style>
""", unsafe_allow_html=True)

###End of css style
# Function to convert an image file to base64
def load_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to load and replace black pixels with white
def load_and_replace_black(image_path):
    image = Image.open(image_path).convert("RGBA")  # Open the image and convert to RGBA
    
    # Get the image's data as a list of tuples
    data = image.getdata()
    
    new_data = []
    for item in data:
        # Replace all black pixels (or near-black) with white
        if item[0] < 50 and item[1] < 50 and item[2] < 50:  # Assuming near-black pixels (RGB < 50)
            new_data.append((255, 255, 255, item[3]))  # Replace with white
        else:
            new_data.append(item)  # Keep the pixel as is

    # Update the image with new data
    image.putdata(new_data)
    
    return image


# This function will for the  sales by category section


# Function to load a local image and convert it to base64
def load_background_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load background image
#background_image_base64 = load_background_image_as_base64("body-background.png")
background_image_base64 = load_background_image_as_base64("background2.png")

# Function to convert local image file to base64
def get_base64_image(img_file):
    with open(img_file, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')



# Function to convert the image to base64 for embedding in HTML
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

#Function

#In order to create the custom css for metric
def custom_metric(label, value, percentage_change, icon_color="#CB3CFF", label_color="#CB3CFF",image_path=None,background_image_path=None):
    # Determine the color for the percentage change
    change_color = "#05CB99" if percentage_change >= 0 else "#FF3C3C"
    # If an image path is provided, convert it to base64
    if image_path:
        # Load the image and replace black with white
        image = load_and_replace_black(image_path)
        # Convert the modified image to base64
        image_base64 = image_to_base64(image)
        # Create the img tag for the HTML
        img_tag = f'<img src="data:image/png;base64,{image_base64}" style="width: 50px; height: 50px; margin-right: 15px;">'
    else:
        img_tag = ''
    # Initialize background_image_base64
    background_image_base64 = ''  # Default to an empty string

    # Convert background image to base64 if provided
    if background_image_path:
        background_image_base64 = load_image_as_base64(background_image_path)

    # Create HTML with the specified colors
    st.markdown(f"""
        <style>
            .metric-container {{
                position: relative;
                background-color: rgba(11, 13, 40, 0.7);
                padding: 10px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                overflow: hidden;
            }}
            .metric-container::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: url('data:image/png;base64,{background_image_base64}');
                background-size: cover;
                background-position: center;
                opacity: 0.5; /* Adjust opacity here */
                z-index: -1; /* Ensure it's behind the content */
            }}
            .metric-content {{
                position: relative; /* Make sure content is above the background */
                z-index: 1; /* Ensure it appears above the background image */
            }}
        </style>

        <div class="metric-container">
            <div  class="metric-content" style="flex:1;display: flex; flex-direction: column; justify-content: center;margin-left:18px">
                <p style="color:white; font-size:30px; margin: 0; padding: 0;">
                    <span style="color:{icon_color}; font-size:26px;">{label[:1]}</span>{label[1:]}
                </p>
                <div style="display: flex; align-items: center; margin-top: 8px;">
                    <h2 style="color:#fafafa; margin: 0; font-size:28px;">{value}</h2>
                    <span style="color:{change_color}; font-size:22px; margin-left: 10px;">{percentage_change:.2f}%</span>
                </div>
            </div>
            <div style="flex-shrink: 0; text-align: right; margin-right:10px">
                <div style="background-color: #0075FF; border-radius: 10px; padding: 10px; display: inline-flex; align-items: center;">
                    {img_tag}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)



# Helper function to format large numbers
def format_number(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return f"{int(value)}"

def parse_dates(df, date_column):
    date_formats = [
        #added more date format
        #changed some format

        '%d-%m-%Y', '%d/%m/%Y',  # Day-first formats
        '%m-%d-%Y', '%m/%d/%Y',  # Month-first formats
        '%Y-%m-%d', '%Y/%m/%d',  # ISO formats
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',  # ISO 8601 with time
        '%d %B %Y', '%d %b %Y',  # Full and abbreviated month names
        '%a, %d %b %Y',  # Weekday with date
        '%m-%d-%Y %I:%M %p', '%m/%d/%Y %I:%M %p'  # 12-hour format with AM/PM

    ]


    for fmt in date_formats:
        try:
            return pd.to_datetime(df[date_column], format=fmt, dayfirst=fmt.startswith('%d'),errors='coerce')
        except ValueError:
            continue
    return(None)

# Display the image in the sidebar
# Display the image in the sidebar
image_path = 'body-background.png'  # Path to your image

# Add custom CSS to make the sidebar image occupy the whole sidebar
def sidebar_bg_image(image_path):
    # Open the image and convert it to base64
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
        encoded_img = base64.b64encode(img_data).decode()

    # Add custom CSS for the sidebar background image
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded_img}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;

        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function to add the background image to the sidebar
sidebar_bg_image(image_path)




st.sidebar.header(" :file_folder: Upload your datasets")
fl = st.sidebar.file_uploader(" ", type=(["csv", "txt", "xlsx", "xls"]))




if fl is not None:
    # Check the file extension to determine how to read it
    if fl.name.endswith('.csv'):
        df = pd.read_csv(fl, encoding='latin1')
    elif fl.name.endswith('.xls'):
        df = pd.read_excel(fl, engine='xlrd')  # Use xlrd for .xls files
    elif fl.name.endswith('.xlsx'):
        df = pd.read_excel(fl, engine='openpyxl')  # Use openpyxl for .xlsx files
    else:
        st.error("Unsupported file type. Please upload a valid file.")
        df = None  # Set df to None if no valid file is uploaded

    ##if df is not None:
    if 'Order Date' in df.columns:
        # Ensure proper date parsing and remove rows with NaT in 'Order Date'
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
        #df["Order Date"] = pd.to_datetime(df["Order Date"])
        ##df["Order Date"] = parse_dates(df, "Order Date")
        #st.write(df["Order Date"].head())

        df = df.dropna(subset=["Order Date"])
        # Create 'Order Year' and 'Order Month' columns if not present
        df['Order Year'] = df['Order Date'].dt.year
        ##df['Order Month'] = df['Order Date'].dt.month  # Extract month for use
        df['Month'] = df['Order Date'].dt.month  # Extract month for use



        # Create or modify columns safely
        if 'Order Year' not in df.columns:
            df['Order Year'] = df['Order Date'].dt.year
        
        # Filter by year
        st.sidebar.subheader("Choose your filter")
        year_list = sorted(list(df['Order Year'].unique()), reverse=True)
        selected_year = st.sidebar.selectbox("Select a year", year_list)

        # Filter the DataFrame by the selected year
        df_selected_year = df[df['Order Year'] == selected_year].copy()

        # Filter by country (only show countries from the selected year data)
        Country = st.sidebar.multiselect("Pick the Country", df_selected_year["Country"].unique())

        if not Country:
            filtered_df = df_selected_year.copy()  # If no country is selected, show data for all countries
        else:
            filtered_df = df_selected_year[df_selected_year["Country"].isin(Country)]  # Filter by selected countries
        

        #New code ---
        col=st.columns((2,2,2,2),gap='small')
        total_sales = filtered_df["Sales"].sum()
        #total_sales = df["Sales"].sum()
        total_orders = filtered_df.shape[0]
        #total_orders = df.shape[0]
        total_profit = filtered_df["Profit"].sum()
        #total_profit = df["Profit"].sum()


        # Calculate Profit Margin Percentage
        if total_sales != 0:  # To avoid division by zero error
            profit_margin_percentage = (total_profit / total_sales) * 100
        else:
            profit_margin_percentage = 0

        #for kpi like
        # Calculate the number of unique customers
        total_customers = filtered_df["Customer Name"].nunique()
        # Calculate Order Frequency (Number of Orders / Total Customers)
        if total_customers != 0:  # To avoid division by zero
            order_frequency = total_orders / total_customers
        else:
            order_frequency = 0


        #Get current date
        today = datetime.today()
        # Get the latest date in the dataset
        max_date = df['Order Date'].max()

        # Define current period (e.g., current month)
        current_period_start = max_date.replace(day=1)  # First day of the current month
        next_month = (current_period_start + pd.DateOffset(months=1)).replace(day=1)  # First day of the next month
        current_period_end = next_month - pd.DateOffset(days=1)  # Last day of the current month

        # Define previous period based on the current period
        previous_month_start = (current_period_start - pd.DateOffset(months=1)).replace(day=1)
        previous_month_end = current_period_start - pd.DateOffset(days=1)
        
        
        # Convert to datetime
        current_period_start = pd.to_datetime(current_period_start)
        current_period_end = pd.to_datetime(current_period_end)
        previous_month_start = pd.to_datetime(previous_month_start)
        previous_month_end = pd.to_datetime(previous_month_end)

        # Filter data for current and previous periods
        current_period_df = df[(df['Order Date'] >= current_period_start) & (df['Order Date'] <= current_period_end)]
        previous_period_df = df[(df['Order Date'] >= previous_month_start) & (df['Order Date'] <= previous_month_end)]
       
        # Calculate metrics for current period
        current_total_sales = current_period_df['Sales'].sum()
        current_total_profit = current_period_df['Profit'].sum()
        current_profit_margin = (current_total_profit / current_total_sales) * 100 if current_total_sales != 0 else 0

        # Calculate metrics for previous period
        previous_total_sales = previous_period_df['Sales'].sum()
        previous_total_profit = previous_period_df['Profit'].sum()
        previous_profit_margin = (previous_total_profit / previous_total_sales) * 100 if previous_total_sales != 0 else 0
        # Calculate order frequencies
        current_orders = current_period_df.shape[0]
        current_customers = current_period_df['Customer Name'].nunique()
        current_order_frequency = current_orders / current_customers if current_customers != 0 else 0

        previous_orders = previous_period_df.shape[0]
        previous_customers = previous_period_df['Customer Name'].nunique()
        previous_order_frequency = previous_orders / previous_customers if previous_customers != 0 else 0


        # Calculate percentage changes
        sales_change = ((current_total_sales - previous_total_sales) / previous_total_sales) * 100 if previous_total_sales != 0 else 0
        profit_change = ((current_total_profit - previous_total_profit) / previous_total_profit) * 100 if previous_total_profit != 0 else 0
        profit_margin_change = current_profit_margin - previous_profit_margin
        order_frequency_change = ((current_order_frequency - previous_order_frequency) / previous_order_frequency) * 100 if previous_order_frequency != 0 else 0


        # Calculate percentage change
        if previous_order_frequency != 0:
            order_frequency_change = ((current_order_frequency - previous_order_frequency) / previous_order_frequency) * 100
        else:
            order_frequency_change = 0

        #checking for data filtering 
        # Displaying all KPIs inside col[0]
        with col[0]:
            sales_image_path = "sales_img.png"
            #custom_metric(value=f"{format_number(total_sales)}", label=" 📈  Total Sales")
            custom_metric("  Current Sales", f"{format_number(current_total_sales)}", sales_change, image_path=sales_image_path,background_image_path="background2.png")
            

        with col[1]:
            #custom_metric(value=f"{format_number(total_orders)}", label="📦 Total Order")
            #custom_metric("🔄 Order Frequency", f"{order_frequency:.2f}")
            profit_image_path="profit.png"
            custom_metric(
                "  Current Profit", 
                f"{format_number(current_total_profit)}", 
                profit_change, 
                icon_color="#FF6347",  # Tomato for the icon
                label_color="#1E90FF" , # Dodger Blue for the label
                image_path=profit_image_path,
                background_image_path="background2.png"
            )

        with col[2]:
            #custom_metric(value=f"{format_number(total_profit)}", label="💰 Total Profit")
            order_image_path="order.png"
            custom_metric(
                " Order Frequency", 
                f"{current_order_frequency:.2f}", 
                order_frequency_change, 
                icon_color="#FF1493",  # Deep Pink for the icon
                label_color="#00BFFF",  # Deep Sky Blue for the label
                image_path=order_image_path,
                background_image_path="background2.png"
            )

        with col[3]:

            # Adding KPI for Profit Margin Percentage
            #custom_metric(value=f"{profit_margin_percentage:.2f}%", label="📊 Profit Margin")
            profit_margin_path="margin.png"
            custom_metric(
                " Profit Margin", 
                #f"{current_profit_margin:.2f}%", 
                f"{current_profit_margin:.2f}%", 
                profit_margin_change, 
                icon_color="#FFD700",  # Gold for the icon
                label_color="#ADFF2F" , # Green Yellow for the label
                image_path=profit_margin_path,
                background_image_path="background2.png"
            )


        st.markdown("<br>", unsafe_allow_html=True)  # Adds vertical space between sections
        col=st.columns((3.5,2,2.5),gap='small')
        with col[0]:
            # Add a gap using st.markdown()
            top_products = filtered_df.groupby('Product Name')['Sales'].sum().reset_index()
            # To show top 3 products
            top_products_sorted = top_products.sort_values(by='Sales', ascending=False).head(3)
            # Calculate the total sales for percentage calculation
            total_sales = top_products_sorted['Sales'].sum()    

            # Calculate percentage sales and add it as a new column
            top_products_sorted['Percentage'] = (top_products_sorted['Sales'] / total_sales * 100).round(2)
            # Truncate product names to a maximum of 2 words
            def truncate_product_name(name, max_words=2):
                words = name.split()
                return ' '.join(words[:max_words]) + ('...' if len(words) > max_words else '')

            # Shorten long product names if they exceed a certain length
            top_products_sorted['Product Name'] = top_products_sorted['Product Name'].apply(lambda x: truncate_product_name(x, max_words=2))

            # Load the image using PIL
            image_path = 'card_free.png'  # Ensure this matches your file name and extension
            image = Image.open(image_path)
            # Convert the image to base64 for use in CSS
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            # Add custom CSS for background image with opacity
            st.markdown(
                f"""
                    <style>
                        .background {{
                            background-image: url('data:image/png;base64,{img_str}'); /* Inline base64 image */ 
                            background-size: cover;
                            background-position: center;
                            margin-top:12px;
                            height: 500px;
                            width: 100%;
                            position: relative;
                            z-index: 1;
                            opacity: 0.8; /* Adjust the opacity as needed */
                        }}
                        .content {{
                            position: absolute;
                            z-index: 2; /* Ensure content appears above the background */
                            color: white; /* Change text color to white for visibility */
                            padding: 20px;
                            bottom: 20px; /* Position content at the bottom */
                            left: 20px; /* Position content to the left */
                        }}
                        .top{{
                            padding-top:20px;
                            margin-left:25px;
                            font-size:39px;
                        }}
                        .top-products-container {{
                            background-color: rgb(0,0,0,0.2);
                            color: #fafafa;
                            padding: 20px;
                            height:150px;
                            font-family: 'Montserrat', sans-serif;
                        }}
                        .top-products-item {{
                            display: flex;
                            align-items: center;
                            
                            margin-bottom: 1px;
                        }}
                        .top-products-item i {{
                            margin-right: 15px; /* Space between icon and text */
                            font-size: 14px;
                            color: #fafafa; /* Light blue color for icons */
                        }}   
                        .top-products-item strong {{
                            color: #fafafa;
                            font-size:25px;
                            margin-botton:5px;
                            flex-grow: 1; /* Take up remaining space */
                        }}
                        .top-products-item span {{
                            color: #fafafa; /* Light blue color for percentages */
                            margin-left:15px;
                            font-size:20px;
                        }}
                    </style>
                    <div class="background">
                        <h2 class='top'>Product</h2>
                        <div class="content">
                            {''.join(f'<div class="top-products-item">'
                                f'<i class="fas fa-box" style="margin-right: 2px; font-size: 14px;"></i>'
                                f'<strong>{row["Product Name"]}</strong>'
                                f'<span>{row["Percentage"]}%</span>'
                                f'</div>' for _, row in top_products_sorted.iterrows())}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
            )

        with col[1]:
            # Path to your local image file
            st.markdown(
                """
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                    body {
                       font-family: 'Montserrat', sans-serif;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            local_image_path = 'background2.png'  # Change this to your local image path
            base64_image = get_base64_image(local_image_path)

            # Group by Category and sum Sales
            category_df = filtered_df.groupby(by=['Category'], as_index=False)["Sales"].sum()
            # Define colors
            ring_colours = ['#6C73D8', '#114CA5', '#071A4A']
            # Create a pie chart with Plotly Express
            fig = px.pie(
                category_df,
                values="Sales",
                names="Category",
                hole=0.7,
                color_discrete_sequence=ring_colours  # Use the custom color sequence
            )

            
            # Calculate the total sales and top category for central text
            total_sales = filtered_df['Sales'].sum()
            top_category = filtered_df.loc[filtered_df['Sales'].idxmax(), 'Category']
            top_sales = filtered_df['Sales'].max()

            # Update layout
            fig.update_layout(
                #height=400,
                height=500,
                title={
                    'text': "Sales by Category",
                    'y':0.91,
                    'x':0.05,
                    'xanchor': 'left',
                    'yanchor': 'top',
                    'font': dict(
                        family='Montserrat, sans-serif',
                        size=22,
                        color='#fafafa',  # Light gray text
                        
                    ),
                },
                paper_bgcolor="rgba(0,0,0,0.4)",
                plot_bgcolor="rgba(0,0,0,0)",  # Make plot area transparent for the image
                margin=dict(l=0, r=0, t=70, b=80),
                showlegend=True,  # Show the legend
                font=dict(color='#fafafa'),
                legend=dict(
                    orientation="h",  # Horizontal legend
                    yanchor="bottom",
                    y=-0.3,  # Position the legend below the chart
                    xanchor="left",
 
                    x=0.2,  # Position the legend to the left
                    font=dict(color='#fafafa'),  # Light gray for legend text



                ),
            )
            
            # Adding glow effect to chart elements (lines and slices)
            #fig.update_traces(marker_line=dict(width=2, color='rgba(255, 255, 255, 0.3)'), selector=dict(type='pie'))

            # Apply hover effect styling
            fig.update_traces(
                hoverinfo="label+percent+value",  # Display more info on hover
                hoverlabel=dict(
                    font_size=12,
                )
            )
           
            # Display the chart in Streamlit
            
            st.plotly_chart(fig, use_container_width=True)
        with col[2]:
            st.markdown(
                """
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                    body {
                       font-family: 'Montserrat', sans-serif;
                    }
                </style>
                """,
               unsafe_allow_html=True
            )
            local_image_path = 'background2.png'  # Change this to your local image path
            base64_image = get_base64_image(local_image_path)

            

            # Group by Region and sum Sales (top 4 regions)
            region_df = filtered_df.groupby(by=['Region'], as_index=False)["Sales"].sum()
            top_regions = region_df.nlargest(4, 'Sales')

            # Define colors
            ring_colours = ['#6C73D8', '#114CA5', '#071A4A', '#8C7EC0']  # Add the new color for the fourth region

            # Create a pie chart for Sales by Category with Plotly Express
            
            # Create a pie chart for Sales by Region with Plotly Express
            region_fig = px.pie(
                top_regions,
                values="Sales",
                names="Region",
                
                color_discrete_sequence=ring_colours  # Use the same custom color sequence
            )
            # Update layout for Sales by Region chart
            region_fig.update_layout(
                height=500,
                title={
                    'text': "Sales by Region",
                    'y': 0.91,
                    'x': 0.05,
                    'xanchor': 'left',
                    'yanchor': 'top',
                    'font': dict(
                    family='Montserrat, sans-serif',
                    size=22,
                    color='#fafafa',  # Light gray text
                ),
            },
            paper_bgcolor="rgba(0,0,0,0.4)",
            plot_bgcolor="rgba(0,0,0,0)",  # Make plot area transparent for the image
            margin=dict(l=0, r=0, t=70, b=80),
            showlegend=True,  # Show the legend
            font=dict(color='#fafafa'),
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",
                y=-0.3,  # Position the legend below the chart
                xanchor="left",
                x=0.2,  # Position the legend to the left
                font=dict(color='#fafafa'),  # Light gray for legend text
            ),
            )
            region_fig.update_traces(
                hoverinfo="label+percent+value",  # Display more info on hover
                hoverlabel=dict(
                    font_size=12,
                )
            )
            st.plotly_chart(region_fig, use_container_width=True)



            
        
            
        st.markdown("<br>", unsafe_allow_html=True)
        

        col_1,col_2=st.columns((4,4),gap='small')
        with col_1:
            # Check and drop 'month_year' column if exists
            # Ensure 'Order Date' is in datetime format
            # Ensure 'Order Date' is in datetime format
            filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"], errors='coerce')
            if 'month_year' in filtered_df.columns:
                filtered_df.drop(columns=['month_year'], inplace=True)
            # Create new 'month_year' column
            filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")

            # Create a new dataframe with sum of Sales grouped by month
            monthly_sales = filtered_df.groupby("month_year").agg({
                'Sales': 'sum'
            }).reset_index()
            
            # Convert 'month_year' to string format for plotting
            monthly_sales["month_year"] = monthly_sales["month_year"].astype(str)


            # Create an area chart with sales by month and profit as second trace
            fig = px.area(monthly_sales,
                x="month_year",  # Explicitly specify x-axis as the string column
                y="Sales",       # Explicitly specify y-axis as the numeric column
                labels={"Sales": "Sales Amount"},
                template="gridon",  # You can change this to your desired template
                height=500,
                width=500)
            
            # Smooth the curves for both lines
            fig.update_traces(mode="lines+markers", line_shape="spline")


            # Update layout with custom background and transparent areas
            fig.update_layout(
                title={
                    'text': "Sales Overview",  # Add the title
                    'y': 0.9,  # Vertical position of the title
                    'x': 0.5,  # Horizontal position of the title (centered)
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color="white")  # Customize the title font size and color
                },
                margin=dict(t=20, b=10),  # Adjusting the top and bottom margins
                xaxis=dict(showgrid=False),  # Remove x-axis gridlines
                yaxis=dict(showgrid=False),  # Remove y-axis gridlines
                plot_bgcolor='rgba(0, 0, 0,0.2)',  # Set the plot area background color with transparency
                paper_bgcolor='rgba(0, 0, 0, 0.4)',  # Set the paper (outer) background color with transparency
                
            )

            # Update traces with custom fill and colors for sales and profit
            fig.update_traces(
                fillcolor='rgba(8, 69, 162, 0.3)'  # Whitish color with some transparency
                
            )

            

            # Add data labels to the chart
            fig.update_traces(mode="lines+markers", textposition="top center")

            # Show the plot with Streamlit
            # Use a container to give width to the outer area of the graph
           
            st.plotly_chart(fig, use_container_width=True)  # Set use_container_width to False for custom width
        with col_2:
            # Aggregate profit data by Month
            profit_data = filtered_df.groupby(['Month'], as_index=False)['Profit'].sum()
            # Create a bar chart
            fig = go.Figure()

            # Add a single bar trace for profit
            fig.add_trace(go.Bar(
                x=profit_data['Month'],
                y=profit_data['Profit'],
                text=profit_data['Profit'].astype(str),
                textposition='outside',
                width=0.15,
                marker=dict(color='white', line=dict(width=1, color='rgba(255, 255, 255, 0.3)'), 
                opacity=0.9)  # Set border color and opacity for rounded effect
            ))
            # Update the layout of the bar chart
            fig.update_layout(
                title={
                    'text': "Monthly Profit Overview",  # Add the title text
                    'y': 0.9,  # Vertical position of the title
                    'x': 0.5,  # Horizontal position of the title (centered)
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color="white")  # Customize the title font size and color
                },
                xaxis_title='Month',
                yaxis_title='Profit',
                barmode='stack',
                height=500,
                margin=dict(l=50, r=10, t=30, b=30),
                xaxis=dict(
                    tickvals=profit_data['Month'].unique(),
                    ticktext=profit_data['Month'].unique(),
                    showgrid=False
                ),
                yaxis=dict(
                    showgrid=False
                ),
                bargap=0.1,
                plot_bgcolor='rgba(0, 0, 0,0.2)',  # Set the plot area background color with transparency
                paper_bgcolor='rgba(0, 0, 0, 0.4)',  # Set the paper (outer) background color with transparency
                
                font_color='white'
            )

            #Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)
      
        st.markdown("<br>", unsafe_allow_html=True)
        col_1,col_2=st.columns((5.5,2.5),gap='medium')
        with col_1:
            # Step 2: Detect a potential sales-related column
            sales_column = None
            for col in df.columns:
                if "sales" in col.lower():
                    sales_column = col
                    break
            # If no explicit sales column is found, select the first numeric column
            if sales_column is None:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    sales_column = numeric_columns[0]  # Select the first numeric column
                else:
                    st.error("No sales or numeric column found in the dataset.")
                    st.stop()
                
            # Step 3: Automatically detect date column or create one
            date_column = None
            for col in df.columns:
                if "date" in col.lower() or "time" in col.lower():
                    date_column = col
                    break
            # If no date column is found, create a sequential date range
            if date_column is None:
                st.warning("No date column found. Generating a daily time index.")
                df['Order Date'] = pd.date_range(start='2020-01-01', periods=len(df), freq='D')
                date_column = 'Order Date'
            # Step 4: Prepare the data for Prophet
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df = df.dropna(subset=[date_column, sales_column])  # Drop invalid rows


            # Step 5: Resample data to monthly level
            #monthly_sales = df.set_index(date_column).resample('M')[sales_column].sum().reset_index()
            monthly_sales = df.set_index(date_column).resample('M').sum().reset_index()

            monthly_sales.rename(columns={date_column: 'ds', sales_column: 'y'}, inplace=True)

            # Ensure there's enough data for forecasting
            if len(monthly_sales) < 2:
                st.error("Not enough data for monthly forecasting. Please upload a larger dataset.")
                st.stop()
            # Allow user to select the train/test split ratio
            split_ratio = st.sidebar.slider("Select Training Data Percentage", min_value=0.5, max_value=0.9, value=0.8)
                

            # Step 6: Split data into training and testing sets based on user input
            train_size = int(len(monthly_sales) * split_ratio)
            train = monthly_sales[:train_size]
            test = monthly_sales[train_size:]

            # Step 7: Fit the Prophet model on training data
            # Adding holiday effects (customize as needed)
                

            model = Prophet()
            model.fit(train)
            # Step 8: Make future dataframe for forecasting based on the test period
            #future = model.make_future_dataframe(periods=len(test), freq='M')
            future = model.make_future_dataframe(periods=len(test), freq='M')
            #future = model.make_future_dataframe(periods=len(test) + 30, freq='M')

            forecast = model.predict(future)

            # Step 9: Calculate accuracy metrics
            y_true = test['y'].values
            #y_pred = forecast['yhat'].iloc[train_size:].values  # Get the corresponding predictions
            y_pred = forecast['yhat'].iloc[train_size:].values
            #y_pred = forecast['yhat'].iloc[
            #train_size:train_size + len(test)].values  # Get predictions for the test period


                

            # Calculate MAE and MAPE
            mae = mean_absolute_error(y_true, y_pred)
            mape = mean_absolute_percentage_error(y_true, y_pred) * 100  # Convert to percentage
            accuracy = 100 - mape
            fig = go.Figure()


            # Add actual sales line (monthly)
            fig.add_trace(go.Scatter(x=monthly_sales['ds'], y=monthly_sales['y'], mode='lines', name='Actual Sales',
                        line=dict(color='#fafafa')))  # Actual Sales color

            # Add predicted sales line (monthly)
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicted Sales',
                        line=dict(color='#0075FF')))  # Predicted Sales color


            # Add lower and upper confidence intervals
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill=None, mode='lines',
                        line=dict(color='rgba(45, 64, 108, 0.2)'), showlegend=False, name='Lower Bound'))
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='lines',
                        line=dict(color='rgba(45, 64, 108, 0.2)'), showlegend=False, name='Upper Bound'))

            # Step 1
            # 
            #1: Update layout and display the chart
            fig.update_layout(
                    title="Sales Forecast",
                    yaxis_title="Sales",
                    xaxis_title="Date",
                    yaxis=dict(showgrid=False),
                    template="plotly_white",
                    height=580,
                        
                    paper_bgcolor="rgb(0,0,0,0.4)",  # Dark background color
                    plot_bgcolor="rgb(0,0,0,0.4)",  # Dark background color for the plot area
                    font=dict(color='#fafafa'),  # Light gray for text
                    #margin=dict(l=
                    #0, r=0, t=30, b=30)  # Adjust margins to reduce extra spacing
            )

            # Show plot in Streamlit
            st.plotly_chart(fig, use_container_width=True)
        with col_2:
            # Total Sales
            total_sales = filtered_df['Sales'].sum()

            # Predefined target scenarios
            target_options = {
                "Previous Year's Sales": total_sales * 1.1,  # 10% increase
                "Quarterly Sales Target": total_sales * 1.2,  # 20% increase
                "Annual Sales Goal": total_sales * 1.5  # 50% increase
            }
                
            # User selects a target scenario
            selected_target = st.selectbox(
                "Select Target Scenario",
                options=list(target_options.keys())
            )
            # Get the target sales value based on the selected scenario
            target_sales = target_options[selected_target]
            # Calculate the progress
            progress_percentage = (total_sales / target_sales) * 100
            progress = min(progress_percentage, 100)
            # Create the circular progress bar
            bar_color = "#0F51AF" if progress_percentage <= 100 else "#06BD91"  # Red for overachievement
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=progress_percentage,
                gauge={
                    #'axis': {'range': [0, max(100, progress_percentage)]},
                    'axis': {'range': [0, 100], 'visible': False},
                    #'bar': {'color': "rgba(14, 67, 251, 0.5)", 'line': {'color': 'rgba(0,0,0,0)', 'width': 0}},  # Add transparency to the bar color
                    'bar': {'color': "#fafafa", 'line': {'color': '#fafafa', 'width': 0}},  # Add transparency to the bar color
                    'bgcolor': "rgb(0,0,0,0.4)",
                    'steps': [
                        {'range': [0, 100], 'color': "#0B1739"}
                    ]

                },
                title={'text': "Sales Target Completion", 'font': {'size': 24, 'color': "#D3D3D3"}},
                number={'suffix': "%", 'font': {'color': "#D3D3D3"}}
            ))
            # Update the layout for the chart
            fig.update_layout(
                paper_bgcolor="rgb(0,0,0,0.4)",
                font=dict(color='#D3D3D3'),
                #height=320,  # Adjust height
                #width=450,   # Adjust width
                margin=dict(l=10, r=10, t=10, b=10),
            )
            # Create a container with specific dimensions and background color
            with st.container():  # Use st.container() for your layout needs
                st.markdown(
                    """
                    <div style="background-color: rgb(0,0,0,0.4); padding: 20px; display: flex; flex-direction: column;">
                    """,
                unsafe_allow_html=True
                )

            # Display the chart in Streamlit
            st.plotly_chart(fig)
            st.markdown(
                """
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            

        

        
           