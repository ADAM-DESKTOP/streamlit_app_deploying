import streamlit as st
import os

# Introducing The Developer and The Creator Functions 


def show_dev_info():
        

    with st.container(height=300, border=True):
            dev_img = r"ADAM'S_IMAGE.png"
            
            developer_image = st.image(image=dev_img)
            developer_header = st.subheader("Adam")
            developer_describtion = st.caption("Describtion: The Developer of the website, He is 15 Years old and He is an Egyptian. He Has a Passion In Programming So He Learned and Made This Project")
            
            hide_devs_info_btn = st.button("Hide info", hide_info)

            if hide_devs_info_btn:
                hide_info(developer_image, developer_header, developer_describtion)

    st.divider()

def show_creator_info():
    with st.container(height=300, border=True, ):
        creator_img = r"FARIDA'S_IMAGE.png"
        
        creator_image = st.image(image=creator_img)
        creator_header = st.subheader("Farida")
        creator_describtion = st.caption("Describtion: The Creator of the accesories, She is 10 Years old and She is an Egyptian She has a passion in Creating accesories so She learned and made these accesories")
        
        hide_creator_info_btn = st.button("Hide info", hide_info)

        if hide_creator_info_btn:
            hide_info(creator_image, creator_header, creator_describtion)

    st.divider()

def hide_info(**param):
    param = False

def show_specs(type_nb, type_price):

    st.markdown(f"**Specifications:**")
    st.markdown(f"                  _Type: {type_nb}_")
    st.markdown(f"                  _price: {type_price}$_")

# Loading Images
images_paths = [
r"bracelet (1).jpg",
r"bracelet (2).jpg",
r"bracelet (3).jpg",
r"bracelet (4).jpg",
r"bracelet (5).jpg",
r"bracelet (6).jpg",
r"bracelet (7).jpg",
r"bracelet (8).jpg",
r"bracelet (9).jpg",
r"bracelet (10).jpg",
r"necklace (1).jpg",
r"necklace (2).jpg",
r"necklace (3).jpg",
r"necklace (4).jpg",
r"necklace (5).jpg",
r"necklace (6).jpg",
r"necklace (7).jpg",
r"ring (1).jpg"
]

st.title("Hand Accessories by Farida")

# Initialize session state to track the current image index
if "current_image_index" not in st.session_state:
    st.session_state.current_image_index = 0

# Create a layout with three columns
col1, col2, col3 = st.columns([1, 6, 1])

# Left button (Previous)
with col1:
    if st.button("Previous", key="prev_btn"):  # Add unique key
        st.session_state.current_image_index = (st.session_state.current_image_index - 1) % len(images_paths)

# Center image and text
if st.session_state.current_image_index + 1 in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
    with col2:
        current_image = images_paths[st.session_state.current_image_index]
        image_col, _, text_col = st.columns([2, 1, 4])  # Adjust column widths as needed
        with image_col:
            st.image(current_image, caption=f"Bracelet {st.session_state.current_image_index + 1}", use_container_width=True)
        with text_col:
            type_b = "Bracelet"
            bprice = "25"
            st.write(f"**Description for Bracelet {st.session_state.current_image_index + 1}:**")
            st.caption("This is a beautiful Bracelet created by Farida. It is designed with care and creativity to enhance your style.")
            show_btn = st.checkbox("Show Specs")
            if show_btn:
                show_specs(type_nb=type_b, type_price=bprice)

if st.session_state.current_image_index + 1 in (11, 12, 13, 14, 15, 16, 17):
    with col2:
        current_image = images_paths[st.session_state.current_image_index]
        image_col, _, text_col = st.columns([2, 1, 4])  # Adjust column widths as needed
        with image_col:
            st.image(current_image, caption=f"Necklace {st.session_state.current_image_index + 1}", use_container_width=True)
        with text_col:
            type_bn = "Necklace"
            nprice = "50"
            st.write(f"**Description for Necklace {st.session_state.current_image_index + 1}:**")
            st.caption("This is a beautiful Necklace created by Farida. It is designed with care and creativity to enhance your style.")
            show_btn = st.checkbox("Show Specs")
            if show_btn:
                show_specs(type_nb=type_bn, type_price=nprice)

# Right button (Next)
with col3:
    if st.button("Next", key="next_btn"):  # Add unique key
        st.session_state.current_image_index = (st.session_state.current_image_index + 1) % len(images_paths)

developer_btn = st.button("Developer's info", on_click=show_dev_info)
creator_btn = st.button("Creator's info", on_click=show_creator_info)

