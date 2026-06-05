import pandas as pd
from numpy.random import default_rng as rng


def get_chart_data_sample() -> pd.DataFrame:
	return pd.DataFrame(rng(0).standard_normal((20, 3)), columns=["a", "b", "c"])


if __name__ == "__main__":
	import streamlit as st

	st.area_chart(get_chart_data_sample())
