# %%
import glob
import json
import pandas as pd
import os
import zipfile

DATA_DIR = "data"

# %% Load dataset

def load_zip_json_to_df(data_dir: str) -> pd.DataFrame:
    records = []
    zip_files = [f for f in glob.glob(os.path.join(data_dir, "*.zip"))]
    for zip_path in zip_files:
        zip_name = os.path.basename(zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                with zip_ref.open(file_name) as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        for obj in content:
                            obj["zip_file"] = zip_name
                            records.append(obj)
                    else:
                        content["zip_file"] = zip_name
                        records.append(content)
    df = pd.DataFrame(records)

    return df

df = load_zip_json_to_df(DATA_DIR)
df.head()

# %% Evaluate patterns

mask_agvs = df["zip_file"] == "agvs.zip"
mask_modules = df["zip_file"] == "modules.zip"
mask_orders = df["zip_file"] == "orders.zip"
mask_products = df["zip_file"] == "products.zip"
mask_resources = df["zip_file"] == "resources.zip"
mask_stations = df["zip_file"] == "stations.zip"

# %% 1) Number of times a machine state switches during processing of an order.
results = []
for order_id in df[mask_orders]["id"].unique():
    df_order = df[mask_orders & (df["id"] == order_id)]

    for resource_id in df_order["allocatedId"]:
        t_track_in = df_order[(df_order["allocatedId"] == resource_id) & pd.isna(df_order["finished"])]["lastUpdated"].iloc[0]
        t_track_out = df_order[(df_order["allocatedId"] == resource_id) & ~pd.isna(df_order["finished"])]["lastUpdated"].iloc[0]

        results.append({
            "Resource": resource_id,
            "ProductionEntity": order_id,
            "intervalStartTime": t_track_in,
            "intervalEndTime": t_track_out,
            "eventCount": sum((df["id"] == resource_id) & (df["lastUpdated"] > t_track_in) & (df["lastUpdated"] < t_track_out))
        })

# %% 2) List all states of a machine during processing of an order.
results = []
for order_id in df[mask_orders]["id"].unique():
    df_order = df[mask_orders & (df["id"] == order_id)]

    for resource_id in df_order["allocatedId"]:
        t_track_in = df_order[(df_order["allocatedId"] == resource_id) & pd.isna(df_order["finished"])]["lastUpdated"].iloc[0]
        t_track_out = df_order[(df_order["allocatedId"] == resource_id) & ~pd.isna(df_order["finished"])]["lastUpdated"].iloc[0]

        results.append({
            "Resource": resource_id,
            "ProductionEntity": order_id,
            "intervalStartTime": t_track_in,
            "intervalEndTime": t_track_out,
            "groupConcat": ", ".join(df[(df["id"] == resource_id) & (df["lastUpdated"] > t_track_in) & (df["lastUpdated"] < t_track_out)]["state"].unique())
        })

# %% 3) Time between processing orders on a machine.
results = []
for resource_id in df[mask_resources]["id"].unique():
    df_resource_allocated = df[df["allocatedId"] == resource_id]
    for track_in_id in df_resource_allocated[pd.isna(df_resource_allocated["finished"])]["id"].unique()[:10]:
        t_track_in = df_resource_allocated[(df_resource_allocated["id"] == track_in_id)]["lastUpdated"].iloc[0]
        t_prec_track_out = df_resource_allocated[~pd.isna(df_resource_allocated["finished"]) & (df_resource_allocated["lastUpdated"] < t_track_in)]["lastUpdated"].max()

        results.append({
            "Resource": resource_id,
            "Event": track_in_id,
            "elapsedTime": t_track_in - t_prec_track_out,
        })

# %% 4.1) Time a machine is in a state.
results = []
for resource_id in df[mask_resources]["id"].unique():
    df_resource_sorted = df[df["id"] == resource_id][["id", "lastUpdated", "state"]].sort_values("lastUpdated").copy()
    df_resource_sorted["elapsedTime"] = df_resource_sorted["lastUpdated"].shift(-1) - df_resource_sorted["lastUpdated"]

    df_resource_sorted.columns = ["Resource", "Event", "value", "elapsedTime"]
    results = df_resource_sorted.to_dict(orient="records")

# %% 4.2) Time between observing products at a Work Station.
results = []
for station_id in df[mask_stations]["id"].unique():
    df_at_station_sorted = df[df["locationEntityId"] == station_id][["locationEntityId", "lastUpdated", "id"]].sort_values("lastUpdated").copy()
    df_at_station_sorted["elapsedTime"] = df_at_station_sorted["lastUpdated"].shift(-1) - df_at_station_sorted["lastUpdated"]

    df_at_station_sorted.columns = ["Resource", "Event", "value", "elapsedTime"]
    results = df_at_station_sorted.to_dict(orient="records")

# %% 5) Throughput time per product.
results = []
for product_id in df[mask_products]["id"].unique():
    df_product = df[df["productId"] == product_id]
    t_track_in_min = df_product[pd.isna(df_product["finished"])]["lastUpdated"].min()
    t_track_out_max = df_product[~pd.isna(df_product["finished"])]["lastUpdated"].max()
    results.append({
        "Entity": product_id,
        "elapsedTime": t_track_out_max - t_track_in_min,
    })

# %% 6) Relate AGV switch state 'free' event to the product that the AGV was transporting.
results = []
for agv_id in df[mask_agvs]["id"].unique()[:1]:
    df_agv = df[(df["id"] == agv_id)]
    for t_free in df_agv[df_agv["state"]=="free"]["lastUpdated"].unique():
        t_transporting = df_agv[(df_agv["state"]=="transporting_unit") & (df_agv["lastUpdated"]<t_free)]["lastUpdated"].max()
        if not pd.isna(t_transporting):
            content_ids = df_agv[(df_agv["lastUpdated"] == t_transporting)]["contentIds"].iloc[0]

            results.append({
                "Event": t_free,
                "EntityLatest": content_ids[0],
            })

# %% 7) Relate machine level track in events to the work station.
# Relation resource (machine) and station
resource_station = {}
for record in df[mask_stations].to_dict(orient="records"):
    for child in record["children"]:
        resource_station[child["id"]] = record["id"]

results = []
for resource_id in df[mask_resources]["id"].unique():
    station_id = resource_station.get(resource_id)
    if station_id:
        for t_track_in in df[(df["allocatedId"] == resource_id) & (pd.isna(df["finished"]))]["lastUpdated"].unique():
            results.append({
                "Event": t_track_in,
                "Entity": station_id,
                "PartEntity": resource_id,
            })

# %% 8) Relate events related to the modules (components) to the product that is composed of those modules.
join_resources = [
    "fbefdec2f0015c2c45d7356f", # F1_J1
    "9e198cf8cd73b25b153ce27d", # F1_J2
    "7454c32cca8e5c7e6c9d086e", # R1_J1
    "8f9e8c99cb96805cbecec2c6", # R1_J2
]

# Relation product and module
product_module = {}
for product_id, product_description in set((i, d) for i, d in df[mask_products][["id", "productDescriptor"]].values):
    product_module[product_id] = df[mask_modules & df["description"].str.startswith(product_description)]["id"].unique()

results = []
for order_id in df[mask_orders & df["allocatedId"].isin(join_resources)]["id"].unique():
    df_order_track_out = df[(df["id"] == order_id) & (pd.isna(df["finished"]))]
    t_join_track_out = df_order_track_out["lastUpdated"].iloc[0]
    product_id = df_order_track_out["productId"].iloc[0]

    module_ids = product_module.get(product_id, [])
    for t_event in df[mask_orders & df["productId"].isin(module_ids) & (df["lastUpdated"] < t_join_track_out)]["lastUpdated"].values:
        results.append({
            "Event": t_event,
            "RelatedProductionEntity": product_id,
        })

# %% 10) Relate orders to the product they are part of.
results = []
for product_id in df[mask_orders]["productId"].unique()[:1]:
    df_product = df[mask_orders & (df["productId"] == product_id)]

    for resource_id in df_product["allocatedId"].unique():
        df_allocated_resource = df_product[df_product["allocatedId"] == resource_id]
        for t_track_in in df_allocated_resource[pd.isna(df_allocated_resource["finished"])]["lastUpdated"].unique():
            t_track_out = df_allocated_resource[~pd.isna(df_allocated_resource["finished"]) & (df_allocated_resource["lastUpdated"]>t_track_in)]["lastUpdated"].min()

            for order_id in df[(df["allocatedId"] == resource_id) & (df["lastUpdated"]>=t_track_in) & (df["lastUpdated"]<=t_track_out)]["description"].unique():
                results.append({
                    "PartEntity": order_id,
                    "ProductionEntity": product_id,
                })
