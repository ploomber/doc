#!/bin/bash
python app.py &
streamlit run streamlit_app.py &
wait
