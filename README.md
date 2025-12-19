# Global Simulation of Forest Fires using Cellular Automata

Implemented model from the article [Modelling of wildland-urban interface fire spread with the heterogeneous
cellular automata model](https://www.sciencedirect.com/science/article/pii/S136481522030952X?ref=pdf_download&fr=RR-2&rr=99fa177d2e3ac80e)

# Structure 

- models: file with environment paraments
- model: file with implemented model
- utils: usefull constants
- example: example of use
- demo: ipynb with simulations

# How to use? 

## Command Line Usage

1. import the model: ```from model.main import WUIModel```
2. init with your params
3. ignite some cell/house: ```ignite_forest/ignite_house```
4. run the simulation with time: ```model.run(300)```
5. create a plot with: ```plot_colormap_fire```
See examples in Demo.ipynb

## Web Interface

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the web application:
```bash
streamlit run app.py
```

3. Open your browser - the app will automatically open at `http://localhost:8501`

Result will be a plot with simulation: 

![Иллюстрация к проекту](https://github.com/randnull/forest_fire_ca/blob/83a800ce538f37fd4b14d52949987bfb7f8dceb9/examples/save2025-11-16.png)
