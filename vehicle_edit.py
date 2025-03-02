import streamlit as st
from db import connection
from datetime import date
import os
image=None
if 'edit_result' not in st.session_state:
    st.session_state['edit_result']=()
if 'edit_exp_result' not in st.session_state:
    st.session_state['edit_exp_result']=[]
mydb,dbcursor=connection()
def save_uploaded_file(uploaded_file,vehicle_no):
    ext=uploaded_file.name.split('.')[-1]
    filename=str(vehicle_no)+"."+ext
    file_path = os.path.join("static",'vehicle',filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
def fetch_vehicle(vehicle_no):
    try:
        query = "SELECT image,vehicle_no,model,cc,purchase_date,cost_price,fine,buyer_name,ifnull(aadhar_no,0),phone_no,sales_date,sales_price,received_amount FROM vehicle  WHERE vehicle_no = %s"

        dbcursor.execute(query, (vehicle_no,))
        result = dbcursor.fetchone()
        if result:
            return result
        else:
            st.error("No Record Found For This Number")
            st.stop()
            return None

    except Exception as e:
        st.error(f'while fetching details {e}')
        st.stop()
        return None
def fetch_expenses(vehicle_no):
    try:
        query="select id,vehicle_num,vehicle_expenses_date,description,amount from vehicle_expenses WHERE vehicle_num = %s;"
        dbcursor.execute(query, (vehicle_no,))
        result = dbcursor.fetchall()
        if result:
            return result
        else:
            return None

    except Exception as e:
        st.error(f'while fetching expenses {e}')
        st.stop()
        return None

def edit_vehilce(vehicle_no,images,model,cc,purchase_date,cost_price,fine,sales_date,sales_price):
    if not fine:
        fine=0
    if not sales_price:
        sales_price=0
    if not model:
        st.error("enter the model name")
    elif not cc:
        st.error("enter the cc")
    elif cc==1:
        st.error("enter the cc")
    elif not purchase_date:
        st.error("purchase date required")
    elif not cost_price:
        st.error("cost price required")
    elif cost_price==2:
        st.error("cost price required")
    else:
        if images:
            image_path=save_uploaded_file(images,vehicle_no)
            vehicle_edit_query = """
            UPDATE vehicle
            SET image = %s, model = %s ,cc= %s,purchase_date=%s,cost_price=%s,fine=%s,sales_date=%s,sales_price=%s
            WHERE vehicle_no = %s
            """
            values=(image_path,model,cc,purchase_date,cost_price,fine,sales_date,sales_price,vehicle_no)
        else:
            vehicle_edit_query = """
            UPDATE vehicle
            SET  model = %s ,cc= %s,purchase_date=%s,cost_price=%s,fine=%s,sales_date=%s,sales_price=%s
            WHERE vehicle_no = %s
            """
            values=(model,cc,purchase_date,cost_price,fine,sales_date,sales_price,vehicle_no)
        try:
            dbcursor.execute(vehicle_edit_query,values)
            mydb.commit()
            st.success('vehicle info edited')
            st.balloons()
        except Exception as e:
            st.error(f"error while updating vehicle info {e}")
def edit_expenses(id,vehicle_no,expense_date,desc,expense):
    if not expense_date:
        st.error('please provide expense date')
    elif not desc:
        st.error("please provide description")
    elif not expense:
        st.error("please provide expense amount")
    else:
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
        st.session_state.edit_result=result
        result=fetch_expenses(vehicle_no)
        st.session_state.edit_exp_result=result
#form2
result=st.session_state.edit_result
if result:
    with st.form('Expenses'):
        vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number",value=result[1],disabled=True)
        if result[0]:  # If image exists
                image_path = result[0]
                col=st.columns(3)
                with col[0]:
                    st.image(image_path,use_container_width=True)
        image_inp=st.file_uploader(label="Vechile Image",type=['png', 'jpg','jpeg'])
        model=st.text_input(placeholder="R15",label="Model",value=result[2])
        cc=st.number_input(placeholder="150",label="CC",value=result[3])
        purchase_date=st.date_input(label="Purchasing Date",value=result[4])
        cost_price=st.number_input(placeholder="80000",label="Cost Price",value=result[5])
        fine=st.number_input(placeholder="1500",label="Fine Amount",value=result[6])
        name=st.text_input(placeholder="muppidathi",label='Buyer Name',value=result[7])
        aadhar_no=st.number_input(placeholder='94** **** ****',label='Aadhar no',value=int(result[8]))
        phone_no=st.number_input(placeholder='1234****',label='phone no',value=int(result[9]))
        sales_date=st.date_input(label="Sales Date",value=result[10])
        sales_price=st.number_input(placeholder="80000",label="Cost Price",value=result[11])
        received_amount=st.number_input(placeholder="80000",label="received amount",value=result[12])
        submit=st.form_submit_button(label="Edit")
        if submit:
            edit_vehilce(vehicle_no,image_inp,model,cc,purchase_date,cost_price,fine,sales_date,sales_price)


#form3
st.header("Expenses")
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
                edit_expenses(id,vehicle_no,expense_date,desc,expense)
else:
    st.info("no Expenses found for this vehicle")