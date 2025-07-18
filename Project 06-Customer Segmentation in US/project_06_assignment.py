# -*- coding: utf-8 -*-
"""Project 06-Assignment.ipynb

Automatically generated by Colab.



# **6.5. Small Business Owners in the United States🇺🇸**

In this assignment, you're going to focus on business owners in the United States. You'll start by examining some demographic characteristics of the group, such as age, income category, and debt vs home value. Then you'll select high-variance features, and create a clustering model to divide small business owners into subgroups. Finally, you'll create some visualizations to highlight the differences between these subgroups. Good luck! 🍀
"""

# Import libraries here
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import pickle
from IPython.display import VimeoVideo
from scipy.stats.mstats import trimmed_var
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

"""## **Prepare Data**

### **Import**

Let's start by bringing our data into the assignment.

**Task 6.5.1**

Read the contents of the file data/SCFP2019.csv.gz in a DataFrame df . Run Check Activity to verify your results.
"""

df = pd.read_csv("data/SCFP2019.csv.gz")
print("df shape:", df.shape)
df.head()

"""### **Explore**

As mentioned at the start of this assignment, you're focusing on business owners. But what percentage of the respondents in df are business owners?

**Task 6.5.2**

Determine the proportion of respondents in df who are business owners by analyzing the "HBUS" column. Assign the result to the variable prop_biz_owners .
"""

prop_biz_owners = (df["HBUS"] == 1).mean()
print("proportion of business owners in df:", prop_biz_owners)

"""Is the distribution of income different for business owners and non-business owners?

**Task 6.5.3**

Create a DataFrame named df_inccat that shows the normalized frequency of income categories for both business owners and non-business owners using the "INCCAT" and "HBUS" columns.
"""

inccat_dict = {
    1: "0-20",
    2: "21-39.9",
    3: "40-59.9",
    4: "60-79.9",
    5: "80-89.9",
    6: "90-100",
}
df_inccat = (
    df["INCCAT"]
    .replace(inccat_dict)
    .groupby(df["HBUS"])
    .value_counts(normalize=True)
    .rename("frequency")
    .to_frame()
    .reset_index()
)

df_inccat

"""**Slight Code Change**

In the following task, you'll notice a small change in how plots are created compared to what you saw in the lessons. While the lessons use the global matplotlib method like plt.plot(...), in this task, you are expected to use the object-oriented (OOP) API instead. This means creating your plots using fig, ax = plt.subplots() and then calling plotting methods on the ax object, such as ax.plot(...), ax.hist(...), or ax.scatter(...).

If you're using pandas’ or seaborn’s built-in plotting methods (like df.plot() or sns.lineplot()), make sure to pass the ax=ax argument so that the plot is rendered on the correct axes.

This approach is considered best practice and will be used consistently across all graded tasks that involve matplotlib.

**Task 6.5.4**

Create a grouped bar chart that compares the income category distribution of business owners vs. non-business owners using the df_inccat DataFrame.

Use sns.barplot() with following plot details :

* X-axis : "INCCAT"

* Y-axis : "frequency"

* hue : "HBUS"

* Set the x-axis order using inccat_dict.values().

* Use the provided fig, ax = plt.subplots() .

* For the X-axis, Y-axis, and title label, refer to the expected outcome.
"""

fig, ax = plt.subplots()

sns.barplot(
    data=df_inccat,
    x="INCCAT",
    y="frequency",
    hue="HBUS",
    order=inccat_dict.values(),
    ax=ax
)

# Labeling
ax.set_xlabel("Income Category")
ax.set_ylabel("Frequency (%)")
ax.set_title("Income Distribution: Business Owners vs. Non-Business Owners");

"""We looked at the relationship between home value and household debt in the context of the the credit fearful, but what about business owners? Are there notable differences between business owners and non-business owners?

**Task 6.5.5**

Use sns.scatterplot() to create a scatter plot to examine the relationship between household debt and home value, distinguishing between business owners and non-business owners.

Plot Details:

* x-axis:Household Debt

* y-axis:Home Value

* hue:"HBUS"

* palette:deep

* title :Home Value vs. Household Debt

* Use the provided fig, ax = plt.subplots(figsize=(8,5))
"""

# Plot "HOUSES" vs "DEBT" with hue as business ownership
fig, ax = plt.subplots(figsize=(8, 5))

sns.scatterplot(
    data=df,
    x="DEBT",
    y="HOUSES",
    hue="HBUS",
    palette="deep",
    ax=ax
)

# Set plot labels and title
ax.set_xlabel("Household Debt")
ax.set_ylabel("Home Value")
ax.set_title("Home Value vs. Household Debt");

"""For the model building part of the assignment, you're going to focus on small business owners, defined as respondents who have a business and whose income does not exceed $500,000.

**Task 6.5.6**

Create a new DataFrame named df_small_biz that includes only respondents who are business owners (HBUS) and have household income less than $500,000 (5e5). Use a boolean mask to apply both conditions and filter the df DataFrame accordingly. Run Check Activity to verify your results.
"""

mask = (df["HBUS"] == 1) & (df["INCOME"] <= 500000)
df_small_biz = df[mask]# use the column `mask` defined above
print("df_small_biz shape:", df_small_biz.shape)
df_small_biz.head()

"""We saw that credit-fearful respondents were relatively young. Is the same true for small business owners?

**Task 6.5.7**

Create a histogram from the "AGE" column in df_small_biz with 10 bins.

Plot Details :

* X-axis :"Age"

* Y-axis :"Frequency (count)"'

* Title :"Small Business Owners: Age Distribution"

* Use fig, ax = plt.subplots()
"""

# Plot histogram of "AGE"
fig, ax = plt.subplots()
df_small_biz["AGE"].plot(
    kind="hist",
    bins = 10,
    ax = ax
)

# Set axis labels and title
ax.set_xlabel("Age")
ax.set_ylabel("Frequency (count)")
ax.set_title("Small Business Owners: Age Distribution")

plt.show()

"""So, can we say the same thing about small business owners as we can about credit-fearful people?

Let's take a look at the variance in the dataset.

**Task 6.5.8**

Calculate the variance for all the features in df_small_biz, and create a Series top_ten_var with the 10 features with the largest variance.
"""

# Calculate variance
variances = df_small_biz.var(numeric_only=True)

# Get top 10 features in ascending order (largest at bottom)
top_ten_var = variances.sort_values(ascending=True).tail(10)

top_ten_var

"""We'll need to remove some outliers to avoid problems in our calculations, so let's trim them out.

**Task 6.5.9**

Calculate the trimmed variance for the features in df_small_biz. Your calculations should not include the top and bottom 10% of observations. Then create a Series top_ten_trim_var with the 10 features with the largest variance.
"""

# Calculate trimmed variance
top_ten_trim_var = df_small_biz.apply(trimmed_var, limits=(0.1, 0.1)).sort_values().tail(10)

top_ten_trim_var

"""Let's do a quick visualization of those values.

**Task 6.5.10**

Create a horizontal bar chart showing the top 10 features with the highest trimmed variance among small business owners.

Plot Details:

* x-axis:top_ten_trim_var

* y-axis:top_ten_trim_var.index

* Orientation: Horizontal

* Title:Small Business Owners: High Variance Features

* Axis Labels:

* x-axis:"Trimmed Variance [$]"

* y-axis:"Feature"

* Use plotly.express.bar() to create the plot and fig.update_layout() to customize axis titles ( given above ).
"""

# Create horizontal bar chart of `top_ten_trim_var`

fig = px.bar(
    x=top_ten_trim_var,
    y=top_ten_trim_var.index,
    orientation='h',
    title="Small Business Owners: High Variance Features",

)
fig.update_layout(xaxis_title="Trimmed Variance", yaxis_title="Feature")

fig.show()

"""Based on this graph, which five features have the highest variance?

**Task 6.5.11**

Using top_ten_trim_var generate a list called high_var_cols with the column names of the five features with the highest trimmed variance.
"""

high_var_cols = top_ten_trim_var.tail(5).index.to_list()
high_var_cols

"""### **Split**

Let's turn that list into a feature matrix.

**Task 6.5.12**

Define a feature matrix X from df_small_biz. It should contain the five columns in high_var_cols. Run Check Activity to verify the results.
"""

X = df_small_biz[high_var_cols]
print("X shape:", X.shape)
X.head()

"""## **Build Model**

Now that our data is in order, let's get to work on the model.

### **Iterate**

**Task 6.5.13**

Assess the performance of K-Means clustering models with different values of n_clusters, ranging from 2 to 12.

Define two empty lists—inertia_errors and silhouette_scores—to store the inertia and silhouette score for each model.

Then, use loop to:

* Build and fit a pipeline with StandardScaler() and KMeans using the current cluster count.

* Keep random_state = 42

* Append the model's inertia to inertia_errors.

* Calculate the silhouette score using the model’s labels and append it to silhouette_scores.

This analysis will help you determine the optimal number of clusters for your dataset.

**Note:** For reproducibility, make sure you set the random state for your model to 42.
"""

n_clusters = range(2, 13)
inertia_errors = []
silhouette_scores = []

# Add `for` loop to train model and calculate inertia, silhouette score.
for k in n_clusters:
    # Build model
    model = make_pipeline(StandardScaler(), KMeans(n_clusters=k, random_state=42))
    # Train model
    model.fit(X)
    # Calculate inertia
    inertia_errors.append(model.named_steps["kmeans"].inertia_)
    # Calculate silhouette score
    silhouette_scores.append(
        silhouette_score(X, model.named_steps["kmeans"].labels_)
    )

print("Inertia:", inertia_errors[:11])
print()
print("Silhouette Scores:", silhouette_scores[:3])

"""Just like we did in the previous module, we can start to figure out how many clusters we'll need with a line plot based on Inertia.

**Task 6.5.14**

Use plotly express to create a line plot that shows the values of inertia_errors as a function of n_clusters.

Plot Details:

* X-axis :Number of Clusters

* Y-axis :Inertia

* Title :K-Means Model: Inertia vs Number of Clusters

After creating the plot, use fig.update_layout() to set:

* xaxis_title=Number of Clusters

* yaxis_title=Inertia

Call fig.show() to display the plot.
"""

# Create line plot of `inertia_errors` vs `n_clusters`
fig = px.line(
    x=n_clusters, y=inertia_errors, title="K-Means Model: Inertia vs Number of Clusters"
)
fig.update_layout(xaxis_title="Number of Clusters (k)", yaxis_title="Inertia")

fig.show()

"""And let's do the same thing with our Silhouette Scores.

**Task 6.5.15**

Use plotly.express.line() to create a line plot that shows the values of silhouette_scores as a function of n_clusters.

Your plot must include:

* x=n_clusters

* y=silhouette_scores

* Title = K-Means Model: Silhouette Score vs Number of Clusters

After creating the plot, use fig.update_layout() to set:

* X - axis = Number of Clusters

* Y - axis = Silhouette Score

Call fig.show() to display the plot.
"""

# Create a line plot of `silhouette_scores` vs `n_clusters`
fig = px.line(
    x=n_clusters,
    y=silhouette_scores,
    title="K-Means Model: Silhouette Score vs Number of Clusters"
)
fig.update_layout(xaxis_title="Number of Clusters (k)", yaxis_title="Silhouette Score")
fig.show()

"""How many clusters should we use? When you've made a decision about that, it's time to build the final model.

**Task 6.5.16**

Build and train a new k-means model named final_model. Using Standard Scaler and Kmeans clustering.

* The number of clusters should be 3.

* Keep random_state=42

After building and training the model, run Check Activity to verify your results.

**Note:** For reproducibility, make sure you set the random state for your model to 42.
"""

final_model = make_pipeline(
    StandardScaler(),
    KMeans(n_clusters=3, random_state=42)

)

# Fit model to data
final_model.fit(X)

"""## **Communicate**

Excellent! Let's share our work!

**Task 6.5.17**

Access the cluster labels from your trained final_model pipeline. Then group the standardized feature set X by these labels and compute the mean of each feature for every cluster. Store the result in a DataFrame named xgb.
"""

labels = final_model.named_steps["kmeans"].labels_
xgb = X.groupby(labels).mean()
xgb

"""As usual, let's make a visualization with the DataFrame.

**Task 6.5.18**

Use plotly.express.bar() to create a side-by-side grouped bar chart that visualizes the values in the DataFrame xgb.

Your plot must include:

* The DataFrame xgb as input data

* barmode=group to display bars side-by-side

* Title=Small Business Owner Finances by Cluster

After creating the plot, use fig.update_layout() to set:

* X-axis=Cluster

* Y-axis=Value [$]

Call fig.show() to display the chart.
"""

# Create side-by-side bar chart of `xgb`
fig = px.bar(
    xgb,
    barmode="group",
    title="Small Business Owner Finances by Cluster"
)
fig.update_layout(xaxis_title="Cluster", yaxis_title="Value [$]")
fig.show()

"""Remember what we did with higher-dimension data last time? Let's do the same thing here.

**Task 6.5.19**

Create a PCA transformer to reduce the dimensionality of the dataset X to 2 components. Apply this transformer to X and store the resulting transformed data in a DataFrame named X_pca. Name the columns of X_pca as "PC1" and "PC2".

**Note :** Keep random_state to 42.
"""

# Instantiate transformer
pca = PCA(n_components=2, random_state=42)

# Transform `X`
X_t = pca.fit_transform(X)

# Put `X_t` into DataFrame
X_pca = pd.DataFrame(X_t, columns=["PC1", "PC2"])

print("X_pca shape:", X_pca.shape)
X_pca.head()

"""Finally, let's make a visualization of our final DataFrame.

**Task 6.5.20**

Use plotly.express.scatter() to create a scatter plot that visualizes the PCA-transformed data in X_pca.

Your plot must include:

* data_frame= X_pca

* x=PC1

* y=PC2

* color=labels.astype(str) to color points by cluster labels

* title=PCA Representation of Clusters

After creating the plot, use fig.update_layout() to set:

* X-axis=PC1

* Y-axis=PC2

Call fig.show() to display the scatter plot.
"""

# Create scatter plot of `PC2` vs `PC1`
fig = px.scatter(
    data_frame=X_pca,
    x="PC1",
    y="PC2",
    color=labels.astype(str),
    title="PCA representation of Clusters"
)
fig.update_layout(xaxis_title="PC1", yaxis_title="PC2")
fig.show()

"""Copyright 2023 WorldQuant University. This content is licensed solely for personal use. Redistribution or publication of this material is strictly prohibited."""
