import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'add_exp_result' not in st.session_state:
    st.session_state['add_exp_result']=()
mydb,dbcursor=connection()
def fetch_vehicle(vehicle_no):
    try:
        query = "SELECT image,vehicle_no,model_name,cc,purchase_date,cost_price,fine,sales_date,sales_price,model_year FROM vehicle WHERE vehicle_no = %s"
        dbcursor.execute(query, (vehicle_no,))
        result = dbcursor.fetchone()
        if result:
            return result
        else:
            st.error("No Record Found For This Number")
            st.stop()
            return None

    except Exception as e:
        st.error(f'while fetching image {e}')
        st.stop()
        return None

def add_expenses(vehicle_no,expenses_date,description,expenses):
    if not expenses_date:
        st.error('please provide expense date')
    elif not description:
        st.error("please provide description")
    elif not expenses:
        st.error("please provide expense amount")
    else:
        try:
            vehicle_add_query = """
                INSERT INTO vehicle_expenses (vehicle_num,vehicle_expenses_date,description,amount)
                VALUES (%s, %s, %s, %s);
            """
            dbcursor.execute(vehicle_add_query,(vehicle_no,expenses_date,description,expenses))
            mydb.commit()
            st.success('vehicle Expenses has added')
            st.balloons()
        except Exception as e:
            st.error(f"error while inserting{e}")
with st.form("fetch_details"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(vehicle_no)
        st.session_state.add_exp_result=result
result=st.session_state.add_exp_result
if result:
    with st.form('Expenses',enter_to_submit=False):
        if result[0]:  # If image exists
                image_path = result[0] 
                col=st.columns(3)
                with col[0]:
                    st.image(image_path,use_container_width=True)
        st.text_input(placeholder="R15",label="Vehicle Name",value=result[2],disabled=True)
        st.number_input(placeholder="2012",label="Model",value=result[9],disabled=True)
        st.number_input(placeholder="150",label="CC",value=result[3],disabled=True)
        st.date_input(label="Purchasing Date",value=result[4],disabled=True)
        st.number_input(placeholder="80000",label="Cost Price",value=result[5],disabled=True)
        st.number_input(placeholder="1500",label="Fine Amount",value=result[6],disabled=True)
        expenses_date=st.date_input(label="Expenses Date",value=date.today())
        description=st.text_input(placeholder="Tyre,Painting,etc..",label="Description").upper()
        expenses=st.number_input(placeholder="500",label="Expenses",value=None,min_value=0,)
        submit=st.form_submit_button(label="Add Expenses")
        if submit:
            add_expenses(result[1],expenses_date,description,expenses)