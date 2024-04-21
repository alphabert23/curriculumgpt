import streamlit as st
from app_functions import *
import os
import base64
import json
import time
import datetime


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

if "doc_path" not in st.session_state:
    st.session_state.doc_path = None
if 'execution_time' not in st.session_state:
    st.session_state.execution_time = None
if 'output_file_path' not in st.session_state:    
    st.session_state.output_file_path= None
    st.session_state.output_file_name = None

if 'learning_outcomes' not in st.session_state:
    st.session_state.learning_outcomes = None

# Title
st.title("GPT Course Outline Generator")

# Input course details
course_title = st.text_input("Course Title")
course_description = st.text_area("Course Description", height=100)
instructor_name = st.text_input("Instructor Name",placeholder="e.g. Dr. Juan Dela Cruz")
target_students = st.text_input("Target Students",placeholder="e.g. 3rd year BS Computer Science students")

col1, col2 = st.columns(2)
with col1:
    credit_units = st.number_input("Credit Units", value=3)
    total_hours = st.number_input("Total Hours", value=54)
    weekly_hours = st.number_input("Weekly Hours", value=3)

with col2:
    number_of_topics = st.number_input("Number of Topics", value=5)
    citation_style = st.selectbox("Citation Style", ["APA", "MLA", "Chicago", "Harvard"])
    document_title = st.text_input("Output Title",placeholder='default value: {course title}.docx')

# model = st.selectbox('Choose gpt model',['gpt-4-turbo-preview','gpt-3.5-turbo'])
model = 'gpt-4-turbo-preview'
# Combing the course details into a single string
course_details = f"""Course Title: {course_title}
Course Description: {course_description}
Instructor Name: {instructor_name}
Credit Units: {credit_units}
Target Students: {target_students}
Total Hours: {total_hours}
Class Hours per Week: {weekly_hours}"""


if st.button("Generate Course Outline",use_container_width=True):
    st.session_state.start_time = time.time()

    with st.spinner("Generating Course Topics..."):
        # Genereate topics and search queries
        queries =  generate_queries(course_details=course_details)
    st.success("Queries Generated")

    with st.spinner("Searching Online for Reference Materials..."):
        # Get Search Results from Google Scholar
        total_search_results = get_search_results(json.loads(queries))
    st.success("Search Results Generated")

    with st.spinner("Generating Learning Outcomes..."):
        # Get Learning Outcomes from GPT-4
        st.session_state.learning_outcomes = generate_learning_outcomes(course_details=course_details, 
                                                       total_search_results=total_search_results, 
                                                       citation_style=citation_style,
                                                       number_of_topics=number_of_topics,
                                                       model=model)

    learning_outcomes = st.session_state.learning_outcomes

    with st.spinner("Generating Course Outline..."):
        # Generate Course Outline
        course_outline = generate_course_outline(course_details=course_details, 
                                                learning_outcomes=learning_outcomes, 
                                                number_of_topics=number_of_topics, 
                                                total_hours=total_hours, 
                                                weekly_hours=weekly_hours,
                                                model=model) 
        course_outline_json = json.loads(course_outline)

    # Create word document from course outline json
    st.session_state.doc_path = create_word_document_from_json(course_outline_json,title=document_title)
    end_time = time.time()
    st.session_state.execution_time = end_time - st.session_state.start_time
    st.session_state.start_time = None

    # Check if the 'outputs' folder exists, if not create it
    outputs_folder = 'course_outline_outputs'
    if not os.path.exists(outputs_folder):
        os.makedirs(outputs_folder)

    # Save output document in the 'outputs' folder
    if document_title == '':
        document_title = f"{course_title.replace(' ','_')}_{instructor_name.replace(' ','_')}_Course_Outline"
    st.session_state.output_file_name = f"{document_title}.docx"
    st.session_state.output_file_path = os.path.join(outputs_folder, st.session_state.output_file_name)
    with open(st.session_state.doc_path, "rb") as file:
        with open(st.session_state.output_file_path, "wb") as output_file:
            output_file.write(file.read())

    
    # Log course details, execution time, and save location
    log_details = {
        "Course Details": {
            "Course Title": course_title,
            "Course Description": course_description,
            "Instructor Name": instructor_name,
            "Credit Units": credit_units,
            "Target Students": target_students,
            "Total Hours": total_hours,
            "Class Hours per Week": weekly_hours
        },
        "Model": model,
        "Execution Time": st.session_state.execution_time,
        "Save Location": st.session_state.output_file_path,
        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    log_file = 'output_logs.json'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_details)
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=4)

if st.session_state.output_file_path:
    st.subheader("Learning Outcomes")
    st.write(st.session_state.learning_outcomes)

    # Provide download button/link
    st.write(f"Execution Time: {st.session_state.execution_time}")
    with open(st.session_state.output_file_path, "rb") as file:
        btn = st.download_button(   
            label="Download Course Outline",
            data=file,
            file_name=st.session_state.output_file_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
