import streamlit as st
import tasks
import functions

st.title("Manual Polling")

st.write("Optionally enter a user ID to store status and results in the database.")

user_id = st.text_input("User ID:", key="user_id_input")


if st.button("Run expensive computation"):
    job_id = tasks.enqueue_task(functions.expensive_computation, user_id=user_id)
    st.write("Submitted job...")
    st.session_state["job_id"] = job_id

if st.session_state.get("job_id") and st.button("Check job status"):
    status, result = tasks.check_job_status(st.session_state["job_id"])

    if status == tasks.JobStatus.PENDING:
        st.write("Job is still pending...")
    elif status == tasks.JobStatus.FINISHED:
        st.write(f"Job finished with result: {result}")
    elif status == tasks.JobStatus.FAILED:
        st.write("Job failed...")
    elif status == tasks.JobStatus.INVALID:
        st.write("Job ID is invalid...")
