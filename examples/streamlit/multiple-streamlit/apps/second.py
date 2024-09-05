import random
import streamlit as st
import plotly.graph_objects as go


def main():
    st.title("Second App")

    if st.button("Generate Scatter Plot"):
        # Generate random data for x and y
        x = [random.random() for _ in range(50)]
        y = [random.random() for _ in range(50)]

        # Create the scatter plot using Plotly
        fig = go.Figure(data=go.Scatter(x=x, y=y, mode="markers"))
        fig.update_layout(
            title="Random Scatter Plot", xaxis_title="X-axis", yaxis_title="Y-axis"
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()
