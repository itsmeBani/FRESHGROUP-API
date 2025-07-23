import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from supabase import create_client, Client


scaler = StandardScaler()



def clustered_data_visualization(data):
    df = pd.DataFrame(data)
    X = df[["Grade12GWA", "FamilyIncome"]]

    scaled_df = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3,n_init=10, random_state=42)
    kmeans.fit(scaled_df)
    df['cluster'] = kmeans.labels_
    print(df)
    return df

def elbow_method(df):
    X = df[["Grade12GWA", "FamilyIncome"]]

    scaled_df = scaler.fit_transform(X)
    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "random_state": 1,
    }
    sse = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(scaled_df)
        sse.append(kmeans.inertia_)
    return sse

def barchart_visualization(low, average, high):
    categories = ["Low Income", "Average Income", "High Income"]
    values = [low, average, high]
    colors = ["#4E79A7", "#F28E2B", "#59A14F"]
    plt.figure()
    plt.bar(categories, values, color=colors)
    plt.ylabel("Number of Student")
    plt.title("Family Income Category")
    plt.show()

def clustered_family_income(data):
    df = pd.DataFrame(data)

    X = df[["Grade12GWA", "FamilyIncome"]]
    scaled_df = scaler.fit_transform(X)
    scaled_income = scaler.fit_transform(df[["FamilyIncome"]])
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    df["cluster"] = kmeans.fit_predict(scaled_income)
    centroids = kmeans.cluster_centers_.flatten()
    ordered = np.argsort(centroids)
    label_map = {ordered[0]: "low", ordered[1]: "average", ordered[2]: "high"}
    df["income_cluster"] = df["cluster"].map(label_map)
    return {
        "low": len(df[df.income_cluster == "low"]),
        "average": len(df[df.income_cluster == "average"]),
        "high": len(df[df.income_cluster == "high"])
    }




def common_program_enrolled(data):
    # Step 1: Create DataFrame
    df = pd.DataFrame(data)

    # Step 2: Encode ProgramEnrolled
    label_encoder = LabelEncoder()
    df['common_program'] = label_encoder.fit_transform(df['ProgramEnrolled'])

    # Step 3: Group by ProgramEnrolled and count occurrences
    program_counts = df.groupby('ProgramEnrolled').size().reset_index(name='count')

    # Convert to list of dictionaries
    result = program_counts.to_dict(orient="records")

    return result



def cluster_student_profile(data):
    if not data:
        return []

    df = pd.DataFrame(data)
    features = ["TypeofSeniorHighSchool", "ProgramEnrolled", "MunicipalityOfOrigin", "Sex", "Grade12GWA", "FamilyIncome"]
    X = df[features].copy()

    # One-hot encode categorical variables
    X = pd.get_dummies(X, columns=["TypeofSeniorHighSchool", "ProgramEnrolled", "MunicipalityOfOrigin", "Sex"])

    # Scale numerical features
    scaler = StandardScaler()
    X[["Grade12GWA", "FamilyIncome"]] = scaler.fit_transform(X[["Grade12GWA", "FamilyIncome"]])

    # Apply KMeans
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    df["Cluster"] = kmeans.fit_predict(X)

    # Build cluster output
    output = {}
    for cluster_num in sorted(df["Cluster"].unique()):
        cluster_df = df[df["Cluster"] == cluster_num]

        # Most common values
        def most_common(col):
            return cluster_df[col].mode().iloc[0]

        common_characteristics = {
            "Municipality": most_common("MunicipalityOfOrigin"),
            "Senior High School Type": most_common("TypeofSeniorHighSchool"),
            "Program": most_common("ProgramEnrolled"),
            "Sex": most_common("Sex"),
            "Family Income": "₱30,000 and above" if cluster_df["FamilyIncome"].mean() >= 0 else "Below ₱30,000",
            "Grade 12 GWA": f"{round(cluster_df['Grade12GWA'].mean(), 2)}"
        }

        # Students without cluster column
        student_list = cluster_df.drop(columns=["Cluster"]).to_dict(orient="records")

        output[f"{cluster_num}"] = {
            "common": common_characteristics,
            "students": student_list
        }

    return output

