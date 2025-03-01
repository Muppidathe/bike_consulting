import streamlit as st
pages={"DashBoard":[st.Page(page="dashboard.py",title="dashboard",icon=":material/bar_chart_4_bars:")],
       "Manage vechile":[st.Page(page="add_vehicle.py",title="create vechile info",icon=":material/add:"),
                         st.Page(page="add_vehicle_expenses.py",title="add expenses to vechile",icon=":material/add_notes:"),
                         st.Page(page="edit_vehicle.py",title="Edit Vehicles",icon=":material/list_alt:"),
                         st.Page(page="edit_vehicle_expenses.py",title="Edit Vehicle Expenses",icon=":material/list_alt:"),
                         st.Page(page="delete_vehicle.py",title="delete vehicle",icon=":material/list_alt:"),
                         st.Page(page="list_all_vehicle.py",title="vehicle list",icon=":material/list_alt:")],
       "Office Management":[st.Page(page="misc.py",title="add office expenses",icon=':material/payments:')]}

pg=st.navigation(pages,)
pg.run()