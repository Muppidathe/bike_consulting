import streamlit as st
pages={"Manage vechile":[st.Page(page="vehicle_dashboard.py",title="Dashboard",icon=":material/bar_chart_4_bars:"),
                        st.Page(page="vehicle_add.py",title="Create Vehicle Info",icon=":material/add:"),
                         st.Page(page="vehicle_expenses_add.py",title="Add Expenses To Vehicle",icon=":material/add_notes:"), 
                         st.Page(page="vehicle_sales.py",title="Vehicle Sold",icon=":material/check_small:"),
                         st.Page(page="vehicle_view.py",title="View Vehicle",icon=":material/visibility:"),
                         st.Page(page="vehicle_edit.py",title="Edit Vehicles",icon=":material/edit:"),
                         st.Page(page="vehicle_delete.py",title="Delete Vehicle",icon=":material/delete:")],
       "Office Management":[st.Page("office_dashboard.py",title="Dashboard",icon=':material/payments:'),
                            st.Page(page="office_expenses_create.py",title="Add Office Expenses",icon=':material/add:'),
                            st.Page(page="office_expenses_edit.py",title="Edit Office Expenses",icon=':material/edit:'),
                            st.Page(page="office_expenses_delete.py",title="Delete Office Expenses",icon=":material/delete:")],
       "Bills Payable":[st.Page(page="bills_dashboard.py",title="Dashboard",icon=":material/payments:"),
                        st.Page(page="bills_payable_create.py",title="Create Bills Payable",icon=':material/add:'),
                        st.Page(page="bills_add_deduct.py",title="Add/Deduct Bills",icon=':material/add_notes:'),
                        st.Page(page="bills_view.py",title="View Bills",icon=":material/visibility:"),
                        st.Page(page="bills_edit.py",title="Edit Bills",icon=':material/edit:'),
                        st.Page(page="bills_delete.py",title="Delete Bills",icon=':material/delete:')
                        ],
       "Business Insights":[st.Page(page="chat_bot.py",title="Chat bOt",icon=":material/smart_toy:")]}


pg=st.navigation(pages,)
pg.run()