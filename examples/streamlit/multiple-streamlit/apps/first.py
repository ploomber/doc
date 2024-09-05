import random
import streamlit as st
import matplotlib.pyplot as plt


def main():
    st.title("First App")

    if st.button("Generate Scatter Plot"):
        # Generate random data for x and y
        x = [random.random() for _ in range(50)]
        y = [random.random() for _ in range(50)]

        # Create the scatter plot
        fig, ax = plt.subplots()
        ax.scatter(x, y)
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        ax.set_title("Random Scatter Plot")

        # Display the plot in Streamlit
        st.pyplot(fig)


if __name__ == "__main__":
    main()
