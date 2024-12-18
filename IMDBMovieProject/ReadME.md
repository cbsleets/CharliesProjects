# **Personalized Movie Recommendation System**

## **Project Overview**
This project focuses on building a personalized movie recommendation system using publicly available IMDb datasets. The goal is to predict personalized movie ratings for a user based on their past ratings, leveraging advanced machine learning models. It also incorporates feature engineering, exploratory data analysis (EDA), and model evaluation.

The project allowed for refining data preprocessing techniques, adding meaningful features, and experimenting with advanced models like Neural Networks, Support Vector Regression (SVR), Random Forest, and XGBoost.

---

## **File Hierarchy**

IMDB Final Project - Charles Blanch
│
├── IMDB Model Data
│   ├── imdb_data.csv
│   ├── name.basics.tsv
│   ├── ratings.csv
│   ├── reviewed_data.csv
│   ├── title.akas.tsv
│   ├── title.basics.tsv
│   ├── title.crew.tsv
│   ├── title.principals.tsv
│   ├── title.ratings.tsv
│
├── PlotImages
│   ├── Chart1.png
│   ├── Chart2.png
│   ├── Chart3.png
│   ├── Chart4.png
│   ├── PieChart.png
│
├── FinalProjectEDA.ipynb
├── FinalProjectEDADataFrameCreationForModel.ipynb
├── FinalProjectModel.ipynb
├── FinalReport.ipynb
├── README.md

---

## **Steps Taken**
1. **Data Collection and Preprocessing**:
   - Merged multiple IMDb datasets located in the `IMDB Model Data/` folder.
   - Created meaningful dummy variables and engineered features like weighted variables, multiplicative factors, and runtime flags.
   - Cleaned missing data and handled multi-category columns (e.g., genres, directors).

2. **Exploratory Data Analysis (EDA)**:
   - Conducted EDA in `FinalProjectEDA.ipynb` to identify trends and correlations in user ratings.
   - Visualized data distributions and key insights using boxplots, scatterplots, and bar charts.

3. **Modeling**:
   - Explored models like Neural Networks, XGBoost, Random Forest, SVR, and LassoCV in `FinalProjectModel.ipynb`.
   - Conducted hyperparameter tuning using grid search for optimal model performance.

4. **Final Report**:
   - Compiled all findings into `FinalReport.ipynb`, which provides a comprehensive overview of the project.

---

## **Instructions to Run**
### **Dependencies**
The following Python libraries are required:
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `xgboost`
- `tensorflow`
- `scikeras`
- `GridSearchCV`

### **Steps**
1. Clone this repository:
   ```bash
   git clone https://gitlab.bucknell.edu/cb072/csci205_labs

2. Download the data from here and place into IMDB Model Data folder https://drive.google.com/drive/u/1/folders/1eFj0ng0o84OF1UWVRjQvj3Fowl1S5niE 

3. Run the FinalProjectEDADataFrameCreationForModel file

4. Run the FinalProjectEDA file to see Any Visualizations

5. Run the FinalProjectModel file to get your predictions - Note you will need to tune the hyperparameters yourself 


Video Presentation

The project video is hosted on MediaSpace
Click this link to view the video : https://mediaspace.bucknell.edu/media/t/1_ulzh5r8t 


