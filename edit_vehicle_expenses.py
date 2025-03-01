import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'edit_exp_result' not in st.session_state:
    st.session_state['edit_exp_result']=[]
mydb,dbcursor=connection()
def fetch_image(vehicle_no):
    try:
        query = "SELECT image FROM vehicle  WHERE vehicle_no = %s"
        dbcursor.execute(query, (vehicle_no,))
        result = dbcursor.fetchone()
        if result:
            if result[0]:  # If image exists
                image_path = result[0] 
                col=st.columns(3)
                with col[0]:
                    st.image(image_path,use_container_width=True)

        else:
            st.error("No Record Found For This Number")
            st.stop()
    except Exception as e:
        st.error(f'while fetching image {e}')
        st.stop()
def fetch_vehicle(vehicle_no):
    try:
        query="select id,vehicle_num,vehicle_expenses_date,description,amount from vehicle_expenses WHERE vehicle_num = %s;"
        dbcursor.execute(query, (vehicle_no,))
        result = dbcursor.fetchall()
        if result:
            return result
        else:
            st.error("No Record Found For This Number")
            st.stop()
            return None

    except Exception as e:
        st.error(f'while fetching expenses {e}')
        st.stop()
        return None

def edit(id,vehicle_no,expense_date,desc,expense):
    vehicle_edit_query = """
        UPDATE vehicle_expenses
        SET  vehicle_num = %s ,vehicle_expenses_date=%s,description=%s,amount=%s
        WHERE id = %s
        """
    values=(vehicle_no,expense_date,desc,expense,id)
    try:
        dbcursor.execute(vehicle_edit_query,values)
        mydb.commit()
        st.success('vehicle info edited')
        st.balloons()
    except Exception as e:
        st.error(f"Error While Editing {e}")
#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(vehicle_no)
        fetch_image(vehicle_no)
        st.session_state.edit_exp_result=result
#form2
result=st.session_state.edit_exp_result
if result:
    for i in result:
        with st.form(key=str(i[0])):
            id=i[0]
            vehicle_no=i[1]
            expense_date=st.date_input(label="expense date",value=i[2])
            desc=st.text_input(label="Description",value=i[3])
            expense=st.number_input(label="expenses",value=i[4],min_value=0)
            submit=st.form_submit_button(label="Edit")
            if submit:
                edit(id,vehicle_no,expense_date,desc,expense)